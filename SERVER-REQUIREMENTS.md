# TFRS 推荐系统服务器需求

## 服务器配置方案

### 方案 1: 开发/测试环境（最低配置）⭐⭐⭐

**适用场景**: 学习、原型开发、小规模测试

#### 配置
```
CPU: 4核 (Intel i5 或同等)
内存: 16GB RAM
GPU: 无（使用 CPU 训练）
存储: 100GB SSD
网络: 10Mbps

操作系统: Ubuntu 20.04 LTS
```

#### 云服务器推荐
| 提供商 | 实例类型 | 价格 | 说明 |
|--------|---------|------|------|
| **阿里云** | ecs.c6.xlarge | ¥0.45/小时 (¥324/月) | 4核8GB，按需付费 |
| **腾讯云** | S5.MEDIUM4 | ¥0.42/小时 (¥302/月) | 4核8GB |
| **AWS** | t3.xlarge | $0.1664/小时 ($120/月) | 4核16GB |
| **Google Cloud** | n1-standard-4 | $0.19/小时 ($137/月) | 4核15GB |

#### 性能预期
```
训练速度: 慢（1-2天训练一个模型）
推理速度: 100-200ms
并发能力: 10-50 QPS
数据规模: < 10万交互记录
```

---

### 方案 2: 生产环境（推荐配置）⭐⭐⭐⭐⭐

**适用场景**: 正式上线、中等规模数据

#### 配置
```
CPU: 8核 (Intel Xeon 或 AMD EPYC)
内存: 32GB RAM
GPU: NVIDIA T4 (16GB VRAM)
存储: 500GB SSD
网络: 100Mbps

操作系统: Ubuntu 20.04 LTS
```

#### 云服务器推荐
| 提供商 | 实例类型 | 价格 | 说明 |
|--------|---------|------|------|
| **阿里云** | ecs.gn6i-c8g1.2xlarge | ¥7.34/小时 (¥5,285/月) | 8核32GB + T4 |
| **腾讯云** | GN7.2XLARGE32 | ¥6.8/小时 (¥4,896/月) | 8核32GB + T4 |
| **AWS** | g4dn.2xlarge | $0.752/小时 ($542/月) | 8核32GB + T4 |
| **Google Cloud** | n1-standard-8 + T4 | $0.65/小时 ($468/月) | 8核30GB + T4 |

#### 性能预期
```
训练速度: 快（2-4小时训练一个模型）
推理速度: 20-50ms
并发能力: 500-1000 QPS
数据规模: 100万-1000万交互记录
```

---

### 方案 3: 高性能环境（大规模）⭐⭐⭐⭐⭐

**适用场景**: 大规模数据、高并发、实时训练

#### 配置
```
CPU: 16核 (Intel Xeon 或 AMD EPYC)
内存: 64GB RAM
GPU: NVIDIA V100 (32GB VRAM) 或 A100 (40GB VRAM)
存储: 1TB NVMe SSD
网络: 1Gbps

操作系统: Ubuntu 20.04 LTS
```

#### 云服务器推荐
| 提供商 | 实例类型 | 价格 | 说明 |
|--------|---------|------|------|
| **阿里云** | ecs.gn6v-c10g1.20xlarge | ¥27.78/小时 (¥20,001/月) | 16核64GB + V100 |
| **腾讯云** | GN10X.4XLARGE80 | ¥25.6/小时 (¥18,432/月) | 16核80GB + V100 |
| **AWS** | p3.2xlarge | $3.06/小时 ($2,203/月) | 8核61GB + V100 |
| **Google Cloud** | n1-standard-16 + V100 | $2.48/小时 ($1,786/月) | 16核60GB + V100 |

#### 性能预期
```
训练速度: 极快（30分钟-1小时训练一个模型）
推理速度: 10-20ms
并发能力: 5000+ QPS
数据规模: 1000万+ 交互记录
```

---

## 详细配置说明

### 1. CPU 要求

#### 为什么需要多核？
```python
# TensorFlow 会自动使用多核并行
import tensorflow as tf

# 数据预处理并行
dataset = tf.data.Dataset.from_tensor_slices(data)
dataset = dataset.map(
    preprocess_fn,
    num_parallel_calls=tf.data.AUTOTUNE  # 自动使用所有核心
)

# 模型训练并行
strategy = tf.distribute.MirroredStrategy()  # 多GPU并行
with strategy.scope():
    model = build_model()
```

