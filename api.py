#!/usr/bin/env python3
"""
AI合照生图-智能体 API服务
提供RESTful API接口供外部调用
"""
import os
import uuid
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import OUTPUT_DIR, INTERACTION_TEMPLATES
from image_analyzer import analyze_images
from image_generator import generate_image
from utils import ensure_dir

# 创建FastAPI应用
app = FastAPI(
    title="AI合照生图-智能体 API",
    description="帮助潜在领养者与流浪宠物生成温馨的亲密合照",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保输出目录存在
ensure_dir(OUTPUT_DIR)


# ============== 数据模型 ==============

class InteractionScene(BaseModel):
    """互动场景"""
    id: str
    name: str
    description: str


class GenerateRequest(BaseModel):
    """生成请求（URL方式）"""
    user_image_url: str
    pet_image_url: str
    interaction_id: str = "cuddle_sofa"


class GenerateResponse(BaseModel):
    """生成响应"""
    success: bool
    message: str
    prompt: Optional[str] = None
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    task_id: Optional[str] = None


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str  # pending, processing, completed, failed
    message: str
    result: Optional[dict] = None


# ============== 存储任务状态（生产环境应使用Redis） ==============
tasks_storage = {}


# ============== API接口 ==============

@app.get("/", tags=["首页"])
async def root():
    """API首页"""
    return {
        "name": "AI合照生图-智能体 API",
        "version": "1.0.0",
        "description": "帮助潜在领养者与流浪宠物生成温馨的亲密合照",
        "endpoints": {
            "生成合照(文件上传)": "POST /api/generate/upload",
            "生成合照(URL)": "POST /api/generate/url",
            "获取互动场景": "GET /api/scenes",
            "查看任务状态": "GET /api/task/{task_id}",
            "下载图片": "GET /api/download/{filename}"
        }
    }


@app.get("/api/scenes", response_model=list[InteractionScene], tags=["互动场景"])
async def get_interaction_scenes():
    """
    获取所有可用的互动场景

    返回所有支持的亲密互动场景列表
    """
    return [
        InteractionScene(
            id=s["id"],
            name=s["name"],
            description=s["description"]
        )
        for s in INTERACTION_TEMPLATES
    ]


@app.post("/api/generate/upload", response_model=GenerateResponse, tags=["生成合照"])
async def generate_with_upload(
    background_tasks: BackgroundTasks,
    user_image: UploadFile = File(..., description="用户照片"),
    pet_image: UploadFile = File(..., description="宠物照片"),
    interaction_id: str = Form(default="cuddle_sofa", description="互动场景ID"),
    async_mode: bool = Form(default=False, description="是否异步处理")
):
    """
    通过文件上传生成亲密合照

    - **user_image**: 用户照片文件
    - **pet_image**: 宠物照片文件
    - **interaction_id**: 互动场景ID（可选，默认cuddle_sofa）
    - **async_mode**: 是否异步处理（可选，默认False）

    返回生成的合照信息
    """
    # 验证互动场景
    valid_ids = [s["id"] for s in INTERACTION_TEMPLATES]
    if interaction_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"无效的互动场景ID，可选值: {valid_ids}")

    # 保存上传的文件
    task_id = str(uuid.uuid4())

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 保存用户照片
        user_path = os.path.join(temp_dir, f"user_{task_id}{os.path.splitext(user_image.filename)[1]}")
        with open(user_path, "wb") as f:
            content = await user_image.read()
            f.write(content)

        # 保存宠物照片
        pet_path = os.path.join(temp_dir, f"pet_{task_id}{os.path.splitext(pet_image.filename)[1]}")
        with open(pet_path, "wb") as f:
            content = await pet_image.read()
            f.write(content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    if async_mode:
        # 异步处理
        tasks_storage[task_id] = {
            "status": "pending",
            "message": "任务已创建，等待处理"
        }
        background_tasks.add_task(process_generation, task_id, user_path, pet_path, interaction_id)

        return GenerateResponse(
            success=True,
            message="任务已创建，请通过 /api/task/{task_id} 查询状态",
            task_id=task_id
        )

    # 同步处理
    return await process_generation_sync(task_id, user_path, pet_path, interaction_id)


@app.post("/api/generate/url", response_model=GenerateResponse, tags=["生成合照"])
async def generate_with_url(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    async_mode: bool = False
):
    """
    通过图片URL生成亲密合照

    - **user_image_url**: 用户照片URL
    - **pet_image_url**: 宠物照片URL
    - **interaction_id**: 互动场景ID（可选，默认cuddle_sofa）
    - **async_mode**: 是否异步处理（查询参数，默认False）

    返回生成的合照信息
    """
    import requests

    # 验证互动场景
    valid_ids = [s["id"] for s in INTERACTION_TEMPLATES]
    if request.interaction_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"无效的互动场景ID，可选值: {valid_ids}")

    task_id = str(uuid.uuid4())

    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 下载用户照片
        user_path = os.path.join(temp_dir, f"user_{task_id}.jpg")
        resp = requests.get(request.user_image_url, timeout=30)
        resp.raise_for_status()
        with open(user_path, "wb") as f:
            f.write(resp.content)

        # 下载宠物照片
        pet_path = os.path.join(temp_dir, f"pet_{task_id}.jpg")
        resp = requests.get(request.pet_image_url, timeout=30)
        resp.raise_for_status()
        with open(pet_path, "wb") as f:
            f.write(resp.content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片下载失败: {str(e)}")

    if async_mode:
        # 异步处理
        tasks_storage[task_id] = {
            "status": "pending",
            "message": "任务已创建，等待处理"
        }
        background_tasks.add_task(process_generation, task_id, user_path, pet_path, request.interaction_id)

        return GenerateResponse(
            success=True,
            message="任务已创建，请通过 /api/task/{task_id} 查询状态",
            task_id=task_id
        )

    # 同步处理
    return await process_generation_sync(task_id, user_path, pet_path, request.interaction_id)


@app.get("/api/task/{task_id}", response_model=TaskStatus, tags=["任务管理"])
async def get_task_status(task_id: str):
    """
    查询异步任务状态

    - **task_id**: 任务ID

    返回任务状态和结果
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks_storage[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        message=task["message"],
        result=task.get("result")
    )


@app.get("/api/download/{filename}", tags=["文件下载"])
async def download_image(filename: str):
    """
    下载生成的图片

    - **filename**: 图片文件名

    返回图片文件
    """
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        file_path,
        media_type="image/png",
        filename=filename
    )


# ============== 辅助函数 ==============

async def process_generation_sync(task_id: str, user_path: str, pet_path: str, interaction_id: str) -> GenerateResponse:
    """同步处理生成任务"""
    try:
        # Step 1: 分析照片
        prompt = analyze_images(user_path, pet_path, interaction_id)

        # Step 2: 生成图像
        output_path = generate_image(prompt)

        # 获取文件名和URL
        filename = os.path.basename(output_path)

        return GenerateResponse(
            success=True,
            message="合照生成成功",
            prompt=prompt,
            image_url=f"/api/download/{filename}",
            local_path=output_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


def process_generation(task_id: str, user_path: str, pet_path: str, interaction_id: str):
    """异步处理生成任务"""
    try:
        tasks_storage[task_id] = {
            "status": "processing",
            "message": "正在分析照片..."
        }

        # Step 1: 分析照片
        prompt = analyze_images(user_path, pet_path, interaction_id)

        tasks_storage[task_id] = {
            "status": "processing",
            "message": "正在生成图像..."
        }

        # Step 2: 生成图像
        output_path = generate_image(prompt)
        filename = os.path.basename(output_path)

        tasks_storage[task_id] = {
            "status": "completed",
            "message": "生成完成",
            "result": {
                "prompt": prompt,
                "image_url": f"/api/download/{filename}",
                "local_path": output_path
            }
        }

    except Exception as e:
        tasks_storage[task_id] = {
            "status": "failed",
            "message": f"生成失败: {str(e)}"
        }


# ============== 启动配置 ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
