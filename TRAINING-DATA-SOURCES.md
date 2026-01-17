# 训练数据源完整列表

## 公开数据集（推荐用于训练）

### 1. MovieLens（电影推荐）
**最推荐 - 已集成到笔记本**
- **100K**: 10万条评分，943用户，1682电影
- **1M**: 100万条评分，6040用户，3706电影
- **10M**: 1000万条评分，71567用户，10681电影
- **25M**: 2500万条评分，162541用户，62423电影
- **下载**: TensorFlow Datasets 自动下载
- **格式**: user_id, movie_id, rating, timestamp
- **许可**: 免费用于研究和教育

```python
import tensorflow_datasets as tfds
ratings = tfds.load("movielens/100k-ratings", split="train")
```

### 2. Amazon Product Reviews（电商推荐）
**最适合电商场景**
- **规模**: 2.33亿条评论，涵盖29个品类
- **品类**: 电子产品、服装、家居、图书等
- **包含**: user_id, product_id, rating, review_text, timestamp
- **下载**: https://nijianmo.github.io/amazon/index.html
- **许可**: 学术研究免费

**推荐子集**：
- Electronics: 2000万条（最相关）
- Clothing: 1100万条
- Home & Kitchen: 2100万条
- Books: 5100万条

```python
# 下载示例
!wget https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_v2/categoryFiles/Electronics.json.gz
```

### 3. Taobao User Behavior（淘宝用户行为）
**中国电商数据**
- **规模**: 100万用户，400万商品，1亿条行为
- **行为**: 点击、收藏、加购、购买
- **时间**: 2017年11月25日 - 12月3日
- **下载**: https://tianchi.aliyun.com/dataset/649
- **许可**: 天池平台免费

```python
# 数据格式
user_id, item_id, category_id, behavior_type, timestamp
```

### 4. Retail Rocket（电商推荐）
**真实电商数据**
- **规模**: 140万用户，23万商品，260万次交互
- **行为**: 浏览、加购、购买
- **下载**: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
- **许可**: Kaggle 公开数据集

### 5. H&M Personalized Fashion（时尚推荐）
**服装电商**
- **规模**: 130万用户，10.5万商品，3100万次购买
- **包含**: 商品图片、描述、用户年龄
- **下载**: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
- **许可**: Kaggle 竞赛数据

### 6. Yelp Dataset（餐厅/服务推荐）
- **规模**: 700万条评论，15万商家
- **包含**: 评分、评论文本、商家信息
- **下载**: https://www.yelp.com/dataset
- **许可**: 学术研究免费

### 7. Last.fm（音乐推荐）
- **规模**: 36万用户，29万艺术家，1700万次播放
- **下载**: http://www.dtic.upf.edu/~ocelma/MusicRecommendationDataset/
- **许可**: 研究使用免费

### 8. Book-Crossing（图书推荐）
- **规模**: 27万用户，27万图书，110万条评分
- **下载**: http://www2.informatik.uni-freiburg.de/~cziegler/BX/
- **许可**: 公开数据集

## 合成数据生成

### 方案 1: 笔记本内置生成器
```python
import numpy as np
import pandas as pd

# 生成 10万条模拟数据
n_users = 1000
n_items = 5000
n_interactions = 100000

data = {
    'user_id': np.random.randint(0, n_users, n_interactions),
    'item_id': np.random.randint(0, n_items, n_interactions),
    'rating': np.random.randint(1, 6, n_interactions),
    'timestamp': np.random.randint(1600000000, 1700000000, n_interactions)
}
df = pd.DataFrame(data)
```

### 方案 2: 基于规则的生成
```python
# 模拟用户偏好
user_preferences = {
    'user_1': ['electronics', 'books'],
    'user_2': ['clothing', 'home'],
}

# 生成符合偏好的交互数据
```

## 您的真实数据

### 数据格式要求
```csv
user_id,item_id,timestamp,rating,behavior_type
user_001,prod_123,1642435200,5,purchase
user_002,prod_456,1642435300,4,view
user_001,prod_789,1642435400,5,add_to_cart
```

