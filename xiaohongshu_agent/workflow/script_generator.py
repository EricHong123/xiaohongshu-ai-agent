import os
"""
脚本生成器 - 使用LLM生成/优化视频脚本
集成电商视频导演Skill：分镜头提示词生成
"""
import requests
from typing import List, Dict, Any, Optional


# 电商视频导演Skill - 分镜头模板
SHOT_TEMPLATES = {
    7: [  # 7秒超短视频
        {"index": 1, "type": "Wide shot", "duration": 2, "name": "全景开场"},
        {"index": 2, "type": "Orbital shot", "duration": 3, "name": "环绕展示"},
        {"index": 3, "type": "Extreme close-up", "duration": 2, "name": "卖点强调"},
    ],
    10: [  # 10秒短视频
        {"index": 1, "type": "Wide shot", "duration": 2, "name": "全景开场"},
        {"index": 2, "type": "Orbital shot", "duration": 3, "name": "环绕展示"},
        {"index": 3, "type": "Extreme close-up", "duration": 2, "name": "材质特写"},
        {"index": 4, "type": "Medium shot", "duration": 3, "name": "功能演示"},
    ],
    15: [  # 15秒标准短视频
        {"index": 1, "type": "Wide shot", "duration": 2, "name": "全景开场"},
        {"index": 2, "type": "Orbital shot", "duration": 3, "name": "环绕展示"},
        {"index": 3, "type": "Extreme close-up", "duration": 2, "name": "材质特写"},
        {"index": 4, "type": "Medium shot", "duration": 3, "name": "功能演示"},
        {"index": 5, "type": "Macro close-up", "duration": 2, "name": "核心细节"},
        {"index": 6, "type": "Extreme close-up", "duration": 2, "name": "卖点强调"},
        {"index": 7, "type": "Wide shot", "duration": 1, "name": "全景收尾"},
    ]
}

# 风格映射
STYLE_MAPPING = {
    "数码科技": {"style": "极简科技感", "lighting": "冷色调+边缘光", "env": "暗色极简展台"},
    "奢侈品": {"style": "高端奢华感", "lighting": "电影质感", "env": "奢华展示台"},
    "家居": {"style": "温馨居家感", "lighting": "自然光", "env": "现代家居环境"},
    "美妆护肤": {"style": "柔美精致感", "lighting": "梦幻光影", "env": "精致化妆台"},
    "运动": {"style": "动感活力感", "lighting": "高对比度", "env": "运动场景"},
    "服装": {"style": "时尚潮流感", "lighting": "专业影棚光", "env": "时尚陈列架"},
    "食品": {"style": "食欲感", "lighting": "暖色调", "env": "温馨餐桌"},
    "种草": {"style": "清新自然感", "lighting": "自然柔光", "env": "生活场景"},
}


class ScriptGenerator:
    """使用MiniMax生成视频脚本 - 集成电商视频导演Skill"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "MiniMax-M2.5"
    ):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = base_url or os.getenv(
            "MINIMAX_BASE_URL",
            "https://api.minimax.chat/v1"
        )
        self.model = model

    def generate(
        self,
        product_info: Dict[str, Any],
        style: str = "种草",
        duration: int = 10
    ) -> Dict[str, Any]:
        """
        生成视频脚本 - 使用电商视频导演Skill

        Args:
            product_info: 产品信息
            style: 视频风格 (种草/测评/教程/开箱)
            duration: 时长(秒)

        Returns:
            脚本字典
        """
        if not self.api_key:
            return {"error": "请配置 MINIMAX_API_KEY 环境变量"}

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

            # MiniMax API 格式
            resp = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=data,
                timeout=120
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
            return {"error": "请配置 MINIMAX_API_KEY 环境变量"}

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

            # MiniMax API 格式
            resp = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=data,
                timeout=120
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
        """构建生成提示词 - 集成电商视频导演Skill"""
        
        # 获取分镜头模板
        template = SHOT_TEMPLATES.get(duration, SHOT_TEMPLATES[10])
        shots_desc = "\n".join([
            f"- 镜头{shot['index']}: {shot['name']}({shot['type']}, {shot['duration']}秒)"
            for shot in template
        ])
        
        # 获取风格配置
        style_config = STYLE_MAPPING.get(style, STYLE_MAPPING["种草"])
        
        return f"""你是一个专业的电商短视频导演。请为以下产品生成{duration}秒的抖音/小红书视频脚本和分镜头提示词。

产品信息:
{self._format_product(product_info)}

视频风格: {style}
风格配置: {style_config['style']}, 灯光: {style_config['lighting']}, 环境: {style_config['env']}
目标时长: {duration}秒

请根据电商视频导演Skill生成专业级分镜头提示词。

分镜头序列:
{shots_desc}

请生成JSON格式的脚本:
```json
{{
  "title": "吸引眼球的标题(适合小红书)",
  "hook": "开场白(3秒,抓住注意力)",
  "body": "主体内容(产品介绍和种草)",
  "cta": "结尾呼吁(关注、点赞)",
  "total_duration": {duration},
  "director_analysis": "导演视角分析(产品视觉呈现重点)",
  "shots": [
    {{
      "index": 1,
      "name": "镜头名称",
      "type": "Wide shot",
      "duration": 2,
      "scene": "场景描述",
      "prompt": "英文AI视频生成提示词,包含主体、运镜、灯光、环境,必须包含9:16 vertical aspect ratio"
    }}
  ]
}}
```

要求:
1. 脚本要口语化,适合口播
2. 开头要有吸引力,抓住眼球
3. 每个分镜的prompt要详细,使用英文,包含:
   - Subject: 主体描述
   - Camera Movement: 运镜方式
   - Lighting: 灯光设置
   - Environment: 环境背景
   - Technical Specs: 9:16 vertical aspect ratio, 8k, photorealistic, 60fps
4. 符合小红书/抖音年轻女性审美
5. 所有prompt必须包含 "9:16 vertical aspect ratio" 确保竖屏适配
6. 每个镜头prompt控制在120词以内,聚焦单一展示目标"""

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
