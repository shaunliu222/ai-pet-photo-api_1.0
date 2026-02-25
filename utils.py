"""
工具函数模块
"""
import os
import base64
from pathlib import Path
from datetime import datetime


def ensure_dir(directory: str) -> None:
    """确保目录存在，不存在则创建"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def image_to_base64(image_path: str) -> str:
    """将图片转换为base64编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_mime_type(image_path: str) -> str:
    """获取图片的MIME类型"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    return mime_types.get(ext, "image/jpeg")


def save_image_from_url(url: str, save_path: str) -> str:
    """从URL下载图片并保存"""
    import requests
    response = requests.get(url)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path


def generate_output_filename(prefix: str = "photo") -> str:
    """生成输出文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.png"


def list_pet_images(pets_dir: str) -> list:
    """列出宠物目录中的所有图片"""
    if not os.path.exists(pets_dir):
        return []

    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    images = []

    for file in os.listdir(pets_dir):
        ext = os.path.splitext(file)[1].lower()
        if ext in valid_extensions:
            images.append(os.path.join(pets_dir, file))

    return sorted(images)


def print_banner():
    """打印程序横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      🐾  AI合照生图-智能体 - 让爱与温暖相遇  🐾           ║
║                                                           ║
║      上传您的照片，与流浪宠物生成温馨的亲密合照            ║
║      感受未来领养生活的美好憧憬                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_interaction_menu():
    """打印互动场景选择菜单"""
    from config import INTERACTION_TEMPLATES

    print("\n📸 请选择亲密互动场景：")
    print("-" * 50)
    for idx, template in enumerate(INTERACTION_TEMPLATES, 1):
        print(f"  {idx}. {template['name']} - {template['description']}")
    print("-" * 50)
