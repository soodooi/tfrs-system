# GitHub 推送指南

## 方法 1: 使用 GitHub 网页创建仓库（推荐，最简单）

### 步骤 1: 在 GitHub 创建仓库

1. 访问：https://github.com/new
2. 填写信息：
   - Repository name: `tfrs-system`
   - Description: `TFRS recommendation system with TensorFlow Recommenders`
   - 选择：Public
   - **不要**勾选 "Initialize this repository with a README"
3. 点击 "Create repository"

### 步骤 2: 复制仓库 URL

创建后，GitHub 会显示仓库 URL，类似：
```
https://github.com/soodooi/tfrs-system.git
```

### 步骤 3: 在终端推送代码

打开终端（在 VSCode 中按 Ctrl+`），然后运行：

```bash
cd recommend/tfrs-system

# 添加远程仓库
git remote add origin https://github.com/soodooi/tfrs-system.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 4: 输入凭据

Git 会提示输入：
- Username: `soodooi`
- Password: **这里需要输入 Personal Access Token（不是密码）**

---

## 创建 Personal Access Token

### 步骤 1: 访问 Token 设置页面

访问：https://github.com/settings/tokens

或者：
1. 点击右上角头像
2. Settings
3. 左侧菜单最下方：Developer settings
4. Personal access tokens → Tokens (classic)

### 步骤 2: 生成新 Token

1. 点击 "Generate new token" → "Generate new token (classic)"
2. 填写信息：
   - Note: `TFRS System Push` （备注名称）
   - Expiration: `90 days` （有效期）
   - 勾选权限：
     - ✅ `repo` （完整的仓库访问权限）
3. 滚动到底部，点击 "Generate token"

### 步骤 3: 复制 Token

⚠️ **重要**：Token 只显示一次，请立即复制保存！

Token 格式类似：
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 步骤 4: 使用 Token 推送

回到终端，当提示输入密码时，粘贴 Token（不是 GitHub 密码）

```bash
Username: soodooi
Password: [粘贴你的 token]
```

---

## 方法 2: 使用 SSH（更安全，推荐长期使用）

### 步骤 1: 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

按 Enter 使用默认路径，可以设置密码或直接 Enter 跳过。

### 步骤 2: 复制公钥

```bash
# Windows
type %USERPROFILE%\.ssh\id_ed25519.pub

# Mac/Linux
cat ~/.ssh/id_ed25519.pub
```

复制输出的内容（以 `ssh-ed25519` 开头）

### 步骤 3: 添加到 GitHub

1. 访问：https://github.com/settings/keys
2. 点击 "New SSH key"
3. Title: `My Computer`
4. Key: 粘贴刚才复制的公钥
5. 点击 "Add SSH key"

### 步骤 4: 使用 SSH 推送

```bash
cd recommend/tfrs-system

# 使用 SSH URL
git remote add origin git@github.com:soodooi/tfrs-system.git

git branch -M main
git push -u origin main
```

---

## 验证推送成功

推送成功后，访问：
```
https://github.com/soodooi/tfrs-system
```

您应该能看到所有文件：
- ✅ Dockerfile
- ✅ requirements.txt
- ✅ src/serving/api.py
- ✅ notebooks/TFRS_Training_Colab.ipynb
- ✅ 等等...

---

## 常见问题

### Q1: 推送时提示 "Permission denied"

**原因**: Token 权限不足或已过期

**解决**: 重新生成 Token，确保勾选 `repo` 权限

### Q2: 推送时提示 "remote: Repository not found"

**原因**: 仓库 URL 错误或仓库不存在

**解决**: 
1. 确认仓库已在 GitHub 创建
2. 检查 URL 是否正确：`git remote -v`
3. 如果错误，删除并重新添加：
   ```bash
   git remote remove origin
   git remote add origin https://github.com/soodooi/tfrs-system.git
   ```

### Q3: 推送时提示 "Updates were rejected"

**原因**: 远程仓库有本地没有的提交

**解决**:
```bash
git pull origin main --rebase
git push origin main
```

---

## 推送成功后的下一步

1. ✅ 在 Railway 部署
   - 访问：https://railway.app/
   - New Project → Deploy from GitHub repo
   - 选择 `tfrs-system`

2. ✅ 在 Colab 训练模型
   - 打开：`notebooks/TFRS_Training_Colab.ipynb`
   - 运行全部

3. ✅ 测试 API
   - 访问 Railway 提供的 URL
   - 测试推荐接口

---

**需要帮助？** 如果遇到问题，请告诉我具体的错误信息。