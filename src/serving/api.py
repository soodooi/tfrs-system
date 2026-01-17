"""
FastAPI 推荐服务
提供 RESTful API 接口
"""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="TFRS Recommendation API",
    description="基于 TensorFlow Recommenders 的推荐系统 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量：模型
model = None
MODEL_PATH = os.getenv("MODEL_PATH", "./models/saved_models/two_tower")


# ============================================
# 数据模型
# ============================================

class RecommendRequest(BaseModel):
    """推荐请求"""
    user_id: str
    top_k: int = 10
    exclude_ids: Optional[List[str]] = None
    context: Optional[dict] = None


class RecommendResponse(BaseModel):
    """推荐响应"""
    user_id: str
    recommendations: List[dict]
    total: int
    model_version: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    service: str
    model_loaded: bool
    version: str


# ============================================
# 模型加载
# ============================================

def load_model():
    """加载训练好的模型"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            logger.info(f"Loading model from {MODEL_PATH}")
            model = tf.saved_model.load(MODEL_PATH)
            logger.info("Model loaded successfully")
            return True
        else:
            logger.warning(f"Model not found at {MODEL_PATH}")
            return False
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """应用启动时加载模型"""
    logger.info("Starting TFRS Recommendation API...")
    load_model()


# ============================================
# API 端点
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "service": "TFRS Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "recommend": "/api/recommend",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy" if model is not None else "degraded",
        service="tfrs-api",
        model_loaded=model is not None,
        version="1.0.0"
    )


@app.post("/api/recommend", response_model=RecommendResponse, tags=["Recommendation"])
async def recommend(
    request: RecommendRequest,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    获取推荐结果
    
    Args:
        request: 推荐请求
        api_key: API 密钥（可选）
    
    Returns:
        推荐结果列表
    """
    # API 密钥验证（可选）
    expected_api_key = os.getenv("API_KEY")
    if expected_api_key and api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # 检查模型是否加载
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        # 调用模型进行推荐
        # 注意：这里需要根据实际模型接口调整
        logger.info(f"Generating recommendations for user: {request.user_id}")
        
        # 模拟推荐结果（实际应该调用模型）
        # TODO: 替换为真实的模型推理逻辑
        recommendations = generate_mock_recommendations(
            request.user_id,
            request.top_k,
            request.exclude_ids
        )
        
        return RecommendResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            total=len(recommendations),
            model_version="v1.0"
        )
        
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommend/{user_id}", tags=["Recommendation"])
async def recommend_get(
    user_id: str,
    top_k: int = 10,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    GET 方式获取推荐（简化版）
    """
    request = RecommendRequest(user_id=user_id, top_k=top_k)
    return await recommend(request, api_key)


@app.post("/api/batch-recommend", tags=["Recommendation"])
async def batch_recommend(
    user_ids: List[str],
    top_k: int = 10,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    批量推荐
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        results = []
        for user_id in user_ids:
            recommendations = generate_mock_recommendations(user_id, top_k)
            results.append({
                "user_id": user_id,
                "recommendations": recommendations
            })
        
        return {
            "total_users": len(user_ids),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/similar/{item_id}", tags=["Recommendation"])
async def similar_items(
    item_id: str,
    top_k: int = 10,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    获取相似商品
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # TODO: 实现相似商品推荐逻辑
        similar = generate_mock_similar_items(item_id, top_k)
        
        return {
            "item_id": item_id,
            "similar_items": similar,
            "total": len(similar)
        }
        
    except Exception as e:
        logger.error(f"Similar items failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 辅助函数
# ============================================

def generate_mock_recommendations(
    user_id: str,
    top_k: int,
    exclude_ids: Optional[List[str]] = None
) -> List[dict]:
    """
    生成模拟推荐结果（用于测试）
    实际部署时应该替换为真实的模型推理
    """
    recommendations = []
    exclude_set = set(exclude_ids or [])
    
    for i in range(top_k):
        item_id = f"item_{i+1}"
        if item_id not in exclude_set:
            recommendations.append({
                "item_id": item_id,
                "score": 0.9 - (i * 0.05),
                "reason": "collaborative_filtering",
                "metadata": {
                    "name": f"Product {i+1}",
                    "category": "mandala",
                    "price": 29.99
                }
            })
    
    return recommendations


def generate_mock_similar_items(item_id: str, top_k: int) -> List[dict]:
    """生成模拟相似商品"""
    similar = []
    for i in range(top_k):
        similar.append({
            "item_id": f"similar_{i+1}",
            "similarity": 0.95 - (i * 0.05),
            "metadata": {
                "name": f"Similar Product {i+1}",
                "category": "geometric"
            }
        })
    return similar


# ============================================
# 运行服务器
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )