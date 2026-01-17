# 现有数据使用和增量数据处理指南

> **项目**: ManiDala POD Platform - TFRS Data Usage  
> **版本**: 1.0  
> **日期**: 2026-01-17  
> **目标**: 充分利用现有数据，建立增量数据处理机制

---

## 📋 目录

1. [现有数据分析](#现有数据分析)
2. [现有数据提取方案](#现有数据提取方案)
3. [增量数据处理](#增量数据处理)
4. [数据合并策略](#数据合并策略)
5. [实施步骤](#实施步骤)

---

## 1. 现有数据分析

### 1.1 可用数据源清单

根据数据库 Schema，我们有以下可用数据：

| 数据表 | 数据量估算 | 可用性 | 训练价值 |
|--------|-----------|--------|----------|
| **orders** | 100-500条 | ⭐⭐⭐⭐⭐ | 高（购买行为） |
| **base_products** | 2000-5000个 | ⭐⭐⭐⭐⭐ | 高（商品特征） |
| **end_products** | 500-2000个 | ⭐⭐⭐⭐ | 中（设计师关联） |
| **images** | 5000-10000个 | ⭐⭐⭐ | 中（浏览行为） |
| **accounts** | 500-1000个 | ⭐⭐⭐⭐ | 高（用户特征） |

### 1.2 数据质量评估

```sql
-- 检查现有数据量
SELECT 
  'orders' as table_name, COUNT(*) as count FROM orders
UNION ALL
SELECT 'base_products', COUNT(*) FROM base_products
UNION ALL
SELECT 'end_products', COUNT(*) FROM end_products
UNION ALL
SELECT 'images', COUNT(*) FROM images
UNION ALL
SELECT 'accounts', COUNT(*) FROM accounts;
```

---

## 2. 现有数据提取方案

### 2.1 从订单数据提取交互

订单是最有价值的数据源，因为它代表真实的购买行为。

#### A. 提取购买交互

```sql
-- 从订单中提取用户-商品交互
SELECT 
  o.email as user_id,
  json_extract(item.value, '$.product_id') as item_id,
  5.0 as rating,  -- 购买行为赋予最高权重
  strftime('%s', o.created_at) as timestamp,
  'purchase' as interaction_type,
  json_extract(item.value, '$.quantity') as quantity,
  json_extract(item.value, '$.price') as price
FROM orders o,
  json_each(o.line_items) as item
WHERE o.financial_status = 'paid'
  AND o.created_at IS NOT NULL
ORDER BY o.created_at;
```

#### B. 生成模拟浏览行为

基于购买记录，我们可以合理推断用户浏览了相关商品：

```sql
-- 为每个购买生成浏览行为（购买前必然浏览）
SELECT 
  o.email as user_id,
  json_extract(item.value, '$.product_id') as item_id,
  3.0 as rating,  -- 浏览行为权重较低
  strftime('%s', datetime(o.created_at, '-' || (RANDOM() % 3600 + 60) || ' seconds')) as timestamp,
  'view' as interaction_type
FROM orders o,
  json_each(o.line_items) as item
WHERE o.financial_status = 'paid';
```

#### C. 生成相似商品浏览

用户购买某商品时，可能浏览了同类商品：

```sql
-- 为每个购买生成同类商品浏览
SELECT 
  o.email as user_id,
  bp.id as item_id,
  2.0 as rating,
  strftime('%s', datetime(o.created_at, '-' || (RANDOM() % 7200 + 300) || ' seconds')) as timestamp,
  'view' as interaction_type
FROM orders o,
  json_each(o.line_items) as purchased_item,
  base_products bp
WHERE o.financial_status = 'paid'
  AND bp.category_id = (
    SELECT category_id 
    FROM base_products 
    WHERE id = json_extract(purchased_item.value, '$.product_id')
  )
  AND bp.id != json_extract(purchased_item.value, '$.product_id')
  AND RANDOM() % 100 < 30  -- 30% 概率生成
LIMIT 3;  -- 每个购买最多3个相似商品
```

### 2.2 从图片浏览数据提取交互

```sql
-- 从图片浏览记录提取交互
SELECT 
  'anonymous_' || CAST(RANDOM() AS TEXT) as user_id,  -- 匿名用户
  entity_id as item_id,
  1.0 as rating,  -- 图片浏览权重最低
  strftime('%s', created_at) as timestamp,
  'image_view' as interaction_type,
  view_count
FROM images
WHERE type = 'design'
  AND entity_id IS NOT NULL
  AND view_count > 0;
```

### 2.3 完整数据提取脚本

创建一个 Worker 来提取和转换现有数据：

```javascript
// workers/manidala-data-extract/src/index.js
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    if (url.pathname === '/extract/existing-data') {
      return await extractExistingData(env);
    }
    
    return new Response('Not found', { status: 404 });
  }
};

async function extractExistingData(env) {
  const interactions = [];
  
  // 1. 提取购买交互
  const purchases = await env.DB.prepare(`
    SELECT 
      o.email as user_id,
      json_extract(item.value, '$.product_id') as item_id,
      5.0 as rating,
      strftime('%s', o.created_at) as timestamp,
      'purchase' as interaction_type
    FROM orders o,
      json_each(o.line_items) as item
    WHERE o.financial_status = 'paid'
      AND o.created_at IS NOT NULL
  `).all();
  
  interactions.push(...purchases.results);
  
  // 2. 生成浏览行为（购买前）
  const views = await env.DB.prepare(`
    SELECT 
      o.email as user_id,
      json_extract(item.value, '$.product_id') as item_id,
      3.0 as rating,
      strftime('%s', datetime(o.created_at, '-' || (ABS(RANDOM()) % 3600 + 60) || ' seconds')) as timestamp,
      'view' as interaction_type
    FROM orders o,
      json_each(o.line_items) as item
    WHERE o.financial_status = 'paid'
  `).all();
  
  interactions.push(...views.results);
  
  // 3. 插入到训练交互表
  const stmt = env.DB.prepare(`
    INSERT INTO training_interactions (
      user_id, item_id, rating, timestamp, interaction_type, source
    ) VALUES (?, ?, ?, ?, ?, 'existing_data')
  `);
  
  const batch = interactions.map(i => 
    stmt.bind(i.user_id, i.item_id, i.rating, i.timestamp, i.interaction_type)
  );
  
  await env.DB.batch(batch);
  
  // 4. 导出为 CSV
  const csv = convertToCSV(interactions);
  
  // 5. 上传到 R2
  await env.R2_BUCKET.put(
    `training-data/existing-data-${Date.now()}.csv`,
    csv,
    {
      httpMetadata: {
        contentType: 'text/csv'
      }
    }
  );
  
  return new Response(JSON.stringify({
    success: true,
    total_interactions: interactions.length,
    breakdown: {
      purchases: purchases.results.length,
      views: views.results.length
    }
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}

function convertToCSV(data) {
  const headers = ['user_id', 'item_id', 'rating', 'timestamp', 'interaction_type'];
  const rows = data.map(row => 
    headers.map(h => row[h]).join(',')
  );
  return [headers.join(','), ...rows].join('\n');
}
```

---

## 3. 增量数据处理

### 3.1 增量数据收集策略

采用**双轨制**：现有数据 + 实时增量数据

```
┌─────────────────────────────────────────────┐
│           数据收集双轨制                     │
├─────────────────────────────────────────────┤
│                                             │
│  轨道 1: 现有数据（一次性）                  │
│  ├─ 订单数据提取                            │
│  ├─ 图片浏览提取                            │
│  └─ 生成模拟行为                            │
│                                             │
│  轨道 2: 增量数据（持续）                    │
│  ├─ 前端埋点收集                            │
│  ├─ API 日志收集                            │
│  └─ 推荐反馈收集                            │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.2 增量数据自动同步

#### A. 订单增量同步

```javascript
// 监听 Shoplazza Webhook - 新订单
export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }
    
    const webhook = await request.json();
    
    if (webhook.topic === 'orders/paid') {
      await processNewOrder(webhook.data, env);
    }
    
    return new Response('OK');
  }
};

async function processNewOrder(order, env) {
  // 1. 保存订单到数据库
  await env.DB.prepare(`
    INSERT INTO orders (shoplazza_id, email, line_items, created_at, ...)
    VALUES (?, ?, ?, ?, ...)
  `).bind(order.id, order.email, JSON.stringify(order.line_items), ...).run();
  
  // 2. 立即生成训练交互
  const interactions = [];
  
  for (const item of order.line_items) {
    // 购买交互
    interactions.push({
      user_id: order.email,
      item_id: item.product_id,
      rating: 5.0,
      timestamp: Math.floor(Date.now() / 1000),
      interaction_type: 'purchase'
    });
    
    // 模拟浏览交互（购买前5-60分钟）
    interactions.push({
      user_id: order.email,
      item_id: item.product_id,
      rating: 3.0,
      timestamp: Math.floor(Date.now() / 1000) - (Math.random() * 3300 + 300),
      interaction_type: 'view'
    });
  }
  
  // 3. 插入训练交互表
  const stmt = env.DB.prepare(`
    INSERT INTO training_interactions (
      user_id, item_id, rating, timestamp, interaction_type, source
    ) VALUES (?, ?, ?, ?, ?, 'webhook')
  `);
  
  const batch = interactions.map(i => 
    stmt.bind(i.user_id, i.item_id, i.rating, i.timestamp, i.interaction_type)
  );
  
  await env.DB.batch(batch);
  
  // 4. 触发增量训练（如果累积足够数据）
  await checkAndTriggerIncrementalTraining(env);
}
```

#### B. 前端行为增量同步

前端 SDK 实时收集的数据会自动进入 `user_behaviors` 表，定期转换为训练数据：

```javascript
// Scheduled Worker - 每小时执行
export default {
  async scheduled(event, env) {
    // 1. 查询最近1小时的新行为
    const lastSync = await env.KV.get('last_sync_timestamp') || 
                     Math.floor(Date.now() / 1000) - 3600;
    
    const newBehaviors = await env.DB.prepare(`
      SELECT 
        COALESCE(user_id, session_id) as user_id,
        product_id as item_id,
        CASE event_type
          WHEN 'purchase' THEN 5.0
          WHEN 'add_to_cart' THEN 4.0
          WHEN 'add_to_wishlist' THEN 3.0
          WHEN 'product_click' THEN 2.0
          WHEN 'product_view' THEN 1.0
          ELSE 0.5
        END as rating,
        strftime('%s', timestamp) as timestamp,
        event_type as interaction_type
      FROM user_behaviors
      WHERE strftime('%s', timestamp) > ?
        AND product_id IS NOT NULL
      ORDER BY timestamp
    `).bind(lastSync).all();
    
    if (newBehaviors.results.length === 0) {
      console.log('No new behaviors to sync');
      return;
    }
    
    // 2. 插入训练交互表
    const stmt = env.DB.prepare(`
      INSERT INTO training_interactions (
        user_id, item_id, rating, timestamp, interaction_type, source
      ) VALUES (?, ?, ?, ?, ?, 'realtime')
    `);
    
    const batch = newBehaviors.results.map(b => 
      stmt.bind(b.user_id, b.item_id, b.rating, b.timestamp, b.interaction_type)
    );
    
    await env.DB.batch(batch);
    
    // 3. 更新同步时间戳
    await env.KV.put('last_sync_timestamp', 
                     Math.floor(Date.now() / 1000).toString());
    
    console.log(`Synced ${newBehaviors.results.length} new behaviors`);
    
    // 4. 检查是否需要增量训练
    await checkAndTriggerIncrementalTraining(env);
  }
};
```

### 3.3 增量训练触发机制

```javascript
async function checkAndTriggerIncrementalTraining(env) {
  // 1. 检查自上次训练以来的新数据量
  const lastTraining = await env.KV.get('last_training_timestamp') || 0;
  
  const newDataCount = await env.DB.prepare(`
    SELECT COUNT(*) as count
    FROM training_interactions
    WHERE created_at > datetime(?, 'unixepoch')
  `).bind(lastTraining).first();
  
  // 2. 判断是否需要重训练
  const RETRAIN_THRESHOLD = 10000;  // 累积1万条新数据
  const RETRAIN_INTERVAL = 7 * 24 * 3600;  // 或7天
  
  const shouldRetrain = 
    newDataCount.count >= RETRAIN_THRESHOLD ||
    (Date.now() / 1000 - lastTraining) >= RETRAIN_INTERVAL;
  
  if (shouldRetrain) {
    // 3. 导出增量数据
    await exportIncrementalData(env, lastTraining);
    
    // 4. 触发训练通知（可以是邮件、Slack等）
    await notifyRetraining(env, {
      new_data_count: newDataCount.count,
      last_training: new Date(lastTraining * 1000).toISOString()
    });
    
    // 5. 更新训练时间戳
    await env.KV.put('last_training_timestamp', 
                     Math.floor(Date.now() / 1000).toString());
  }
}

async function exportIncrementalData(env, since) {
  const data = await env.DB.prepare(`
    SELECT user_id, item_id, rating, timestamp, interaction_type
    FROM training_interactions
    WHERE created_at > datetime(?, 'unixepoch')
    ORDER BY timestamp
  `).bind(since).all();
  
  const csv = convertToCSV(data.results);
  
  await env.R2_BUCKET.put(
    `training-data/incremental-${Date.now()}.csv`,
    csv,
    {
      httpMetadata: {
        contentType: 'text/csv'
      },
      customMetadata: {
        type: 'incremental',
        since: since.toString(),
        count: data.results.length.toString()
      }
    }
  );
}
```

---

## 4. 数据合并策略

### 4.1 训练数据合并方案

#### 方案 A: 全量重训练（推荐）

```python
# 在 Colab 中合并所有数据
import pandas as pd
from google.colab import drive

# 1. 挂载 Google Drive
drive.mount('/content/drive')

# 2. 读取所有数据文件
existing_data = pd.read_csv('/content/drive/MyDrive/tfrs-data/existing-data.csv')
incremental_data = pd.read_csv('/content/drive/MyDrive/tfrs-data/incremental-*.csv')

# 3. 合并数据
all_data = pd.concat([existing_data, incremental_data], ignore_index=True)

# 4. 去重（同一用户-商品-时间窗口）
all_data['time_window'] = pd.to_datetime(all_data['timestamp'], unit='s').dt.floor('5min')
all_data = all_data.drop_duplicates(
    subset=['user_id', 'item_id', 'time_window'],
    keep='last'
)

# 5. 按时间排序
all_data = all_data.sort_values('timestamp')

# 6. 划分训练/测试集（80/20）
split_idx = int(len(all_data) * 0.8)
train_data = all_data[:split_idx]
test_data = all_data[split_idx:]

print(f"Total: {len(all_data)}, Train: {len(train_data)}, Test: {len(test_data)}")
```

#### 方案 B: 增量训练（高级）

```python
# 加载已有模型，使用新数据继续训练
import tensorflow as tf
import tensorflow_recommenders as tfrs

# 1. 加载已有模型
model = tf.keras.models.load_model('/content/drive/MyDrive/tfrs-models/model-v1')

# 2. 准备增量数据
incremental_dataset = tf.data.Dataset.from_tensor_slices({
    'user_id': incremental_data['user_id'].values,
    'item_id': incremental_data['item_id'].values,
    'rating': incremental_data['rating'].values
})

# 3. 继续训练（较少的 epochs）
model.fit(
    incremental_dataset.batch(256),
    epochs=5,  # 增量训练用较少 epochs
    verbose=1
)

# 4. 保存新版本模型
model.save('/content/drive/MyDrive/tfrs-models/model-v2')
```

### 4.2 数据版本管理

```javascript
// 在 R2 中管理数据版本
const DATA_VERSIONS = {
  'v1.0': {
    files: ['existing-data-20260117.csv'],
    total_interactions: 5000,
    date: '2026-01-17'
  },
  'v1.1': {
    files: ['existing-data-20260117.csv', 'incremental-20260124.csv'],
    total_interactions: 15000,
    date: '2026-01-24'
  },
  'v2.0': {
    files: ['merged-data-20260201.csv'],
    total_interactions: 50000,
    date: '2026-02-01'
  }
};

// 保存版本信息到 KV
await env.KV.put('data_versions', JSON.stringify(DATA_VERSIONS));
```

---

## 5. 实施步骤

### 5.1 第一步：提取现有数据（立即执行）

```bash
# 1. 部署数据提取 Worker
cd workers/manidala-data-extract
wrangler deploy

# 2. 触发数据提取
curl -X POST https://data-extract.your-domain.workers.dev/extract/existing-data

# 3. 下载生成的 CSV
# 从 R2 下载: training-data/existing-data-*.csv
```

### 5.2 第二步：使用现有数据训练初始模型（1-2天）

```python
# 在 Colab 中
# 1. 上传 existing-data.csv 到 Google Drive
# 2. 运行训练笔记本
# 3. 下载训练好的模型
```

### 5.3 第三步：部署增量数据收集（1周）

```bash
# 1. 部署前端 Tracking SDK
# 2. 部署 Tracking Worker
# 3. 配置 Scheduled Worker（每小时同步）
# 4. 配置 Webhook（订单实时同步）
```

### 5.4 第四步：建立增量训练流程（持续）

```
每周流程：
1. 周一：检查累积数据量
2. 周二：如果 > 1万条，导出增量数据
3. 周三：在 Colab 重训练模型
4. 周四：部署新模型到 Railway
5. 周五：A/B 测试新旧模型
```

---

## 6. 数据量预估

### 6.1 现有数据预估

| 数据源 | 预估量 | 训练交互数 |
|--------|--------|-----------|
| 订单（购买） | 100-500 | 100-500 |
| 订单（模拟浏览） | 100-500 | 100-500 |
| 订单（相似商品） | 300-1500 | 300-1500 |
| 图片浏览 | 5000-10000 | 5000-10000 |
| **总计** | | **5500-12500** |

### 6.2 增量数据预估

假设日活 100 用户，每用户 10 次交互：

| 时间 | 日增量 | 累积量 | 是否重训练 |
|------|--------|--------|-----------|
| 第1周 | 1000 | 6500-13500 | ❌ |
| 第2周 | 1000 | 13500-20500 | ✅ |
| 第4周 | 1000 | 27500-34500 | ✅ |
| 第8周 | 1000 | 55500-62500 | ✅ |

---

## 7. 监控和优化

### 7.1 数据质量监控

```javascript
// 每日数据质量报告
export default {
  async scheduled(event, env) {
    const report = {
      date: new Date().toISOString().split('T')[0],
      existing_data: {},
      incremental_data: {},
      total: {}
    };
    
    // 现有数据统计
    const existing = await env.DB.prepare(`
      SELECT 
        COUNT(*) as count,
        COUNT(DISTINCT user_id) as users,
        COUNT(DISTINCT item_id) as items
      FROM training_interactions
      WHERE source = 'existing_data'
    `).first();
    
    report.existing_data = existing;
    
    // 增量数据统计
    const incremental = await env.DB.prepare(`
      SELECT 
        COUNT(*) as count,
        COUNT(DISTINCT user_id) as users,
        COUNT(DISTINCT item_id) as items
      FROM training_interactions
      WHERE source IN ('webhook', 'realtime')
    `).first();
    
    report.incremental_data = incremental;
    
    // 总计
    report.total = {
      count: existing.count + incremental.count,
      users: existing.users + incremental.users,
      items: existing.items + incremental.items
    };
    
    // 保存报告
    await env.R2_BUCKET.put(
      `reports/data-quality-${report.date}.json`,
      JSON.stringify(report, null, 2)
    );
    
    console.log('Data quality report:', report);
  }
};
```

### 7.2 性能优化建议

1. **批量处理**：每小时批量同步，而非实时
2. **数据压缩**：使用 Parquet 格式存储大数据
3. **增量导出**：只导出新增数据，减少传输
4. **定期清理**：删除1年以上的旧数据

---

## 8. 常见问题

### Q1: 现有数据太少怎么办？

**A**: 采用混合策略：
- 使用公开数据集（MovieLens）预训练
- 用现有数据微调（Fine-tuning）
- 生成合理的模拟数据补充

### Q2: 如何处理匿名用户？

**A**: 使用 session_id 或 device_id 作为临时用户ID：
```sql
SELECT COALESCE(user_id, session_id, device_id) as user_id
```

### Q3: 增量数据何时触发重训练？

**A**: 三个条件之一满足即可：
- 新数据量 > 10000 条
- 距上次训练 > 7 天
- 模型性能下降 > 10%

### Q4: 如何避免数据重复？

**A**: 使用唯一约束和去重逻辑：
```sql
CREATE UNIQUE INDEX idx_unique_interaction 
ON training_interactions(user_id, item_id, timestamp);
```

---

## 9. 总结

### 核心要点

1. **现有数据**：立即提取订单和浏览数据，可获得 5000-12000 条交互
2. **增量数据**：通过前端埋点和 Webhook 持续收集
3. **数据合并**：定期（每周）合并全量数据重训练
4. **版本管理**：使用 R2 + KV 管理数据和模型版本

### 下一步行动

1. ✅ **今天**：运行数据提取脚本，获取现有数据
2. ✅ **明天**：使用现有数据训练第一个模型
3. ✅ **本周**：部署增量数据收集系统
4. ✅ **下周**：建立自动化训练流程

---

**文档版本**: 1.0  
**创建日期**: 2026-01-17  
**维护者**: ManiDala Team  
**状态**: ✅ 可执行
