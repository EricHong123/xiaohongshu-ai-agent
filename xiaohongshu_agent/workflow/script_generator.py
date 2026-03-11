"""
脚本生成器 - 使用LLM生成/优化视频脚本
"""
import os
import requests
from typing import List, Dict, Any, Optional


class ScriptGenerator:
    """使用智谱GLM生成视频脚本"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "glm-4.6v"
    ):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
        self.base_url = base_url or os.getenv(
            "ZHIPU_BASE_URL",
            "https://open.bigmodel.cn/api/paas/v4"
        )
        self.model = model

    def generate(
        self,
        product_info: Dict[str, Any],
        style: str = "种草",
        duration: int = 10
    ) -> Dict[str, Any]:
        """
        生成视频脚本

        Args:
            product_info: 产品信息
            style: 视频风格 (种草/测评/教程/开箱)
            duration: 时长(秒)

        Returns:
            脚本字典
        """
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY 环境变量"}

        prompt = self._build_prompt(product_info, style, duration)

        messages = [
            {"role": "user", "content": prompt}
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
                timeout=30
            )

            result = resp.json()

            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                return self._parse_script(content)
            else:
                return {"error": result.get("error", "未知错误")}

        except Exception as e:
            return {"error": f"脚本生成失败: {str(e)}"}

    def optimize(
        self,
        script: Dict[str, Any],
        feedback: str = ""
    ) -> Dict[str, Any]:
        """
        优化已有脚本

        Args:
            script: 原始脚本
            feedback: 优化建议

        Returns:
            优化后的脚本
        """
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY 环境变量"}

        prompt = f"""请优化以下小红书视频脚本:

原始脚本:
{self._format_script(script)}

优化要求:
1. 更加口语化,适合口播
2. 增加吸引力,提高完播率
3. {feedback if feedback else "保持原有结构"}

请以JSON格式返回优化后的脚本。
"""

        messages = [
            {"role": "user", "content": prompt}
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
                timeout=30
            )

            result = resp.json()

            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                return self._parse_script(content)
            else:
                return {"error": result.get("error", "未知错误")}

        except Exception as e:
            return {"error": f"脚本优化失败: {str(e)}"}

    def _build_prompt(
        self,
        product_info: Dict[str, Any],
        style: str,
        duration: int
    ) -> str:
        """构建生成提示词"""
        return f"""你是一个专业的小红书短视频编剧。请为以下产品生成{duration}秒的视频脚本。

产品信息:
{self._format_product(product_info)}

视频风格: {style}
目标时长: {duration}秒

请生成JSON格式的脚本:
```json
{{
  "title": "吸引眼球的标题",
  "hook": "开场白(3秒,抓住注意力)",
  "body": "主体内容(产品介绍)",
  "cta": "结尾呼吁(关注、点赞)",
  "total_duration": {duration},
  "shots": [
    {{"index": 1, "scene": "场景", "prompt": "AI视频生成提示词", "duration": 3}},
    {{"index": 2, "scene": "场景", "prompt": "AI视频生成提示词", "duration": {duration - 3}}}
  ]
}}
```

要求:
1. 脚本要口语化,适合口播
2. 开头要有吸引力,抓住眼球
3. 分镜prompt要详细,包含主体、场景、动作
4. 符合小红书年轻女性审美
"""

    def _format_product(self, info: Dict) -> str:
        """格式化产品信息"""
        lines = []
        for key, value in info.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _format_script(self, script: Dict) -> str:
        """格式化脚本"""
        import json
        return json.dumps(script, ensure_ascii=False, indent=2)

    def _parse_script(self, content: str) -> Dict[str, Any]:
        """解析脚本"""
        import json
        import re

        # 尝试提取JSON
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {"raw_content": content}
