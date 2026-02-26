"""
AI合照生图-智能体 配置文件
"""
import os

# 智谱AI API配置 - 使用环境变量
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "0c2259755c3446afbf508c19fcee939c.fPWCmzXHimidSIOC")

# API端点
ZHIPU_API_BASE = "https://open.bigmodel.cn/api/paas/v4"

# 模型配置
VISION_MODEL = "glm-4v-flash"  # 多模态视觉模型
IMAGE_MODEL = "cogview-3-flash"  # 图像生成模型 (免费)

# 目录配置 - 使用/tmp目录作为输出目录（Render只读文件系统）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PETS_DIR = os.path.join(BASE_DIR, "pets")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/output")

# 亲密互动场景模板
INTERACTION_TEMPLATES = [
    {
        "id": "cuddle_sofa",
        "name": "沙发相拥",
        "description": "坐在沙发上，宠物依偎在怀里",
        "prompt_suffix": "sitting on a cozy worn couch, gently holding the pet close, warm smile, golden hour sunlight streaming through window"
    },
    {
        "id": "sleeping_together",
        "name": "一起睡觉",
        "description": "温馨的午睡时光，宠物蜷缩在身边",
        "prompt_suffix": "sleeping peacefully in a soft bed, the pet curled up on chest or beside, morning light, serene and cozy atmosphere"
    },
    {
        "id": "feeding",
        "name": "喂食时光",
        "description": "给宠物喂食的温馨画面",
        "prompt_suffix": "sitting on kitchen floor, hand-feeding the pet, warm eye contact, morning sunlight, homey kitchen background"
    },
    {
        "id": "outdoor_walk",
        "name": "户外散步",
        "description": "阳光下的户外互动",
        "prompt_suffix": "walking together in a sunny park, happy expression, green grass and trees, beautiful day, lifestyle photography"
    },
    {
        "id": "gentle_touch",
        "name": "温柔抚摸",
        "description": "轻抚宠物，深情对视",
        "prompt_suffix": "sitting on floor with legs crossed, gently petting the animal, looking at each other with love, warm indoor lighting, intimate moment"
    }
]

# 摄影师系统提示词
PHOTOGRAPHER_SYSTEM_PROMPT = """你是一位世界顶级的温情派宠物摄影师，擅长捕捉人与动物之间最真实、深刻的情感纽带。你的任务是帮助潜在的领养者想象他们与这只特定流浪动物未来的生活场景。

你将接收两组输入：
1. [User Image]: 一张用户的照片。
2. [Pet Image]: 一张特定流浪宠物的照片。

你需要运用你的视觉分析能力，提取两者的关键特征，然后编写一段极其详细的英文图像生成提示词（Prompt），这段提示词将被发送给一个高级 AI 绘画模型。

编写提示词的要求：
1. **身份保持至关重要：** 必须明确描述画面中的人具有 [User Image] 中的发色、发型、种族和面部特征；画面中的宠物必须是 [Pet Image] 中的确切品种、花色和独特标记（例如左眼周围的斑点）。
2. **定义亲密互动动作：** 不要只写"在一起"。要写具体的动作，例如："The person is sitting on a worn couch, gently scratching behind the dog's ears, smiling warmly down at it," 或 "A person is sleeping deeply with the ginger cat curled up on their chest, purring."
3. **营造氛围 (The Vibe)：** 关键词是"家"、"安全感"、"被爱"、"慵懒的午后"。光线应该是黄金时刻的暖光，背景是舒适、略显杂乱但充满生活气息的客厅或卧室。
4. **摄影风格：** 胶片颗粒感，浅景深 (shallow depth of field)，聚焦于情感交流的眼神或接触点，色彩温暖、柔和。

返回格式：仅返回最终的英文图像提示词，不要包含其他对话。"""