#### CPU 选择建议
- **Intel**: Xeon 系列（服务器级）
- **AMD**: EPYC 系列（性价比高）
- **避免**: 低端 Celeron、Pentium

---

### 2. 内存要求

#### 内存使用估算
```python
# 数据加载到内存
data_size = 100_000 * 100  # 10万样本 × 100维特征
memory_needed = data_size * 4 / (1024**3)  # 约 0.04GB

# 模型参数
model_params = 15_000_000  # 1500万参数
model_memory = model_params * 4 / (1024**3)  # 约 0.06GB

# 训练时梯度和优化器状态
training_memory = model_memory * 3  # 约 0.18GB

# 批处理数据
batch_size = 1024
batch_memory = batch_size * 100 * 4 / (1024**3)  # 约 0.0004GB

# 总计（保守估计）
total = data_size + model_memory + training_memory + batch_memory
# 实际需要 2-4 倍缓冲 = 16-32GB
```

#### 内存选择建议
- **最低**: 16GB（小规模）
- **推荐**: 32GB（中等规模）
- **理想**: 64GB+（大规模）

---

### 3. GPU 要求

#### 为什么需要 GPU？
```
训练速度对比（10万样本，10个epoch）:

CPU (8核):     2-4 小时
GPU (T4):      15-30 分钟  (8-16倍加速)
GPU (V100):    5-10 分钟   (24-48倍加速)
GPU (A100):    2-5 分钟    (48-120倍加速)
```

#### GPU 选择建议

| GPU | VRAM | 性能 | 价格 | 推荐场景 |
|-----|------|------|------|---------|
| **无GPU** | - | 1x | $0 | 学习、测试 |
| **GTX 1660** | 6GB | 3x | ¥1,500 | 个人开发 |
| **RTX 3060** | 12GB | 5x | ¥2,500 | 小规模生产 |
| **T4** | 16GB | 8x | ¥5,000/月 | 中等规模 |
| **V100** | 32GB | 20x | ¥20,000/月 | 大规模 |
| **A100** | 40GB | 40x | ¥40,000/月 | 超大规模 |

#### VRAM 需求估算
```python
# 模型大小
model_size = 15_000_000 * 4 / (1024**3)  # 约 0.06GB

# 批处理大小
batch_size = 1024
batch_vram = batch_size * 100 * 4 / (1024**3)  # 约 0.0004GB

# 梯度和优化器
gradient_vram = model_size * 2  # 约 0.12GB

# 总计
total_vram = model_size + batch_vram + gradient_vram  # 约 0.18GB

# 实际需要 4-8 倍缓冲 = 1-2GB
# 推荐: 8GB+ VRAM
```

---

### 4. 存储要求

#### 存储使用估算
```
原始数据:        10GB   (100万张图片)
处理后数据:      5GB    (特征向量)
模型检查点:      2GB    (每个epoch 200MB × 10)
日志和元数据:    1GB
临时文件:        5GB

总计: 约 25GB
推荐: 100GB+ SSD
```

#### 存储类型选择
- **HDD**: 慢，不推荐
- **SATA SSD**: 可以，性价比高
- **NVMe SSD**: 最佳，训练速度快

---

### 5. 网络要求

#### 带宽需求
```
数据下载:     1GB/小时  (爬取 Pinterest)
模型同步:     100MB/次  (上传到服务器)
API 请求:     10KB/次   (推荐请求)

最低: 10Mbps
推荐: 100Mbps
理想: 1Gbps
```

---


---

## Railway.app 部署方案（强烈推荐）⭐⭐⭐⭐⭐

### 为什么选择 Railway？

**官网**: https://railway.app/

Railway 是一个现代化的应用部署平台，特别适合 TFRS 推荐系统：

#### 核心优势
```
✅ 开发者友好: Git 推送即部署，零配置
✅ 免费额度: $5/月 免费额度
✅ 按用量付费: 只为实际使用付费，无需预付
✅ 自动扩展: 根据负载自动调整资源
✅ 内置服务: PostgreSQL, Redis, MongoDB 等
✅ 简单易用: 无需 DevOps 知识
✅ 全球 CDN: 自动优化访问速度
```

