# AI合照生图-智能体 API 接口文档

## 概述

AI合照生图-智能体 API 提供RESTful接口，帮助潜在领养者与流浪宠物生成温馨的亲密合照。

**Base URL**: `http://localhost:8000`

**在线文档**: `http://localhost:8000/docs` (Swagger UI)

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python api.py
```

服务将在 `http://localhost:8000` 启动

---

## API 接口

### 1. 首页

```
GET /
```

返回API基本信息。

**响应示例**:
```json
{
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
```

---

### 2. 获取互动场景列表

```
GET /api/scenes
```

获取所有可用的亲密互动场景。

**响应示例**:
```json
[
  {
    "id": "cuddle_sofa",
    "name": "沙发相拥",
    "description": "坐在沙发上，宠物依偎在怀里"
  },
  {
    "id": "sleeping_together",
    "name": "一起睡觉",
    "description": "温馨的午睡时光，宠物蜷缩在身边"
  },
  {
    "id": "feeding",
    "name": "喂食时光",
    "description": "给宠物喂食的温馨画面"
  },
  {
    "id": "outdoor_walk",
    "name": "户外散步",
    "description": "阳光下的户外互动"
  },
  {
    "id": "gentle_touch",
    "name": "温柔抚摸",
    "description": "轻抚宠物，深情对视"
  }
]
```

---

### 3. 生成合照（文件上传）

```
POST /api/generate/upload
```

通过上传图片文件生成亲密合照。

**请求参数** (multipart/form-data):

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_image | file | 是 | 用户照片 |
| pet_image | file | 是 | 宠物照片 |
| interaction_id | string | 否 | 互动场景ID，默认 "cuddle_sofa" |
| async_mode | boolean | 否 | 是否异步处理，默认 false |

**请求示例 (curl)**:
```bash
curl -X POST "http://localhost:8000/api/generate/upload" \
  -H "accept: application/json" \
  -F "user_image=@/path/to/user.jpg" \
  -F "pet_image=@/path/to/pet.jpg" \
  -F "interaction_id=cuddle_sofa"
```

**响应示例 (同步模式)**:
```json
{
  "success": true,
  "message": "合照生成成功",
  "prompt": "A young individual with short brown hair...",
  "image_url": "/api/download/intimate_photo_20260225_155517.png",
  "local_path": "/path/to/output/intimate_photo_20260225_155517.png",
  "task_id": null
}
```

**响应示例 (异步模式)**:
```json
{
  "success": true,
  "message": "任务已创建，请通过 /api/task/{task_id} 查询状态",
  "prompt": null,
  "image_url": null,
  "local_path": null,
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 4. 生成合照（URL方式）

```
POST /api/generate/url
```

通过图片URL生成亲密合照。

**请求参数** (application/json):

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_image_url | string | 是 | 用户照片URL |
| pet_image_url | string | 是 | 宠物照片URL |
| interaction_id | string | 否 | 互动场景ID，默认 "cuddle_sofa" |

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| async_mode | boolean | 否 | 是否异步处理，默认 false |

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/generate/url" \
  -H "Content-Type: application/json" \
  -d '{
    "user_image_url": "https://example.com/user.jpg",
    "pet_image_url": "https://example.com/pet.jpg",
    "interaction_id": "cuddle_sofa"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "合照生成成功",
  "prompt": "A young individual with short brown hair...",
  "image_url": "/api/download/intimate_photo_20260225_155517.png",
  "local_path": "/path/to/output/intimate_photo_20260225_155517.png",
  "task_id": null
}
```

---

### 5. 查询任务状态

```
GET /api/task/{task_id}
```

查询异步任务的处理状态。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |

**响应示例**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "生成完成",
  "result": {
    "prompt": "A young individual with short brown hair...",
    "image_url": "/api/download/intimate_photo_20260225_155517.png",
    "local_path": "/path/to/output/intimate_photo_20260225_155517.png"
  }
}
```

**状态说明**:

| 状态 | 说明 |
|------|------|
| pending | 等待处理 |
| processing | 正在处理 |
| completed | 处理完成 |
| failed | 处理失败 |

---

### 6. 下载图片

```
GET /api/download/{filename}
```

下载生成的图片文件。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 图片文件名 |

**响应**: 图片文件 (image/png)

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/download/intimate_photo_20260225_155517.png" \
  --output photo.png
```

---

## 错误响应

所有错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见错误码**:

| HTTP状态码 | 说明 |
|------------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python 示例

```python
import requests

# 文件上传方式
url = "http://localhost:8000/api/generate/upload"

with open("user.jpg", "rb") as user_file, open("pet.jpg", "rb") as pet_file:
    files = {
        "user_image": ("user.jpg", user_file, "image/jpeg"),
        "pet_image": ("pet.jpg", pet_file, "image/jpeg")
    }
    data = {
        "interaction_id": "cuddle_sofa"
    }

    response = requests.post(url, files=files, data=data)
    result = response.json()

    if result["success"]:
        print(f"生成成功！图片URL: {result['image_url']}")

        # 下载图片
        img_response = requests.get(f"http://localhost:8000{result['image_url']}")
        with open("output.png", "wb") as f:
            f.write(img_response.content)
```

### JavaScript 示例

```javascript
// 文件上传方式
const formData = new FormData();
formData.append('user_image', userFile);
formData.append('pet_image', petFile);
formData.append('interaction_id', 'cuddle_sofa');

fetch('http://localhost:8000/api/generate/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('生成成功！图片URL:', data.image_url);
  }
});
```

---

## 互动场景说明

| ID | 名称 | 描述 |
|----|------|------|
| cuddle_sofa | 沙发相拥 | 坐在沙发上，宠物依偎在怀里 |
| sleeping_together | 一起睡觉 | 温馨的午睡时光，宠物蜷缩在身边 |
| feeding | 喂食时光 | 给宠物喂食的温馨画面 |
| outdoor_walk | 户外散步 | 阳光下的户外互动 |
| gentle_touch | 温柔抚摸 | 轻抚宠物，深情对视 |

---

## 部署说明

### 开发环境

```bash
python api.py
```

### 生产环境

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t ai-photo-api .
docker run -p 8000:8000 ai-photo-api
```

---

## 技术支持

- GitHub Issues: [项目地址]
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
