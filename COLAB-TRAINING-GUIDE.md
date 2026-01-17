# Colab 训练指南

## 训练数据来源

### 方案 1: MovieLens 公开数据集（推荐用于测试）
- **数据集**: MovieLens 100K
- **包含**: 10万条用户-电影评分记录
- **优点**: 免费、合法、即开即用
- **用途**: 测试模型、验证流程

### 方案 2: 合成数据（快速验证）
- **生成**: 笔记本自动生成模拟数据
- **包含**: 用户ID、商品ID、交互记录
- **优点**: 无需下载、快速启动
- **用途**: 快速测试、开发调试

### 方案 3: 您的真实数据（生产环境）
需要准备 CSV 文件，格式：
```csv
user_id,item_id,timestamp,rating
user1,item123,1642435200,5
user2,item456,1642435300,4
```

上传到 Colab 后加载。

## 训练步骤

### 1. 打开笔记本
访问 GitHub 仓库：
```
https://github.com/soodooi/tfrs-system/blob/main/notebooks/TFRS_Training_Colab.ipynb
```

点击 "Open in Colab" 按钮

### 2. 选择 GPU
- 点击 "运行时" → "更改运行时类型"
- 硬件加速器：选择 "GPU"
- GPU 类型：T4（免费）或 A100（Pro）
- 点击 "保存"

### 3. 运行单元格
按顺序运行每个单元格（Shift+Enter）：

#### 单元格 1: 环境设置（1分钟）
```python
# 安装依赖
!pip install tensorflow==2.15.0
!pip install tensorflow-recommenders==0.7.3
```
显示：安装进度条

#### 单元格 2: 数据准备（2分钟）
```python
# 加载 MovieLens 数据
import tensorflow_datasets as tfds
ratings = tfds.load("movielens/100k-ratings", split="train")
```
显示：下载进度、数据样本

#### 单元格 3: 数据预处理（1分钟）
```python
# 处理数据
ratings = ratings.map(lambda x: {
    "user_id": x["user_id"],
    "movie_id": x["movie_title"]
})
```
显示：处理进度

#### 单元格 4: 构建模型（30秒）
```python
# 创建双塔模型
class TwoTowerModel(tfrs.Model):
    ...
```
显示：模型结构

#### 单元格 5: 训练模型（30-120分钟）
```python
# 训练
model.fit(train_dataset, epochs=10)
```

**训练进度显示**：
```
Epoch 1/10
━━━━━━━━━━━━━━━━━━━━ 1234/1234 [02:15<00:00, 9.12it/s]
loss: 0.8234 - factorized_top_k/top_100_categorical_accuracy: 0.0234

Epoch 2/10
━━━━━━━━━━━━━━━━━━━━ 1234/1234 [02:10<00:00, 9.45it/s]
loss: 0.6543 - factorized_top_k/top_100_categorical_accuracy: 0.0456
```

**关键指标**：
- `loss`: 损失值（越小越好，目标 < 0.5）
- `accuracy`: 准确率（越大越好，目标 > 0.05）
- `it/s`: 每秒迭代数（GPU 约 8-10）

#### 单元格 6: 评估模型（5分钟）
```python
# 评估
metrics = model.evaluate(test_dataset)
```
显示：测试集指标

#### 单元格 7: 导出模型（1分钟）
```python
# 保存模型
model.save("/content/saved_model")
```
显示：保存路径

#### 单元格 8: 下载模型（1分钟）
```python
# 打包下载
!zip -r model.zip /content/saved_model
from google.colab import files
files.download('model.zip')
```
显示：下载链接

## 查看训练进度

### 实时监控
Colab 会实时显示：
- ✅ 当前 Epoch（如 3/10）
- ✅ 进度条（如 ━━━━━━━━ 45%）
- ✅ 剩余时间（如 ETA: 1:23:45）
- ✅ 损失值变化
- ✅ 准确率变化

### TensorBoard（可选）
在训练单元格前添加：
```python
%load_ext tensorboard
%tensorboard --logdir logs
```

会显示：
- 损失曲线图
- 准确率曲线图
- 学习率变化
- 训练速度

### 训练时间估算

| GPU 类型 | 数据量 | 预计时间 |
|---------|--------|---------|
| T4（免费） | 10万条 | 30-60分钟 |
| T4（免费） | 100万条 | 2-4小时 |
| A100（Pro） | 10万条 | 10-20分钟 |
| A100（Pro） | 100万条 | 30-60分钟 |

## 常见问题

### Q: 训练中断了怎么办？
A: Colab 会自动保存检查点，重新运行训练单元格会从断点继续。

### Q: 如何使用自己的数据？
A: 修改数据加载单元格：
```python
# 上传 CSV
from google.colab import files
uploaded = files.upload()

# 加载数据
import pandas as pd
df = pd.read_csv('your_data.csv')
```

### Q: 训练太慢怎么办？
A: 
1. 升级到 Colab Pro（$10/月，A100 GPU）
2. 减少数据量（采样）
3. 减少 epochs（如 10 → 5）
4. 减少 batch_size

### Q: 内存不足怎么办？
A:
```python
# 减少 batch size
train_dataset = train_dataset.batch(256)  # 原来 512

# 或使用数据采样
ratings = ratings.take(50000)  # 只用 5万条
```

## 训练完成后

### 1. 验证模型
```python
# 测试推荐
user_id = "42"
scores, titles = model({"user_id": [user_id]})
print(f"Top 10 recommendations for user {user_id}:")
for title, score in zip(titles[0][:10], scores[0][:10]):
    print(f"  {title.numpy().decode('utf-8')}: {score.numpy():.4f}")
```

### 2. 下载模型
模型会自动下载为 `model.zip`（约 50MB）

### 3. 上传到 Railway
解压后上传到 Railway 项目的 `models/` 目录

## 下一步
模型训练完成后，参考 [`QUICK-START.md`](QUICK-START.md) 部署到 Railway。