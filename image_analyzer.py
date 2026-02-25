"""
图像分析模块 - ��用GLM-4V分析用户和宠物照片，生成详细提示词
"""
import base64
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, VISION_MODEL, INTERACTION_TEMPLATES
from utils import get_image_mime_type, image_to_base64


def encode_image_to_url(image_path: str) -> str:
    """将本地图片编码为data URL格式"""
    mime_type = get_image_mime_type(image_path)
    base64_data = image_to_base64(image_path)
    return f"data:{mime_type};base64,{base64_data}"


def analyze_images(user_image_path: str, pet_image_path: str, interaction_id: str = "cuddle_sofa") -> str:
    """
    分析用户和宠物照片，生成详细的图像生成提示词

    Args:
        user_image_path: 用户照片路径
        pet_image_path: 宠物照片路径
        interaction_id: 互动场景ID

    Returns:
        生成的英文图像提示词
    """
    # 获取互动场景模板
    interaction = next((t for t in INTERACTION_TEMPLATES if t["id"] == interaction_id), INTERACTION_TEMPLATES[0])
    interaction_prompt = interaction["prompt_suffix"]

    # 编码图片
    user_image_url = encode_image_to_url(user_image_path)
    pet_image_url = encode_image_to_url(pet_image_path)

    # 初始化客户端
    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    # 构建消息
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""请分析以下两张照片：

[用户照片]：
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": user_image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""
[宠物照片]：
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": pet_image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""

请仔细分析用户的外貌特征（发色、发型、肤色、面部特征等）和宠物的特征（品种、花色、体型、特殊标记等）。

然后生成一段详细的英文图像生成提示词，描述用户与宠物进行"{interaction['name']}"的场景。

场景描述：{interaction['description']}
具体动作参考：{interaction_prompt}

要求：
1. 明确描述用户的外貌特征
2. 明确描述宠物的特征
3. 详细描述互动动作和姿势
4. 营造温暖、家的氛围
5. 使用专业摄影术语

请只返回英文提示词，不要有其他内容。"""
                    }
                ]
            }
        ],
        max_tokens=1024,
        temperature=0.7
    )

    prompt = response.choices[0].message.content

    # 添加摄影风格后缀
    style_suffix = ", film grain, shallow depth of field, warm color grading, lifestyle photography, candid moment, emotional connection"
    if style_suffix not in prompt:
        prompt = prompt.strip() + style_suffix

    return prompt


def extract_features_simple(image_path: str) -> str:
    """
    简单提取图片特征描述（备用函数）

    Args:
        image_path: 图片路径

    Returns:
        特征描述
    """
    image_url = encode_image_to_url(image_path)

    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请用简洁的语言描述这张照片中主体（人或宠物）的外貌特征，包括：\n1. 如果是人：发色、发型、肤色、年龄感、穿着风格\n2. 如果是宠物：品种、花色、体型、特殊标记\n\n请直接列出特征，不要有开场白。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        max_tokens=512,
        temperature=0.5
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) >= 3:
        user_img = sys.argv[1]
        pet_img = sys.argv[2]
        interaction = sys.argv[3] if len(sys.argv) > 3 else "cuddle_sofa"

        print(f"分析用户照片: {user_img}")
        print(f"分析宠物照片: {pet_img}")
        print(f"互动场景: {interaction}")
        print("-" * 50)

        prompt = analyze_images(user_img, pet_img, interaction)
        print("生成的提示词：")
        print(prompt)