### Railway 定价

| 计划 | 价格 | 配置 | 适用场景 |
|------|------|------|---------|
| **Developer** | $0 (免费) | 512MB RAM, 0.5 vCPU, $5 额度 | 开发测试 |
| **Hobby** | $5/月起 | 8GB RAM, 8 vCPU, 按用量 | 小型生产 |
| **Pro** | $20/月起 | 32GB RAM, 32 vCPU, 无限 | 中大型生产 |

### TFRS 在 Railway 上的成本估算

#### 场景 1: 推理服务（24/7运行）
```
配置:
- RAM: 2GB
- CPU: 1 vCPU
- 存储: 5GB

月成本: 约 $10-15 (¥70-105)
```

#### 场景 2: 训练任务（按需运行）
```
配置:
- RAM: 8GB
- CPU: 4 vCPU
- 运行时间: 4小时/天

月成本: 约 $20-30 (¥140-210)
```

#### 总成本
```
推理 + 训练: $30-45/月 (¥210-315)

对比传统云:
- 阿里云: ¥1,200/月
- AWS: $542/月
- Railway: ¥210-315/月

节省: 75-80%！
```

### Railway 部署步骤

#### 1. 项目配置文件

```yaml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python -m src.serving.api"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "tfrs-api"
```

#### 2. Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "src.serving.api"]
```

#### 3. 部署命令

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 链接到 GitHub（推荐）
railway link

# 部署
railway up

# 查看日志
railway logs

# 查看服务状态
railway status

# 打开服务
railway open
```

#### 4. 环境变量配置

```bash
# 在 Railway Dashboard 或 CLI 设置
railway variables set MODEL_PATH=/app/models/saved_model
railway variables set API_KEY=your_secret_key
railway variables set LOG_LEVEL=INFO
```

### Railway vs 其他平台对比

| 平台 | 月成本 | 部署难度 | 自动扩展 | 免费额度 | 推荐度 |
|------|--------|---------|---------|---------|--------|
| **Railway** | ¥210-315 | ⭐ 极简 | ✅ | $5 | ⭐⭐⭐⭐⭐ |
| **Render** | ¥175-350 | ⭐⭐ 简单 | ✅ | 750小时 | ⭐⭐⭐⭐ |
| **Fly.io** | ¥150-300 | ⭐⭐⭐ 中等 | ✅ | 3个VM | ⭐⭐⭐⭐ |
| **Heroku** | ¥350-700 | ⭐⭐ 简单 | ✅ | 无 | ⭐⭐⭐ |
| **阿里云** | ¥1,200 | ⭐⭐⭐⭐ 复杂 | ❌ | 无 | ⭐⭐⭐ |
| **AWS** | $542 | ⭐⭐⭐⭐⭐ 很复杂 | ✅ | 12个月 | ⭐⭐ |

### Railway 最佳实践

#### 1. 使用 GitHub 自动部署
```bash
# 连接 GitHub 仓库
railway link

# 每次 push 自动部署
git push origin main
```

#### 2. 配置健康检查
```python
# src/serving/api.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tfrs-api"}
```

#### 3. 使用 Railway 数据库
```bash
# 添加 PostgreSQL
railway add postgresql

# 自动注入环境变量
# DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
```

#### 4. 监控和日志
```bash
# 实时日志
railway logs --follow

# 查看指标
railway metrics
```

### Railway 限制与注意事项

#### 限制
```
❌ 无 GPU 支持（训练需要在本地或 Colab）
❌ 最大 32GB RAM（大模型可能不够）
❌ 按用量计费（流量大时成本上升）
```

#### 解决方案
```
✅ 训练: 使用 Google Colab Pro
✅ 推理: 部署到 Railway
✅ 大模型: 模型量化或使用 TF Lite
✅ 成本控制: 设置预算告警
```

### 推荐架构

