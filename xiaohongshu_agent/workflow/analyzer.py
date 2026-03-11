"""
图片分析器 - 使用多模态LLM分析产品图片
"""
import os
import base64
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path


class ImageAnalyzer:
    """使用智谱GLM-4V分析产品图片"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "glm-4-flash"
    ):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
        self.base_url = base_url or os.getenv(
            "ZHIPU_BASE_URL",
            "https://open.bigmodel.cn/api/paas/v4"
        )
        self.model = model

    def _encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _read_image_url(self, url: str) -> str:
        """从URL读取图片并编码"""
        response = requests.get(url, timeout=60)
        return base64.b64encode(response.content).decode("utf-8")

    def analyze(
        self,
        image_paths: List[str],
        product_name: str = "",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        分析产品图片

        Args:
            image_paths: 图片路径列表
            product_name: 产品名称(可选)
            context: 额外上下文信息

        Returns:
            分析结果字典
        """
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY 环境变量"}

        # 构建图片内容
        images_content = []
        for path in image_paths:
            if path.startswith("http"):
                b64 = self._read_image_url(path)
            else:
                b64 = self._encode_image(path)

            images_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}"
                }
            })

        # 构建提示词
        prompt = self._build_prompt(product_name, context)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    *images_content
                ]
            }
        ]

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": messages
            }

            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            result = resp.json()

            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                return self._parse_response(content)
            else:
                return {"error": result.get("error", "未知错误")}

        except Exception as e:
            return {"error": f"图片分析失败: {str(e)}"}

    def _build_prompt(self, product_name: str, context: str) -> str:
        """构建分析提示词"""
        base_prompt = """你是一个专业的小红书种草视频创意专家。请分析以下产品图片，生成视频创作所需的脚本和分镜信息。

请以JSON格式返回分析结果，包含以下字段：
```json
{
  "product_name": "产品名称",
  "product_features": ["特点1", "特点2", "特点3"],
  "target_audience": "目标人群",
  "video_style": "视频风格",
  "script": {
    "title": "视频标题(吸引眼球的)",
    "hook": "开场白(3秒,抓住注意力)",
    "body": "主体内容(产品介绍和种草)",
    "cta": "结尾呼吁(关注、点赞等)"
  },
  "shots": [
    {"index": 1, "scene": "场景描述", "prompt": "AI视频生成提示词", "duration": 3},
    {"index": 2, "scene": "场景描述", "prompt": "AI视频生成提示词", "duration": 4}
  ]
}
```

要求：
1. 脚本口语化,适合口播
2. 每个分镜的prompt要详细,包含主体、场景、动作、光线等
3. 整体时长控制在7-15秒
4. 风格要符合小红书年轻女性受众
"""

        if product_name:
            base_prompt += f"\n产品名称: {product_name}"
        if context:
            base_prompt += f"\n额外信息: {context}"

        return base_prompt

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """解析LLM返回的内容"""
        import json
        import re

        # 尝试提取JSON
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 如果解析失败,返回原始内容
        return {
            "raw_response": content,
            "error": "JSON解析失败,请检查返回格式"
        }
