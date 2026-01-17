# TFRS 推荐系统快速开始指南

## 🚀 5分钟快速部署

### 前置条件
- ✅ Google Colab 账号（已注册）
- ✅ Railway 账号（已有）
- ✅ GitHub 账号

---

## 步骤 1: 在 Colab 训练模型（2-4小时）

### 1.1 打开 Colab 笔记本

1. 访问 Google Colab: https://colab.research.google.com/
2. 上传笔记本文件: [`notebooks/TFRS_Training_Colab.ipynb`](notebooks/TFRS_Training_Colab.ipynb)
3. 或者直接在 Colab 中打开 GitHub 链接

### 1.2 配置 GPU

```
菜单栏 → 运行时 → 更改运行时类型 → 硬件加速器 → GPU → 保存
```

### 1.3 运行训练

```
菜单栏 → 运行时 → 全部运行
```

**等待时间**: 2-4小时（取决于数据量）

### 1.4 下载模型

训练完成后，笔记本会自动下载 `saved_models.zip` 文件

---

## 步骤 2: 准备项目代码（5分钟）

### 2.1 创建 GitHub 仓库

```bash
# 在本地创建仓库
cd recommend/tfrs-system
git init
git add .
git commit -m "Initial commit: TFRS recommendation system"

# 在 GitHub 创建新仓库，然后推送
git remote add origin https://github.com/your-username/tfrs-system.git
git branch -M main
git push -u origin main
```

### 2.2 上传训练好的模型

```bash
# 解压下载的模型
unzip saved_models.zip

# 创建模型目录
mkdir -p models/saved_models

# 移动模型文件
mv saved_models/two_tower models/saved_models/

# 提交到 Git
git add models/
git commit -m "Add trained model"
git push
```

---

## 步骤 3: 部署到 Railway（2分钟）

### 3.1 连接 GitHub

1. 登录 Railway: https://railway.app/
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的 `tfrs-system` 仓库

### 3.2 配置环境变量

在 Railway Dashboard 中设置：

```
MODEL_PATH=/app/models/saved_models/two_tower
API_KEY=your_secret_key_here
LOG_LEVEL=INFO
```

### 3.3 等待部署

Railway 会自动：
1. 检测 Dockerfile
2. 构建镜像
3. 部署服务
4. 分配域名

**部署时间**: 约 2-5 分钟

---

## 步骤 4: 测试 API（1分钟）

### 4.1 获取服务 URL

在 Railway Dashboard 中找到您的服务 URL，例如：
```
https://tfrs-system-production.up.railway.app
```

### 4.2 测试健康检查

```bash
curl https://your-app.railway.app/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "service": "tfrs-api",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### 4.3 测试推荐 API

```bash
curl -X POST https://your-app.railway.app/api/recommend \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_key_here" \
  -d '{
    "user_id": "user_1",
    "top_k": 10
  }'
```

**预期响应**:
```json
{
  "user_id": "user_1",
  "recommendations": [
    {
      "item_id": "item_1",
      "score": 0.9,
      "reason": "collaborative_filtering",
      "metadata": {
        "name": "Product 1",
        "category": "mandala",
        "price": 29.99
      }
    }
  ],
  "total": 10,
  "model_version": "v1.0"
}
```

---

## 步骤 5: 集成到前端（10分钟）

### 5.1 安装依赖

```bash
npm install axios
```

### 5.2 创建推荐服务

```typescript
// src/services/tfrs.service.ts
import axios from 'axios';

const TFRS_API_URL = 'https://your-app.railway.app';
const API_KEY = 'your_secret_key_here';

export async function getRecommendations(userId: string, topK: number = 10) {
  try {
    const response = await axios.post(
      `${TFRS_API_URL}/api/recommend`,
      {
        user_id: userId,
        top_k: topK
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        }
      }
    );
    
    return response.data.recommendations;
  } catch (error) {
    console.error('TFRS API error:', error);
    return [];
  }
}
```

### 5.3 在组件中使用

```typescript
// src/components/Recommendations.tsx
import { useEffect, useState } from 'react';
import { getRecommendations } from '@/services/tfrs.service';

export function Recommendations({ userId }: { userId: string }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRecommendations() {
      const recs = await getRecommendations(userId);
      setProducts(recs);
      setLoading(false);
    }
    
    fetchRecommendations();
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="recommendations">
      <h2>Recommended for You</h2>
      <div className="grid">
        {products.map(product => (
          <div key={product.item_id} className="product-card">
            <h3>{product.metadata.name}</h3>
            <p>${product.metadata.price}</p>
            <span>Score: {product.score.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 完成！🎉

您的 TFRS 推荐系统已经成功部署并运行！

### 总耗时
- Colab 训练: 2-4小时（自动）
- 代码准备: 5分钟
- Railway 部署: 2分钟
- API 测试: 1分钟
- 前端集成: 10分钟

**总计**: 约 20分钟（不含训练时间）

---

## 常见问题

### Q1: 模型加载失败怎么办？

**检查**:
1. 模型文件是否正确上传到 `models/saved_models/` 目录
2. Railway 环境变量 `MODEL_PATH` 是否正确设置
3. 查看 Railway 日志: `railway logs`

**解决**:
```bash
# 重新上传模型
git add models/
git commit -m "Fix model path"
git push

# Railway 会自动重新部署
```

### Q2: API 返回 503 错误？

**原因**: 模型未加载或服务未启动

**解决**:
1. 检查 Railway 日志
2. 确认服务状态
3. 重启服务: Railway Dashboard → Restart

### Q3: 推荐结果不准确？

**原因**: 使用的是模拟数据

**解决**:
1. 在 Colab 中使用真实数据重新训练
2. 调整模型参数（embedding_dim, 网络层数）
3. 增加训练 epochs

### Q4: Railway 成本太高？

**优化**:
1. 使用 Railway 的 Sleep 功能（空闲时自动休眠）
2. 减小 Docker 镜像大小
3. 使用模型量化减少内存占用

### Q5: 如何更新模型？

```bash
# 1. 在 Colab 重新训练
# 2. 下载新模型
# 3. 替换旧模型
rm -rf models/saved_models/two_tower
mv new_saved_models/two_tower models/saved_models/

# 4. 提交并推送
git add models/
git commit -m "Update model"
git push

# Railway 自动重新部署
```

---

## 下一步

### 性能优化
- [ ] 实现模型缓存
- [ ] 添加 Redis 缓存推荐结果
- [ ] 使用 ScaNN 加速检索
- [ ] 模型量化减小体积

### 功能增强
- [ ] 添加 A/B 测试
- [ ] 实现实时推荐
- [ ] 添加用户反馈收集
- [ ] 实现多模型集成

### 监控与分析
- [ ] 添加 Prometheus 监控
- [ ] 实现推荐效果分析
- [ ] 添加告警通知
- [ ] 生成推荐报表

---

## 获取帮助

- 📖 查看完整文档: [`README.md`](README.md)
- 🏗️ 了解架构: [`SYSTEM-ARCHITECTURE.md`](../SYSTEM-ARCHITECTURE.md)
- 💻 查看代码: [`src/serving/api.py`](src/serving/api.py)
- 📓 Colab 笔记本: [`notebooks/TFRS_Training_Colab.ipynb`](notebooks/TFRS_Training_Colab.ipynb)

---

**祝您使用愉快！** 🚀