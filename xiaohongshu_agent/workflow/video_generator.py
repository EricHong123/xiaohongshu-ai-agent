"""
视频生成器 - 支持多种后端
"""
import os
import time
import jwt
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path


class VideoGenerator:
    """多后端视频生成器"""

    def __init__(
        self,
        provider: str = "zhipu",  # zhipu, kling, minimax
        access_key: str = "",
        secret_key: str = "",
        api_key: str = "",
        base_url: str = "",
        model: str = "cogvideoX-3"
    ):
        self.provider = provider
        self.access_key = access_key or os.getenv("KLING_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("KLING_SECRET_KEY", "")
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", os.getenv("MINIMAX_API_KEY", ""))
        self.base_url = base_url
        self.model = model

    def generate(
        self,
        prompt: str,
        image_path: str = "",
        duration: float = 5.0,
        aspect_ratio: str = "9:16"
    ) -> Dict[str, Any]:
        """生成视频"""
        if self.provider == "kling":
            return self._generate_kling(prompt, image_path, duration, aspect_ratio)
        elif self.provider == "zhipu":
            return self._generate_zhipu(prompt, image_path, duration)
        elif self.provider == "minimax":
            return self._generate_minimax(prompt, image_path, duration)
        else:
            return {"error": f"不支持的供应商: {self.provider}"}

    def _generate_kling(self, prompt: str, image_path: str, duration: float, aspect_ratio: str) -> Dict[str, Any]:
        """可灵AI生成"""
        if not self.access_key or not self.secret_key:
            return {"error": "请配置 KLING_ACCESS_KEY 和 KLING_SECRET_KEY"}

        try:
            # 生成JWT Token
            headers = {"alg": "HS256", "typ": "JWT"}
            payload = {
                "iss": self.access_key,
                "exp": int(time.time()) + 1800,
                "nbf": int(time.time()) - 5
            }
            token = jwt.encode(payload, self.secret_key, headers=headers)

            # 构建请求
            url = "https://api-beijing.klingai.com/v1/images/generations"

            payload = {
                "model": "kling-v1",
                "prompt": prompt,
                "duration": min(max(duration, 3), 10),
                "mode": "std",
                "aspect_ratio": aspect_ratio
            }

            if image_path:
                import base64
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                payload["image_url"] = f"data:image/jpeg;base64,{img_b64}"

            session = requests.Session()
            session.verify = False
            import urllib3
            urllib3.disable_warnings()

            resp = session.post(
                url,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                json=payload,
                timeout=120
            )

            result = resp.json()

            if "task_id" in result:
                return {"status": "processing", "task_id": result["task_id"], "duration": duration}
            elif "code" in result:
                return {"error": f"错误 {result.get('code')}: {result.get('message', '')}"}
            else:
                return {"error": str(result)}

        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

    def _generate_zhipu(self, prompt: str, image_path: str, duration: float) -> Dict[str, Any]:
        """智谱CogVideo生成"""
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY"}

        # 智谱CogVideo可能需要单独的API端点
        # 当前测试显示账户可能没有开通此功能
        return {
            "error": "智谱CogVideoX需要单独开通，请确认账户已开通此功能",
            "suggestion": "当前支持: 可灵(kling), 请确保账户余额充足"
        }

    def _generate_minimax(self, prompt: str, image_path: str, duration: float) -> Dict[str, Any]:
        """MiniMax视频生成"""
        if not self.api_key:
            return {"error": "请配置 MINIMAX_API_KEY"}

        return {"error": "MiniMax视频生成功能开发中"}

    def generate_from_script(
        self,
        shots: List[Dict[str, Any]],
        reference_image: str = ""
    ) -> List[Dict[str, Any]]:
        """根据分镜列表生成视频"""
        results = []
        for i, shot in enumerate(shots):
            result = self.generate(
                prompt=shot.get("prompt", ""),
                image_path=reference_image if i == 0 else "",
                duration=shot.get("duration", 5)
            )
            results.append({
                "index": shot.get("index", i + 1),
                "prompt": shot.get("prompt", ""),
                "result": result
            })
            if i < len(shots) - 1:
                time.sleep(1)
        return results

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        if self.provider == "kling":
            return self._query_kling(task_id)
        return {"error": "不支持的供应商"}

    def _query_kling(self, task_id: str) -> Dict[str, Any]:
        """查询可灵任务"""
        try:
            # 生成JWT
            headers = {"alg": "HS256", "typ": "JWT"}
            payload = {"iss": self.access_key, "exp": int(time.time()) + 1800, "nbf": int(time.time()) - 5}
            token = jwt.encode(payload, self.secret_key, headers=headers)

            url = f"https://api-beijing.klingai.com/v1/images/generations/{task_id}"

            session = requests.Session()
            session.verify = False
            import urllib3
            urllib3.disable_warnings()

            resp = session.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            result = resp.json()

            status = result.get("task_status", "")
            if status == "succeeded":
                videos = result.get("task_result", {}).get("videos", [])
                return {"status": "completed", "video_url": videos[0].get("url", "") if videos else ""}
            elif status == "failed":
                return {"status": "failed", "error": result.get("task_result", {}).get("message", "生成失败")}
            else:
                return {"status": "processing", "progress": result.get("task_result", {}).get("progress", 0)}

        except Exception as e:
            return {"error": str(e)}

    def wait_for_completion(self, task_id: str, max_wait: int = 120, interval: int = 3) -> Dict[str, Any]:
        """等待视频生成完成"""
        elapsed = 0
        while elapsed < max_wait:
            result = self.query_task(task_id)
            if result.get("status") == "completed":
                return result
            elif result.get("status") == "failed":
                return result
            time.sleep(interval)
            elapsed += interval
        return {"error": "等待超时"}
