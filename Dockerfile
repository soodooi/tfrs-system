# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（只安装推理需要的）
RUN pip install --no-cache-dir \
    tensorflow==2.15.0 \
    tensorflow-recommenders==0.7.3 \
    fastapi==0.108.0 \
    uvicorn[standard]==0.25.0 \
    pydantic==2.5.3 \
    numpy==1.26.2 \
    pandas==2.1.4 \
    python-dotenv==1.0.0

# 复制项目文件
COPY . .

# 创建模型目录
RUN mkdir -p /app/models/saved_models

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "src.serving.api:app", "--host", "0.0.0.0", "--port", "8000"]