```
┌─────────────────────────────────────────┐
│  训练环境: Google Colab Pro             │
│  - GPU: T4/V100                         │
│  - 成本: $10/月                         │
│  - 用途: 模型训练                       │
└─────────────────────────────────────────┘
              │
              ↓ 导出模型
┌─────────────────────────────────────────┐
│  部署环境: Railway.app                  │
│  - CPU: 1-2 vCPU                        │
│  - RAM: 2-4GB                           │
│  - 成本: $10-20/月                      │
│  - 用途: API 推理服务                   │
└─────────────────────────────────────────┘
              │
              ↓ 提供 API
┌─────────────────────────────────────────┐
│  前端: Cloudflare Workers               │
│  - 调用 Railway API                     │
│  - 全球 CDN 加速                        │
│  - 成本: 免费                           │
└─────────────────────────────────────────┘

总成本: $20-30/月 (¥140-210)
```

## 成本优化方案

### 方案 A: 按需付费（推荐）⭐⭐⭐⭐⭐

```
训练时: 使用 GPU 实例 (¥7/小时)
推理时: 使用 CPU 实例 (¥0.5/小时)

月成本估算:
- 训练: 4小时/天 × 30天 × ¥7 = ¥840
- 推理: 24小时/天 × 30天 × ¥0.5 = ¥360
总计: ¥1,200/月
```

### 方案 B: 竞价实例（最便宜）⭐⭐⭐⭐⭐

```
使用云服务商的竞价实例（Spot Instance）
价格: 正常价格的 20-30%

例如:
- AWS Spot: T4 实例 $0.15/小时 (原价 $0.75)
- 阿里云抢占式: ¥1.5/小时 (原价 ¥7.34)

月成本: ¥450-600
```

### 方案 C: 本地服务器（长期最划算）⭐⭐⭐⭐

```
购买配置:
- CPU: AMD Ryzen 9 5900X (¥2,500)
- 内存: 64GB DDR4 (¥1,500)
- GPU: RTX 3090 24GB (¥12,000)
- 主板+电源+机箱: (¥3,000)
- 存储: 1TB NVMe (¥800)

总计: ¥19,800

回本周期: 19,800 / 1,200 = 16.5个月
```

### 方案 D: Colab/Kaggle（免费）⭐⭐⭐

```
Google Colab Pro:
- GPU: T4 或 V100
- 价格: $9.99/月
- 限制: 每次最多 12小时

Kaggle:
- GPU: P100
- 价格: 免费
- 限制: 每周 30小时

适合: 学习、原型开发
```

---

## 推荐配置总结

### 预算 < ¥500/月
```
方案: Google Colab Pro + 阿里云 CPU 实例
- 训练: Colab ($10/月)
- 推理: 阿里云 2核4GB (¥200/月)
总计: ¥280/月
```

### 预算 ¥500-2000/月
```
方案: 阿里云按需付费
- 训练: GPU 实例 4小时/天
- 推理: CPU 实例 24小时
总计: ¥1,200/月
```

### 预算 ¥2000-5000/月
```
方案: 阿里云包年包月
- 实例: ecs.gn6i-c8g1.2xlarge (T4)
- 配置: 8核32GB + T4 GPU
总计: ¥4,896/月
```

### 预算 > ¥20,000
```
方案: 购买本地服务器
- 一次性投入: ¥20,000
- 电费: ¥200/月
- 16个月回本
```

---

## 快速决策表

| 数据规模 | 用户量 | 推荐配置 | 月成本 |
|---------|--------|---------|--------|
| < 1万 | < 1000 | Colab + 小型CPU | ¥300 |
| 1-10万 | 1000-1万 | 按需GPU + CPU | ¥1,200 |
| 10-100万 | 1-10万 | T4 GPU 实例 | ¥5,000 |
| > 100万 | > 10万 | V100/A100 实例 | ¥20,000 |

---

## 开始建议

**第1个月**: 使用 Google Colab Pro ($10) 进行原型开发和测试

**第2-3个月**: 如果效果好，升级到阿里云按需付费 (¥1,200/月)

**第4个月+**: 根据实际规模决定是否购买本地服务器或升级云实例

---

**总结**: 对于 ManiDala 项目，建议从 **Colab Pro + 小型 CPU 实例** 开始，成本仅 ¥300/月，足够完成原型开发和初期测试。