### 最小数据量建议
- **测试**: 1万条（快速验证）
- **开发**: 10万条（基本效果）
- **生产**: 100万条+（良好效果）

### 数据收集来源
1. **用户行为日志**: 浏览、点击、收藏、购买
2. **订单数据**: 购买记录、评分
3. **搜索日志**: 搜索关键词、点击商品
4. **推荐反馈**: 推荐展示、点击率

## 数据集对比

| 数据集 | 规模 | 场景 | 推荐度 | 下载难度 |
|--------|------|------|--------|----------|
| MovieLens 100K | 10万 | 通用 | ⭐⭐⭐⭐⭐ | 极易 |
| Amazon Reviews | 2.3亿 | 电商 | ⭐⭐⭐⭐⭐ | 中等 |
| Taobao Behavior | 1亿 | 电商 | ⭐⭐⭐⭐⭐ | 中等 |
| H&M Fashion | 3100万 | 时尚 | ⭐⭐⭐⭐ | 易 |
| Retail Rocket | 260万 | 电商 | ⭐⭐⭐⭐ | 易 |
| Yelp | 700万 | 服务 | ⭐⭐⭐ | 中等 |
| Last.fm | 1700万 | 音乐 | ⭐⭐⭐ | 易 |
| 合成数据 | 自定义 | 测试 | ⭐⭐ | 极易 |

## 推荐使用策略

### 阶段 1: 快速验证（1-2天）
使用 **MovieLens 100K**
- 已集成到笔记本
- 无需下载配置
- 快速验证流程

### 阶段 2: 场景适配（1周）
使用 **Amazon Reviews** 或 **Taobao Behavior**
- 更接近电商场景
- 数据量充足
- 训练效果更好

### 阶段 3: 生产部署（持续）
使用 **您的真实数据**
- 最符合业务场景
- 持续收集和更新
- 最佳推荐效果

## 数据预处理

### 通用预处理步骤
```python
import pandas as pd

# 1. 加载数据
df = pd.read_csv('data.csv')

# 2. 去重
df = df.drop_duplicates(['user_id', 'item_id', 'timestamp'])

# 3. 过滤低频用户/商品
user_counts = df['user_id'].value_counts()
item_counts = df['item_id'].value_counts()
df = df[df['user_id'].isin(user_counts[user_counts >= 5].index)]
df = df[df['item_id'].isin(item_counts[item_counts >= 5].index)]

# 4. 时间排序
df = df.sort_values('timestamp')

# 5. 划分训练/测试集（80/20）
split_idx = int(len(df) * 0.8)
train_df = df[:split_idx]
test_df = df[split_idx:]
```

## 数据增强技巧

### 1. 负采样
```python
# 为每个正样本生成 4 个负样本
negative_samples = generate_negative_samples(positive_samples, ratio=4)
```

### 2. 时间加权
```python
# 最近的交互权重更高
df['weight'] = np.exp((df['timestamp'] - df['timestamp'].min()) / time_decay)
```

### 3. 隐式反馈转换
```python
# 将浏览、点击转换为隐式评分
df['implicit_rating'] = df['behavior_type'].map({
    'view': 1,
    'add_to_cart': 3,
    'purchase': 5
})
```

## 法律和道德考虑

### ✅ 可以使用
- 公开数据集（标注为研究/教育用途）
- 自己收集的数据（有用户授权）
- 合成/模拟数据

### ❌ 不能使用
- 爬取的未授权数据
- 包含个人隐私的数据
- 违反平台服务条款的数据

## 下一步

1. **选择数据集**: 根据场景选择合适的数据集
2. **下载数据**: 使用提供的链接下载
3. **预处理**: 按照格式要求处理数据
4. **上传 Colab**: 上传到 Colab 进行训练
5. **训练模型**: 运行笔记本开始训练

详细训练步骤见 [`COLAB-TRAINING-GUIDE.md`](COLAB-TRAINING-GUIDE.md)