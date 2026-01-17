# 模型训练验证指南

## 如何检查 Colab 训练状态

### 1. 打开 Colab 笔记本
访问：https://github.com/soodooi/tfrs-system/blob/main/notebooks/TFRS_Training_Colab.ipynb

点击 "Open in Colab" 按钮

### 2. 检查训练是否完成

#### 训练中的标志
```
Epoch 3/10
━━━━━━━━━━━━━━━━━━━━ 1234/1234 [02:15<00:00, 9.12it/s]
loss: 0.6543 - accuracy: 0.0456
```

#### 训练完成的标志
```
Epoch 10/10
━━━━━━━━━━━━━━━━━━━━ 1234/1234 [02:10<00:00, 9.45it/s]
loss: 0.3421 - accuracy: 0.0823

Training completed!
Model saved to: /content/saved_model
```

### 3. 验证模型文件

在 Colab 中运行：
```python
import os

# 检查模型目录
model_path = "/content/saved_model"
if os.path.exists(model_path):
    print("✓ 模型目录存在")
    
    # 列出文件
    for root, dirs, files in os.walk(model_path):
        level = root.replace(model_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_size = os.path.getsize(os.path.join(root, file))
            print(f'{subindent}{file} ({file_size / 1024 / 1024:.2f} MB)')
else:
    print("✗ 模型目录不存在，训练可能未完成")
```

**预期输出**：
```
✓ 模型目录存在
saved_model/
  saved_model.pb (2.34 MB)
  variables/
    variables.data-00000-of-00001 (45.67 MB)
    variables.index (0.01 MB)
  assets/
```

### 4. 测试模型推理

```python
import tensorflow as tf

# 加载模型
model = tf.saved_model.load("/content/saved_model")

# 测试推荐
user_id = "42"
recommendations = model({"user_id": [user_id]})

print(f"为用户 {user_id} 推荐的商品：")
for i, (item_id, score) in enumerate(zip(recommendations[0][:10], recommendations[1][:10])):
    print(f"{i+1}. {item_id.numpy().decode('utf-8')}: {score.numpy():.4f}")
```

**预期输出**：
```
为用户 42 推荐的商品：
1. item_123: 0.9234
2. item_456: 0.8765
3. item_789: 0.8432
...
```

### 5. 检查训练指标

#### 良好的训练指标
- **Loss（损失）**: 
  - 初始：0.8-1.0
  - 最终：< 0.5（越小越好）
  - 趋势：持续下降

- **Accuracy（准确率）**:
  - 初始：0.01-0.03
  - 最终：> 0.05（越大越好）
  - 趋势：持续上升

- **训练时间**:
  - T4 GPU: 30-60分钟（10万条数据）
  - A100 GPU: 10-20分钟（10万条数据）

#### 问题指标
- ❌ Loss 不下降或上升
- ❌ Accuracy 始终很低（< 0.01）
- ❌ 训练速度很慢（< 1 it/s）
- ❌ 内存溢出错误

### 6. 下载模型

训练完成后，运行：
```python
# 打包模型
!zip -r model.zip /content/saved_model

# 下载
from google.colab import files
files.download('model.zip')
```

**预期文件大小**: 40-60 MB

### 7. 验证下载的模型

解压后检查：
```
model.zip
└── saved_model/
    ├── saved_model.pb (2-5 MB)
    ├── variables/
    │   ├── variables.data-00000-of-00001 (40-50 MB)
    │   └── variables.index (< 1 MB)
    └── assets/ (可能为空)
```

## 常见问题排查

### Q1: 训练一直卡在某个 Epoch
**原因**: 数据量太大或 batch size 太小
**解决**:
```python
# 减少数据量
ratings = ratings.take(50000)  # 只用 5万条

# 增加 batch size
train_dataset = train_dataset.batch(512)  # 原来 256
```

### Q2: 内存不足 (OOM)
**原因**: 模型太大或数据太多
**解决**:
```python
# 减少 embedding 维度
embedding_dimension = 32  # 原来 64

# 减少数据
ratings = ratings.take(10000)
```

### Q3: Loss 不下降
**原因**: 学习率太高或数据质量差
**解决**:
```python
# 降低学习率
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)  # 原来 0.01

# 增加训练轮数
model.fit(train_dataset, epochs=20)  # 原来 10
```

### Q4: 训练速度很慢
**原因**: 没有使用 GPU
**解决**:
1. 点击 "运行时" → "更改运行时类型"
2. 硬件加速器：选择 "GPU"
3. 重新运行所有单元格

验证 GPU：
```python
import tensorflow as tf
print("GPU 可用:", tf.config.list_physical_devices('GPU'))
```

### Q5: 模型文件不存在
**原因**: 训练未完成或保存失败
**解决**:
```python
# 手动保存
model.save("/content/saved_model")

# 检查是否成功
import os
print(os.path.exists("/content/saved_model"))
```

## 模型质量评估

### 基本评估
```python
# 在测试集上评估
test_metrics = model.evaluate(test_dataset, return_dict=True)
print("测试集指标:")
for metric, value in test_metrics.items():
    print(f"  {metric}: {value:.4f}")
```

### 推荐质量评估
```python
# 为多个用户生成推荐
test_users = ["1", "10", "100", "1000"]
for user_id in test_users:
    recs = model({"user_id": [user_id]})
    print(f"\n用户 {user_id} 的推荐:")
    for item, score in zip(recs[0][:5], recs[1][:5]):
        print(f"  {item.numpy().decode('utf-8')}: {score.numpy():.4f}")
```

### 多样性评估
```python
# 检查推荐的多样性
all_recommendations = []
for user_id in range(100):
    recs = model({"user_id": [str(user_id)]})
    all_recommendations.extend([r.numpy().decode('utf-8') for r in recs[0][:10]])

unique_items = len(set(all_recommendations))
total_items = len(all_recommendations)
diversity = unique_items / total_items

print(f"推荐多样性: {diversity:.2%}")
print(f"独特商品数: {unique_items}")
print(f"总推荐数: {total_items}")
```

**良好的多样性**: > 30%

## 下一步

### 如果训练成功
1. 下载模型文件（model.zip）
2. 上传到 Railway 项目
3. 部署 API 服务
4. 测试推荐功能

### 如果训练失败
1. 检查错误信息
2. 参考上面的问题排查
3. 调整参数重新训练
4. 或使用更小的数据集测试

## 需要帮助？

如果遇到问题，提供以下信息：
1. 错误信息截图
2. 训练日志（最后几行）
3. 使用的数据集和大小
4. GPU 类型（T4/A100）
5. 训练参数（epochs, batch_size 等）

---

**提示**: 第一次训练建议使用 MovieLens 100K 数据集（10万条），训练时间约 30-60 分钟，成功率最高。