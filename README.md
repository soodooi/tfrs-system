# TFRS 推荐系统

基于 TensorFlow Recommenders 的深度学习推荐系统，为 Manidala 电商平台提供个性化产品推荐。

## 🎯 项目概述

这是一个完整的推荐系统解决方案，包括：
- **训练环境**：Google Colab 笔记本（GPU 加速）
- **部署环境**：Railway.app（自动扩展）
- **API 服务**：FastAPI（高性能异步）
- **推荐算法**：双塔模型、深度交叉网络

## 📦 项目结构

```
tfrs-system/
├── src/
│   ├── serving/
│   │   └── api.py              # FastAPI 服务（318行）
│   └── __init__.py
├── notebooks/
│   └── TFRS_Training_Colab.ipynb  # Colab 训练笔记本
├── models/                     # 训练好的模型（需要生成）
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 配置
├── railway.toml               # Railway 部署配置
├── .env.example               # 环境变量模板
├── QUICK-START.md             # 5分钟快速开始
├── SERVER-REQUIREMENTS.md     # 服务器需求详解
├── GITHUB-PUSH-GUIDE.md       # GitHub 推送指南
├── NETWORK-TROUBLESHOOTING.md # 网络问题解决
└── push-to-github.bat         # 自动推送脚本

```

## 🚀 快速开始

### 1. 训练模型（Google Colab）

1. 打开 Colab 笔记本：
   ```
   notebooks/TFRS_Training_Colab.ipynb
   ```

2. 点击 "在 Colab 中打开"

3. 运行所有单元格（约 2-4 小时）

4. 下载训练好的模型到 `models/` 目录

### 2. 部署到 Railway

1. 访问 [Railway.app](https://railway.app/)

2. 连接 GitHub 仓库：`soodooi/tfrs-system`

3. Railway 会自动：
   - 检测 `Dockerfile`
   - 构建镜像
   - 部署服务
   - 分配域名

4. 配置环境变量：
   ```
   API_KEY=your-secret-key
   MODEL_PATH=/app/models
   ```

### 3. 测试 API

```bash
# 健康检查
curl https://your-app.railway.app/health

# 获取推荐
curl -X POST https://your-app.railway.app/recommend \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "limit": 10}'
```

## 📚 详细文档

- **[QUICK-START.md](QUICK-START.md)** - 5分钟快速开始指南
- **[SERVER-REQUIREMENTS.md](SERVER-REQUIREMENTS.md)** - 服务器需求和成本分析
- **[GITHUB-PUSH-GUIDE.md](GITHUB-PUSH-GUIDE.md)** - GitHub 推送详细指南
- **[NETWORK-TROUBLESHOOTING.md](NETWORK-TROUBLESHOOTING.md)** - 网络问题解决方案

## 🔌 API 端点

### 1. 健康检查
```http
GET /health
```

### 2. 单用户推荐
```http
POST /recommend
Content-Type: application/json
X-API-Key: your-secret-key

{
  "user_id": "user123",
  "limit": 10,
  "exclude_items": ["item1", "item2"]
}
```

### 3. 批量推荐
```http
POST /recommend/batch
Content-Type: application/json
X-API-Key: your-secret-key

{
  "user_ids": ["user1", "user2", "user3"],
  "limit": 10
}
```

### 4. 相似商品推荐
```http
POST /recommend/similar
Content-Type: application/json
X-API-Key: your-secret-key

{
  "item_id": "item123",
  "limit": 10
}
```

### 5. 热门商品
```http
GET /recommend/popular?limit=20
X-API-Key: your-secret-key
```

### 6. 模型信息
```http
GET /model/info
X-API-Key: your-secret-key
```

## 💰 成本估算

### 训练成本（Google Colab）
- **Colab Pro**: $10/月
- **GPU 使用**: 包含在订阅中
- **训练频率**: 每周 1-2 次

### 部署成本（Railway）
- **Starter Plan**: $5/月（500小时）
- **Developer Plan**: $10/月（无限制）
- **预估**: $10-20/月

### 总成本
- **月成本**: $20-30（¥140-210）
- **比传统云便宜**: 75-80%

## 🛠️ 技术栈

- **深度学习**: TensorFlow 2.15, TensorFlow Recommenders 0.7.3
- **API 框架**: FastAPI, Uvicorn
- **容器化**: Docker
- **部署平台**: Railway (PaaS)
- **训练平台**: Google Colab (GPU)

## 📊 推荐策略

系统采用混合推荐策略：
- **个性化推荐**: 40%（基于用户历史）
- **热门推荐**: 25%（基于全局热度）
- **相似推荐**: 20%（基于商品相似度）
- **探索推荐**: 15%（新品和冷门商品）

## 🔐 安全性

- API Key 认证
- HTTPS 加密传输
- 环境变量管理敏感信息
- 请求频率限制

## 📈 性能指标

- **响应时间**: < 100ms（单次推荐）
- **吞吐量**: 1000+ QPS
- **模型大小**: ~50MB
- **内存占用**: ~512MB

## 🔄 更新模型

1. 在 Colab 重新训练模型
2. 下载新模型文件
3. 上传到 Railway 或使用 CI/CD
4. 重启服务（自动加载新模型）

## 🐛 故障排查

### 推送到 GitHub 失败
运行自动推送脚本：
```bash
cd recommend/tfrs-system
push-to-github.bat
```

或查看 [NETWORK-TROUBLESHOOTING.md](NETWORK-TROUBLESHOOTING.md)

### Railway 部署失败
1. 检查 Dockerfile 语法
2. 确认 requirements.txt 依赖
3. 查看 Railway 构建日志

### API 返回错误
1. 检查模型文件是否存在
2. 验证 API Key
3. 查看服务日志

## 📞 支持

- **GitHub Issues**: https://github.com/soodooi/tfrs-system/issues
- **文档**: 查看项目中的 Markdown 文件
- **示例**: 参考 Colab 笔记本

## 📄 许可证

MIT License

## 🎉 致谢

- TensorFlow Recommenders 团队
- Railway.app 平台
- Google Colab 服务

---

**项目状态**: ✅ 已推送到 GitHub  
**仓库地址**: https://github.com/soodooi/tfrs-system  
**代理端口**: 7890（已配置）