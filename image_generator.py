"""
图像生成模块 - 使用CogView生成亲密合照
"""
import time
import os
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, IMAGE_MODEL, OUTPUT_DIR
from utils import ensure_dir, generate_output_filename, save_image_from_url


def generate_image(prompt: str, save_path: str = None) -> str:
    """
    使用CogView生成图像

    Args:
        prompt: 图像生成提示词
        save_path: 保存路径，如果不指定则自动生���

    Returns:
        生成图片的本地路径
    """
    ensure_dir(OUTPUT_DIR)

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, generate_output_filename("intimate_photo"))

    print(f"\n🎨 正在生成图像...")
    print(f"   模型: {IMAGE_MODEL}")

    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    try:
        # 使用SDK调用图像生成API
        response = client.images.generations(
            model=IMAGE_MODEL,
            prompt=prompt,
        )

        print(f"   图像生成成功!")

        # 获取生成的图片URL
        if hasattr(response, 'data') and len(response.data) > 0:
            image_url = response.data[0].url
            print(f"   图片URL: {image_url}")

            # 下载并保存���片
            print(f"   正在下载到: {save_path}")
            save_image_from_url(image_url, save_path)
            print(f"   ✓ 已保存到: {save_path}")

            return save_path

        raise Exception("响应中没有图片数据")

    except Exception as e:
        print(f"   ✗ 错误: {e}")
        raise


def generate_with_retry(prompt: str, max_retries: int = 3, save_path: str = None) -> str:
    """
    带重试机制的图像生成

    Args:
        prompt: 图像生成提示词
        max_retries: 最大重试次数
        save_path: 保存路径

    Returns:
        生成图片的路径
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return generate_image(prompt, save_path)
        except Exception as e:
            last_error = e
            print(f"   第 {attempt + 1} 次尝试失败: {e}")
            if attempt < max_retries - 1:
                print(f"   等待 3 秒后重试...")
                time.sleep(3)

    raise last_error


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) >= 2:
        prompt = sys.argv[1]
        save_path = sys.argv[2] if len(sys.argv) > 2 else None

        print(f"提示词: {prompt[:100]}...")
        result = generate_image(prompt, save_path)
        print(f"\n结果: {result}")
    else:
        # 默认测试
        test_prompt = """
        A warm, candid photograph of a young Asian woman with shoulder-length black hair,
        sitting on a cozy worn couch with a ginger and white tabby cat curled up in her lap.
        She is smiling warmly, gently petting the cat. Golden hour sunlight streams through
        a window, casting a warm glow. Film grain, shallow depth of field, warm color grading,
        lifestyle photography, intimate moment.
        """

        print("测试图像生成...")
        result = generate_image(test_prompt)
        print(f"\n结果: {result}")
