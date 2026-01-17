# TFRS 训练数据收集方案

> **项目**: ManiDala POD Platform - TFRS Training Data Collection  
> **版本**: 1.0  
> **日期**: 2026-01-17  
> **目标**: 建立完整的训练数据收集、处理和管理体系

---

## 📋 目录

1. [方案概述](#方案概述)
2. [数据源分析](#数据源分析)
3. [数据收集架构](#数据收集架构)
4. [数据格式规范](#数据格式规范)
5. [技术实现](#技术实现)
6. [数据质量保证](#数据质量保证)
7. [隐私与合规](#隐私与合规)
8. [实施路线图](#实施路线图)

---

## 1. 方案概述

### 1.1 目标

建立一套完整的数据收集体系，为 TFRS 推荐模型提供高质量的训练数据：

- ✅ **真实性**: 收集真实用户行为数据
- ✅ **完整性**: 覆盖所有关键交互类型
- ✅ **时效性**: 实时/准实时数据收集
- ✅ **可扩展**: 支持数据量持续增长
- ✅ **合规性**: 符合 GDPR/CCPA 等隐私法规

### 1.2 数据收集策略

采用**三阶段**数据收集策略：

```
阶段 1: 公开数据集训练（立即开始）
  ↓
阶段 2: 模拟数据 + 少量真实数据（1-2周）
  ↓
阶段 3: 完整真实数据收集（持续）
```

### 1.3 预期数据量

| 阶段 | 时间 | 用户数 | 商品数 | 交互数 | 数据质量 |
|------|------|--------|--------|--------|----------|
| 阶段 1 | 立即 | 1000 | 5000 | 10万 | 公开数据集 |
| 阶段 2 | 2周 | 500 | 2000 | 5万 | 模拟+真实 |
| 阶段 3 | 1月 | 2000+ | 5000+ | 20万+ | 真实数据 |
| 阶段 4 | 3月 | 10000+ | 10000+ | 100万+ | 生产级 |

---

## 2. 数据源分析

### 2.1 现有数据源（ManiDala 平台）

#### A. 数据库表（Cloudflare D1）

**1. accounts（用户数据）**
```sql
-- 可用字段
id, email, username, role, created_at, updated_at
external_id, synced_at

-- 数据量估算: 500-1000 用户
```

**2. base_products（基础产品）**
```sql
-- 可用字段
id, sds_id, name, english_name, sku, img_url
category_id, cost_price, recommended_price
description, categories, images

-- 数据量估算: 2000-5000 产品
```

**3. end_products（成品）**
```sql
-- 可用字段
id, shoplazza_id, title, body_html, tags
price, compare_at_price, variants
base_product_id, designer_id, status

-- 数据量估算: 500-2000 成品
```

**4. orders（订单数据）**
```sql
-- 可用字段
id, shoplazza_id, order_number, email
total_price, line_items, created_at
financial_status, fulfillment_status

-- 数据量估算: 100-500 订单
```

**5. images（图片资源）**
```sql
-- 可用字段
id, type, entity_id, url, ai_tags
view_count, download_count, artist_id

-- 数据量估算: 5000-10000 图片
```

#### B. 前端行为数据（需要新增）

**当前状态**: ❌ 未实现  
**需要收集**:
- 页面浏览（PV）
- 产品点击
- 搜索查询
- 加购行为
- 收藏行为
- 停留时长
- 滚动深度

#### C. Shoplazza 数据（通过 API 同步）

**可用数据**:
- 订单详情
- 产品浏览统计
- 购物车数据
- 客户行为

**同步频率**: 每小时/每天

#### D. SDS 数据（通过 API 同步）

**可用数据**:
- 产品详情
- 库存信息
- 价格变动
- 分类信息

**同步频率**: 每天

---

### 2.2 需要新增的数据收集点

#### A. 前端埋点（优先级：⭐⭐⭐⭐⭐）

```javascript
// 需要追踪的事件
const TRACKING_EVENTS = {
  // 页面事件
  PAGE_VIEW: 'page_view',
  PAGE_LEAVE: 'page_leave',
  
  // 产品事件
  PRODUCT_VIEW: 'product_view',
  PRODUCT_CLICK: 'product_click',
  PRODUCT_IMPRESSION: 'product_impression',
  
  // 交互事件
  ADD_TO_CART: 'add_to_cart',
  REMOVE_FROM_CART: 'remove_from_cart',
  ADD_TO_WISHLIST: 'add_to_wishlist',
  
  // 搜索事件
  SEARCH: 'search',
  SEARCH_RESULT_CLICK: 'search_result_click',
  
  // 推荐事件
  RECOMMENDATION_VIEW: 'recommendation_view',
  RECOMMENDATION_CLICK: 'recommendation_click',
  
  // 购买事件
  CHECKOUT_START: 'checkout_start',
  PURCHASE: 'purchase'
};
```

#### B. 服务端日志（优先级：⭐⭐⭐⭐）

```javascript
// API 访问日志
{
  timestamp: '2026-01-17T14:30:00Z',
  user_id: 'user_123',
  session_id: 'session_456',
  endpoint: '/api/v2/products/789',
  method: 'GET',
  response_time: 45,
  status: 200
}
```

#### C. 推荐反馈（优先级：⭐⭐⭐⭐⭐）

```javascript
// 推荐展示和点击
{
  timestamp: '2026-01-17T14:30:00Z',
  user_id: 'user_123',
  recommendation_id: 'rec_789',
  recommended_items: ['item_1', 'item_2', 'item_3'],
  clicked_item: 'item_2',
  position: 2,
  context: 'homepage_new_arrivals'
}
```

---

## 3. 数据收集架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        数据源层                              │
├─────────────────────────────────────────────────────────────┤
│  前端埋点  │  API日志  │  数据库  │  Shoplazza  │  SDS      │
└─────┬───────────┬─────────┬─────────┬────────────┬──────────┘
      │           │         │         │            │
      ▼           ▼         ▼         ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据收集层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 前端SDK  │  │ Worker   │  │ D1 Query │  │ API Sync │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────┬───────────┬─────────┬─────────┬────────────┬──────────┘
      │           │         │         │            │
      ▼           ▼         ▼         ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据处理层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 清洗     │  │ 去重     │  │ 转换     │  │ 聚合     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────┬───────────┬─────────┬─────────┬────────────┬──────────┘
      │           │         │         │            │
      ▼           ▼         ▼         ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ D1 数据库│  │ R2 存储  │  │ KV 缓存  │  │ CSV导出  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────┬───────────┬─────────┬─────────┬────────────┬──────────┘
      │           │         │         │            │
      ▼           ▼         ▼         ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据导出层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ CSV      │  │ Parquet  │  │ TFRecord │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────┬───────────┬─────────┬──────────────────────────────────┘
      │           │         │
      ▼           ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                    TFRS 训练（Colab）                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 技术选型

| 层级 | 技术方案 | 说明 |
|------|----------|------|
| 前端埋点 | 自定义 JS SDK | 轻量级，无第三方依赖 |
| 数据收集 | Cloudflare Workers | 边缘计算，低延迟 |
| 数据存储 | D1 + R2 | D1存结构化，R2存文件 |
| 数据处理 | Workers + Durable Objects | 实时处理 |
| 数据导出 | Scheduled Workers | 定时导出 |
| 训练平台 | Google Colab | GPU 加速 |

---

## 4. 数据格式规范

### 4.1 核心数据表

#### A. user_behaviors（用户行为表）

```sql
CREATE TABLE user_behaviors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  
  -- 用户标识
  user_id TEXT,                    -- 用户ID（登录用户）
  session_id TEXT NOT NULL,        -- 会话ID（匿名用户）
  device_id TEXT,                  -- 设备指纹
  
  -- 行为信息
  event_type TEXT NOT NULL,        -- 事件类型
  event_category TEXT,             -- 事件分类
  event_label TEXT,                -- 事件标签
  
  -- 产品信息
  product_id INTEGER,              -- 产品ID
  product_sku TEXT,                -- 产品SKU
  product_category TEXT,           -- 产品分类
  product_price REAL,              -- 产品价格
  
  -- 上下文信息
  page_url TEXT,                   -- 页面URL
  referrer TEXT,                   -- 来源页面
  search_query TEXT,               -- 搜索关键词
  recommendation_context TEXT,     -- 推荐上下文
  
  -- 交互详情
  duration INTEGER,                -- 停留时长（秒）
  scroll_depth INTEGER,            -- 滚动深度（%）
  click_position INTEGER,          -- 点击位置
  
  -- 设备信息
  user_agent TEXT,                 -- User Agent
  device_type TEXT,                -- 设备类型
  browser TEXT,                    -- 浏览器
  os TEXT,                         -- 操作系统
  screen_resolution TEXT,          -- 屏幕分辨率
  
  -- 地理位置
  country TEXT,                    -- 国家
  region TEXT,                     -- 地区
  city TEXT,                       -- 城市
  timezone TEXT,                   -- 时区
  
  -- 元数据
  ip_address TEXT,                 -- IP地址（加密）
  timestamp TEXT NOT NULL,         -- 时间戳
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_user_behaviors_user ON user_behaviors(user_id);
CREATE INDEX idx_user_behaviors_session ON user_behaviors(session_id);
CREATE INDEX idx_user_behaviors_product ON user_behaviors(product_id);
CREATE INDEX idx_user_behaviors_event ON user_behaviors(event_type);
CREATE INDEX idx_user_behaviors_timestamp ON user_behaviors(timestamp);
```

#### B. training_interactions（训练交互表）

```sql
CREATE TABLE training_interactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  
  -- 核心字段（TFRS 需要）
  user_id TEXT NOT NULL,           -- 用户ID
  item_id TEXT NOT NULL,           -- 商品ID
  rating REAL,                     -- 评分/权重
  timestamp INTEGER NOT NULL,      -- Unix 时间戳
  
  -- 扩展字段
  interaction_type TEXT,           -- view/click/cart/purchase
  interaction_weight REAL,         -- 交互权重
  context TEXT,                    -- 上下文 JSON
  
  -- 特征字段
  user_features TEXT,              -- 用户特征 JSON
  item_features TEXT,              -- 商品特征 JSON
  
  -- 元数据
  source TEXT DEFAULT 'platform',  -- 数据来源
  is_training INTEGER DEFAULT 1,   -- 是否用于训练
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_training_user ON training_interactions(user_id);
CREATE INDEX idx_training_item ON training_interactions(item_id);
CREATE INDEX idx_training_timestamp ON training_interactions(timestamp);
CREATE INDEX idx_training_type ON training_interactions(interaction_type);
```

#### C. recommendation_logs（推荐日志表）

```sql
CREATE TABLE recommendation_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  
  -- 推荐信息
  recommendation_id TEXT UNIQUE NOT NULL,
  user_id TEXT,
  session_id TEXT,
  
  -- 推荐结果
  recommended_items TEXT NOT NULL,  -- JSON 数组
  algorithm TEXT,                   -- 推荐算法
  context TEXT,                     -- 推荐场景
  
  -- 反馈信息
  displayed_items TEXT,             -- 实际展示的商品
  clicked_items TEXT,               -- 点击的商品
  purchased_items TEXT,             -- 购买的商品
  
  -- 性能指标
  response_time INTEGER,            -- 响应时间（ms）
  model_version TEXT,               -- 模型版本
  
  -- 时间
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  feedback_at TEXT                  -- 反馈时间
);

-- 索引
CREATE INDEX idx_rec_logs_user ON recommendation_logs(user_id);
CREATE INDEX idx_rec_logs_session ON recommendation_logs(session_id);
CREATE INDEX idx_rec_logs_created ON recommendation_logs(created_at);
```

### 4.2 TFRS 训练数据格式

#### 标准 CSV 格式

```csv
user_id,item_id,rating,timestamp,interaction_type
user_001,prod_123,5.0,1705478400,purchase
user_001,prod_456,3.0,1705478500,view
user_002,prod_123,4.0,1705478600,cart
user_002,prod_789,5.0,1705478700,purchase
```

#### TensorFlow Dataset 格式

```python
# 数据结构
{
  'user_id': tf.string,
  'item_id': tf.string,
  'rating': tf.float32,
  'timestamp': tf.int64,
  'user_features': {
    'age_group': tf.string,
    'country': tf.string,
    'total_purchases': tf.int32
  },
  'item_features': {
    'category': tf.string,
    'price': tf.float32,
    'tags': tf.string
  }
}
```

---

## 5. 技术实现

### 5.1 前端数据收集 SDK

#### A. SDK 核心代码

```javascript
// tracking-sdk.js
class ManiDalaTracker {
  constructor(config) {
    this.endpoint = config.endpoint || '/api/v2/tracking';
    this.userId = config.userId || null;
    this.sessionId = this.getOrCreateSessionId();
    this.deviceId = this.getOrCreateDeviceId();
    this.queue = [];
    this.flushInterval = config.flushInterval || 5000;
    
    this.init();
  }
  
  init() {
    // 自动追踪页面浏览
    this.trackPageView();
    
    // 定期发送数据
    setInterval(() => this.flush(), this.flushInterval);
    
    // 页面卸载时发送
    window.addEventListener('beforeunload', () => this.flush());
  }
  
  // 追踪事件
  track(eventType, properties = {}) {
    const event = {
      event_type: eventType,
      user_id: this.userId,
      session_id: this.sessionId,
      device_id: this.deviceId,
      timestamp: new Date().toISOString(),
      properties: properties,
      context: this.getContext()
    };
    
    this.queue.push(event);
    
    // 重要事件立即发送
    if (this.isImportantEvent(eventType)) {
      this.flush();
    }
  }
  
  // 追踪产品浏览
  trackProductView(productId, productData = {}) {
    this.track('product_view', {
      product_id: productId,
      product_sku: productData.sku,
      product_name: productData.name,
      product_price: productData.price,
      product_category: productData.category
    });
  }
  
  // 追踪产品点击
  trackProductClick(productId, position, context) {
    this.track('product_click', {
      product_id: productId,
      click_position: position,
      recommendation_context: context
    });
  }
  
  // 追踪加购
  trackAddToCart(productId, quantity = 1) {
    this.track('add_to_cart', {
      product_id: productId,
      quantity: quantity
    });
  }
  
  // 追踪搜索
  trackSearch(query, resultCount) {
    this.track('search', {
      search_query: query,
      result_count: resultCount
    });
  }
  
  // 追踪购买
  trackPurchase(orderId, items, totalAmount) {
    this.track('purchase', {
      order_id: orderId,
      items: items,
      total_amount: totalAmount
    });
  }
  
  // 发送数据
  async flush() {
    if (this.queue.length === 0) return;
    
    const events = [...this.queue];
    this.queue = [];
    
    try {
      await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ events }),
        keepalive: true
      });
    } catch (error) {
      console.error('Tracking error:', error);
      // 失败的事件放回队列
      this.queue.unshift(...events);
    }
  }
  
  // 获取上下文信息
  getContext() {
    return {
      page_url: window.location.href,
      referrer: document.referrer,
      user_agent: navigator.userAgent,
      screen_resolution: `${screen.width}x${screen.height}`,
      viewport_size: `${window.innerWidth}x${window.innerHeight}`,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
  }
  
  // 会话ID管理
  getOrCreateSessionId() {
    let sessionId = sessionStorage.getItem('manidala_session_id');
    if (!sessionId) {
      sessionId = this.generateId();
      sessionStorage.setItem('manidala_session_id', sessionId);
    }
    return sessionId;
  }
  
  // 设备ID管理
  getOrCreateDeviceId() {
    let deviceId = localStorage.getItem('manidala_device_id');
    if (!deviceId) {
      deviceId = this.generateId();
      localStorage.setItem('manidala_device_id', deviceId);
    }
    return deviceId;
  }
  
  // 生成唯一ID
  generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  // 判断是否重要事件
  isImportantEvent(eventType) {
    return ['purchase', 'add_to_cart', 'checkout_start'].includes(eventType);
  }
  
  // 追踪页面浏览
  trackPageView() {
    const startTime = Date.now();
    
    this.track('page_view', {
      page_title: document.title,
      page_path: window.location.pathname
    });
    
    // 追踪页面停留时长
    window.addEventListener('beforeunload', () => {
      const duration = Math.floor((Date.now() - startTime) / 1000);
      this.track('page_leave', {
        duration: duration,
        page_path: window.location.pathname
      });
    });
  }
}

// 初始化
window.ManiDalaTracker = ManiDalaTracker;
```

#### B. 使用示例

```html
<!-- 在页面中引入 -->
<script src="/js/tracking-sdk.js"></script>
<script>
  // 初始化追踪器
  const tracker = new ManiDalaTracker({
    endpoint: '/api/v2/tracking',
    userId: '{{ user.id }}', // 从后端注入
    flushInterval: 5000
  });
  
  // 追踪产品点击
  document.querySelectorAll('.product-card').forEach((card, index) => {
    card.addEventListener('click', () => {
      const productId = card.dataset.productId;
      tracker.trackProductClick(productId, index, 'homepage_new_arrivals');
    });
  });
  
  // 追踪加购按钮
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const productId = btn.dataset.productId;
      tracker.trackAddToCart(productId);
    });
  });
</script>
```

### 5.2 后端数据收集 Worker

#### A. Tracking Worker

```javascript
// workers/manidala-tracking/src/index.js
export default {
  async fetch(request, env) {
    // CORS 处理
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }
    
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }
    
    try {
      const { events } = await request.json();
      
      // 批量插入数据库
      const stmt = env.DB.prepare(`
        INSERT INTO user_behaviors (
          user_id, session_id, device_id, event_type,
          product_id, page_url, timestamp, context
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `);
      
      const batch = events.map(event => 
        stmt.bind(
          event.user_id,
          event.session_id,
          event.device_id,
          event.event_type,
          event.properties?.product_id,
          event.context?.page_url,
          event.timestamp,
          JSON.stringify(event)
        )
      );
      
      await env.DB.batch(batch);
      
      return new Response(JSON.stringify({ success: true }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    } catch (error) {
      console.error('Tracking error:', error);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
```

### 5.3 数据处理和导出

#### A. 数据转换脚本

```javascript
// scripts/export-training-data.js
export default {
  async scheduled(event, env) {
    console.log('Starting training data export...');
    
    // 1. 查询用户行为数据
    const behaviors = await env.DB.prepare(`
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
      WHERE timestamp >= datetime('now', '-30 days')
        AND product_id IS NOT NULL
      ORDER BY timestamp
    `).all();
    
    // 2. 转换为 CSV
    const csv = convertToCSV(behaviors.results);
    
    // 3. 上传到 R2
    await env.R2_BUCKET.put(
      `training-data/interactions-${Date.now()}.csv`,
      csv,
      {
        httpMetadata: {
          contentType: 'text/csv'
        }
      }
    );
    
    console.log(`Exported ${behaviors.results.length} interactions`);
  }
};

function convertToCSV(data) {
  const headers = ['user_id', 'item_id', 'rating', 'timestamp', 'interaction_type'];
  const rows = data.map(row => 
    headers.map(h => row[h]).join(',')
  );
  return [headers.join(','), ...rows].join('\n');
}
```

#### B. Scheduled Worker 配置

```toml
# wrangler.toml
name = "manidala-data-export"
main = "src/index.js"
compatibility_date = "2024-01-01"

[triggers]
crons = ["0 2 * * *"]  # 每天凌晨2点执行

[[d1_databases]]
binding = "DB"
database_name = "manidala-db"
database_id = "9aa23ffd-5100-413d-94d7-448c709e5abc"

[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "manidala-training-data"
```

---

## 6. 数据质量保证

### 6.1 数据验证规则

#### A. 必填字段验证

```javascript
const VALIDATION_RULES = {
  user_behaviors: {
    required: ['session_id', 'event_type', 'timestamp'],
    optional: ['user_id', 'product_id', 'duration']
  },
  training_interactions: {
    required: ['user_id', 'item_id', 'rating', 'timestamp'],
    optional: ['interaction_type', 'context']
  }
};
```

#### B. 数据类型验证

```javascript
function validateEvent(event) {
  const errors = [];
  
  // 检查必填字段
  if (!event.session_id) errors.push('Missing session_id');
  if (!event.event_type) errors.push('Missing event_type');
  if (!event.timestamp) errors.push('Missing timestamp');
  
  // 检查数据类型
  if (event.product_id && typeof event.product_id !== 'number') {
    errors.push('Invalid product_id type');
  }
  
  // 检查时间戳格式
  if (event.timestamp && !isValidTimestamp(event.timestamp)) {
    errors.push('Invalid timestamp format');
  }
  
  return errors;
}
```

#### C. 数据范围验证

```javascript
const DATA_RANGES = {
  rating: { min: 0, max: 5 },
  duration: { min: 0, max: 86400 }, // 最多24小时
  scroll_depth: { min: 0, max: 100 },
  price: { min: 0, max: 10000 }
};
```

### 6.2 数据清洗流程

#### A. 去重逻辑

```sql
-- 去除重复的用户行为（同一用户在5秒内的相同事件）
DELETE FROM user_behaviors
WHERE id NOT IN (
  SELECT MIN(id)
  FROM user_behaviors
  GROUP BY user_id, product_id, event_type, 
           strftime('%Y-%m-%d %H:%M', timestamp, 'unixepoch')
);
```

#### B. 异常值处理

```sql
-- 删除异常停留时长（> 24小时）
DELETE FROM user_behaviors
WHERE duration > 86400;

-- 删除未来时间戳
DELETE FROM user_behaviors
WHERE timestamp > strftime('%s', 'now');

-- 删除过旧数据（> 1年）
DELETE FROM user_behaviors
WHERE timestamp < strftime('%s', 'now', '-1 year');
```

#### C. 数据补全

```javascript
// 补全缺失的用户ID（使用session_id）
async function fillMissingUserIds() {
  await env.DB.prepare(`
    UPDATE user_behaviors
    SET user_id = session_id
    WHERE user_id IS NULL
  `).run();
}
```

### 6.3 数据质量监控

#### A. 质量指标

```javascript
const QUALITY_METRICS = {
  completeness: {
    // 完整性：必填字段填充率
    target: 0.95,
    query: `
      SELECT 
        COUNT(*) FILTER (WHERE user_id IS NOT NULL) * 1.0 / COUNT(*) as user_id_rate,
        COUNT(*) FILTER (WHERE product_id IS NOT NULL) * 1.0 / COUNT(*) as product_id_rate
      FROM user_behaviors
    `
  },
  accuracy: {
    // 准确性：有效数据占比
    target: 0.98,
    query: `
      SELECT 
        COUNT(*) FILTER (WHERE duration BETWEEN 0 AND 86400) * 1.0 / COUNT(*) as valid_duration_rate
      FROM user_behaviors
    `
  },
  timeliness: {
    // 时效性：最新数据时间
    target: 300, // 5分钟内
    query: `
      SELECT 
        strftime('%s', 'now') - MAX(strftime('%s', timestamp)) as seconds_since_last
      FROM user_behaviors
    `
  }
};
```

#### B. 质量报告

```javascript
async function generateQualityReport(env) {
  const report = {
    timestamp: new Date().toISOString(),
    metrics: {}
  };
  
  // 数据量统计
  const counts = await env.DB.prepare(`
    SELECT 
      COUNT(*) as total,
      COUNT(DISTINCT user_id) as unique_users,
      COUNT(DISTINCT product_id) as unique_products,
      COUNT(DISTINCT DATE(timestamp)) as active_days
    FROM user_behaviors
    WHERE timestamp >= datetime('now', '-30 days')
  `).first();
  
  report.metrics.volume = counts;
  
  // 数据质量统计
  const quality = await env.DB.prepare(`
    SELECT 
      COUNT(*) FILTER (WHERE user_id IS NOT NULL) * 100.0 / COUNT(*) as user_id_completeness,
      COUNT(*) FILTER (WHERE product_id IS NOT NULL) * 100.0 / COUNT(*) as product_id_completeness,
      COUNT(*) FILTER (WHERE duration > 0 AND duration < 86400) * 100.0 / COUNT(*) as valid_duration_rate
    FROM user_behaviors
  `).first();
  
  report.metrics.quality = quality;
  
  return report;
}
```

### 6.4 数据采样策略

#### A. 训练/测试集划分

```python
# 时间序列划分（80/20）
def split_data_by_time(df):
    df = df.sort_values('timestamp')
    split_idx = int(len(df) * 0.8)
    
    train_df = df[:split_idx]
    test_df = df[split_idx:]
    
    return train_df, test_df
```

#### B. 负采样策略

```python
# 为每个正样本生成4个负样本
def generate_negative_samples(positive_samples, all_items, ratio=4):
    negative_samples = []
    
    for user_id, item_id in positive_samples:
        # 随机选择用户未交互的商品
        user_items = set(positive_samples[positive_samples['user_id'] == user_id]['item_id'])
        available_items = list(set(all_items) - user_items)
        
        neg_items = random.sample(available_items, min(ratio, len(available_items)))
        
        for neg_item in neg_items:
            negative_samples.append({
                'user_id': user_id,
                'item_id': neg_item,
                'rating': 0.0,
                'timestamp': int(time.time())
            })
    
    return negative_samples
```

---

## 7. 隐私与合规

### 7.1 数据隐私保护

#### A. 数据脱敏

```javascript
// IP地址脱敏（只保留前3段）
function anonymizeIP(ip) {
  const parts = ip.split('.');
  return `${parts[0]}.${parts[1]}.${parts[2]}.0`;
}

// 邮箱脱敏
function anonymizeEmail(email) {
  const [local, domain] = email.split('@');
  return `${local.substring(0, 3)}***@${domain}`;
}

// 用户ID哈希
async function hashUserId(userId) {
  const encoder = new TextEncoder();
  const data = encoder.encode(userId + SALT);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
```

#### B. 数据加密

```javascript
// 敏感字段加密存储
async function encryptSensitiveData(data, key) {
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(JSON.stringify(data));
  
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: crypto.getRandomValues(new Uint8Array(12)) },
    key,
    dataBuffer
  );
  
  return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
}
```

### 7.2 用户同意管理

#### A. Cookie 同意横幅

```html
<div id="cookie-consent" class="cookie-banner">
  <p>
    We use cookies and tracking to improve your experience. 
    <a href="/privacy">Learn more</a>
  </p>
  <button onclick="acceptTracking()">Accept</button>
  <button onclick="rejectTracking()">Reject</button>
</div>

<script>
function acceptTracking() {
  localStorage.setItem('tracking_consent', 'accepted');
  document.getElementById('cookie-consent').style.display = 'none';
  initTracker();
}

function rejectTracking() {
  localStorage.setItem('tracking_consent', 'rejected');
  document.getElementById('cookie-consent').style.display = 'none';
}

// 检查同意状态
if (localStorage.getItem('tracking_consent') === 'accepted') {
  initTracker();
}
</script>
```

#### B. 数据访问和删除

```javascript
// 用户数据导出（GDPR 要求）
async function exportUserData(userId, env) {
  const behaviors = await env.DB.prepare(`
    SELECT * FROM user_behaviors
    WHERE user_id = ?
  `).bind(userId).all();
  
  return {
    user_id: userId,
    data: behaviors.results,
    exported_at: new Date().toISOString()
  };
}

// 用户数据删除（GDPR 要求）
async function deleteUserData(userId, env) {
  await env.DB.prepare(`
    DELETE FROM user_behaviors WHERE user_id = ?
  `).bind(userId).run();
  
  await env.DB.prepare(`
    DELETE FROM training_interactions WHERE user_id = ?
  `).bind(userId).run();
  
  return { success: true, deleted_at: new Date().toISOString() };
}
```

### 7.3 合规检查清单

#### GDPR 合规

- ✅ 用户同意机制
- ✅ 数据访问权（导出）
- ✅ 数据删除权（被遗忘权）
- ✅ 数据最小化原则
- ✅ 数据加密存储
- ✅ 隐私政策透明

#### CCPA 合规

- ✅ 数据收集通知
- ✅ 选择退出机制
- ✅ 数据出售禁止
- ✅ 数据访问请求

---

## 8. 实施路线图

### 8.1 阶段 1：基础设施搭建（1周）

**目标**: 建立数据收集基础设施

**任务清单**:
- [ ] 创建数据库表（user_behaviors, training_interactions, recommendation_logs）
- [ ] 开发前端追踪 SDK
- [ ] 部署 Tracking Worker
- [ ] 配置 R2 存储桶
- [ ] 测试数据收集流程

**交付物**:
- 数据库 Schema
- Tracking SDK (v1.0)
- Tracking Worker (deployed)
- 测试报告

### 8.2 阶段 2：数据收集启动（2周）

**目标**: 开始收集真实用户数据

**任务清单**:
- [ ] 在前端页面集成 Tracking SDK
- [ ] 配置关键事件追踪点
- [ ] 实施数据验证规则
- [ ] 设置数据质量监控
- [ ] 收集初始数据（目标：5万条）

**交付物**:
- 集成文档
- 数据质量报告
- 初始数据集（CSV）

### 8.3 阶段 3：数据处理优化（1周）

**目标**: 优化数据处理和导出流程

**任务清单**:
- [ ] 开发数据清洗脚本
- [ ] 实施数据去重逻辑
- [ ] 配置定时导出任务
- [ ] 优化数据格式转换
- [ ] 测试 TFRS 数据导入

**交付物**:
- 数据处理脚本
- 导出配置文件
- TFRS 兼容数据集

### 8.4 阶段 4：模型训练集成（1周）

**目标**: 使用真实数据训练 TFRS 模型

**任务清单**:
- [ ] 导出训练数据到 Colab
- [ ] 更新训练笔记本
- [ ] 训练第一个真实数据模型
- [ ] 评估模型性能
- [ ] 部署模型到生产环境

**交付物**:
- 训练好的模型
- 性能评估报告
- 部署文档

### 8.5 阶段 5：持续优化（持续）

**目标**: 持续改进数据质量和模型效果

**任务清单**:
- [ ] 监控数据收集质量
- [ ] 定期重训练模型（每周）
- [ ] A/B 测试推荐效果
- [ ] 收集用户反馈
- [ ] 优化推荐算法

**交付物**:
- 周度质量报告
- 月度性能报告
- 优化建议文档

---

## 9. 成本估算

### 9.1 基础设施成本

| 项目 | 服务 | 月成本 | 说明 |
|------|------|--------|------|
| 数据库 | Cloudflare D1 | $5 | 包含 500万行 |
| 存储 | Cloudflare R2 | $0.015/GB | 约 $1-5 |
| Workers | Cloudflare Workers | $5 | 包含 1000万请求 |
| 训练 | Google Colab Pro | $10 | GPU 加速 |
| 部署 | Railway | $10-20 | 推荐服务 |
| **总计** | | **$31-45** | **约 ¥220-320** |

### 9.2 人力成本

| 阶段 | 工作量 | 说明 |
|------|--------|------|
| 阶段 1 | 40小时 | 基础设施搭建 |
| 阶段 2 | 80小时 | 数据收集启动 |
| 阶段 3 | 40小时 | 数据处理优化 |
| 阶段 4 | 40小时 | 模型训练集成 |
| 阶段 5 | 20小时/月 | 持续优化 |

---

## 10. 风险与挑战

### 10.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 数据量不足 | 高 | 中 | 使用公开数据集补充 |
| 数据质量差 | 高 | 中 | 严格验证和清洗 |
| 性能瓶颈 | 中 | 低 | 使用缓存和批处理 |
| 隐私合规 | 高 | 低 | 实施脱敏和加密 |

### 10.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 用户量少 | 高 | 高 | 使用模拟数据 |
| 冷启动问题 | 中 | 高 | 基于内容推荐 |
| 推荐效果差 | 高 | 中 | A/B 测试优化 |

---

## 11. 成功指标

### 11.1 数据收集指标

- ✅ 日活跃用户数 > 100
- ✅ 日交互数 > 1000
- ✅ 数据完整率 > 95%
- ✅ 数据准确率 > 98%

### 11.2 模型性能指标

- ✅ 推荐准确率 > 70%
- ✅ 点击率 > 5%
- ✅ 转化率 > 3%
- ✅ 响应时间 < 200ms

### 11.3 业务影响指标

- ✅ GMV 提升 > 20%
- ✅ 客单价提升 > 15%
- ✅ 用户停留时长提升 > 30%

---

## 12. 总结

本数据收集方案提供了一套完整的解决方案，从数据源分析、架构设计、技术实现到质量保证和合规管理，覆盖了 TFRS 训练数据收集的全流程。

### 核心优势

1. **低成本**: 月成本 $31-45，比传统方案便宜 70%+
2. **高效率**: 使用 Cloudflare 边缘计算，全球低延迟
3. **可扩展**: 支持从百万到千万级数据量
4. **合规性**: 符合 GDPR/CCPA 等隐私法规
5. **易维护**: 代码简洁，文档完善

### 下一步行动

1. **立即开始**: 使用公开数据集训练第一个模型
2. **并行推进**: 搭建数据收集基础设施
3. **快速迭代**: 2周内收集真实数据并重训练
4. **持续优化**: 建立数据-训练-部署的闭环

---

**文档版本**: 1.0  
**创建日期**: 2026-01-17  
**维护者**: ManiDala Team  
**状态**: ✅ 待实施
