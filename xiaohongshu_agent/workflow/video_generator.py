"""
视频生成器 - 使用可灵AI生成视频
"""
import os
import time
import jwt
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path


class VideoGenerator:
    """可灵AI视频生成"""

    def __init__(
        self,
        access_key: str = "",
        secret_key: str = "",
        base_url: str = "https://api-beijing.klingai.com",
        model: str = "kling-v1"
    ):
        self.access_key = access_key or os.getenv("KLING_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("KLING_SECRET_KEY", "")
        self.base_url = base_url
        self.model = model

    def _generate_token(self) -> str:
        """生成JWT Token"""
        if not self.access_key or not self.secret_key:
            raise ValueError("请配置 KLING_ACCESS_KEY 和 KLING_SECRET_KEY")

        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800,
            "nbf": int(time.time()) - 5
        }

        return jwt.encode(payload, self.secret_key, headers=headers)

    def _make_request(self, method: str, path: str, data: dict = None) -> dict:
        """发送API请求"""
        if not self.access_key or not self.secret_key:
            return {"error": "请配置 KLING_ACCESS_KEY 和 KLING_SECRET_KEY"}

        token = self._generate_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f"{self.base_url}{path}"

        try:
            # 使用session支持代理环境
            session = requests.Session()
            session.verify = False
            
            import urllib3
            urllib3.disable_warnings()

            if method == "GET":
                resp = session.get(url, headers=headers, timeout=60)
            else:
                resp = session.post(url, headers=headers, json=data, timeout=120)

            return resp.json()
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

    def generate(
        self,
        prompt: str,
        image_path: str = "",
        duration: float = 5.0,
        aspect_ratio: str = "9:16"
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 视频生成提示词
            image_path: 参考图片路径(可选)
            duration: 时长(秒),支持3-10秒
            aspect_ratio: 宽高比 (9:16, 16:9, 1:1)

        Returns:
            任务信息,包含task_id用于查询结果
        """
        if not self.access_key or not self.secret_key:
            return {"error": "请配置 KLING_ACCESS_KEY 和 KLING_SECRET_KEY"}

        # 验证时长
        duration = min(max(duration, 3), 10)

        # 构建请求
        payload = {
            "model": self.model,
            "prompt": prompt,
            "duration": duration,
            "mode": "std",
            "aspect_ratio": aspect_ratio
        }

        if image_path:
            import base64
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            payload["image_url"] = f"data:image/jpeg;base64,{img_b64}"

        result = self._make_request("POST", "/v1/images/generations", payload)

        if "task_id" in result:
            return {
                "status": "processing",
                "task_id": result["task_id"],
                "duration": duration
            }
        elif "code" in result:
            return {"error": f"错误 {result.get('code')}: {result.get('message', '')}"}
        else:
            return {"error": str(result)}

    def generate_from_script(
        self,
        shots: List[Dict[str, Any]],
        reference_image: str = ""
    ) -> List[Dict[str, Any]]:
        """根据分镜列表生成视频片段"""
        results = []

        for i, shot in enumerate(shots):
            print(f"正在生成第 {i+1}/{len(shots)} 个分镜...")
            result = self.generate(
                prompt=shot.get("prompt", ""),
                image_path=reference_image if i == 0 else "",
                duration=shot.get("duration", 5),
                aspect_ratio="9:16"
            )
            results.append({"index": shot.get("index", i + 1), "prompt": shot.get("prompt", ""), "result": result})

            if i < len(shots) - 1:
                time.sleep(1)

        return results

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        result = self._make_request("GET", f"/v1/images/generations/{task_id}")

        status = result.get("task_status", "")

        if status == "succeeded":
            videos = result.get("task_result", {}).get("videos", [])
            return {
                "status": "completed",
                "video_url": videos[0].get("url", "") if videos else "",
                "cover_url": videos[0].get("cover_image_url", "") if videos else ""
            }
        elif status == "failed":
            return {
                "status": "failed",
                "error": result.get("task_result", {}).get("message", "生成失败")
            }
        else:
            return {
                "status": "processing",
                "progress": result.get("task_result", {}).get("progress", 0)
            }

    def wait_for_completion(self, task_id: str, max_wait: int = 120, interval: int = 3) -> Dict[str, Any]:
        """等待视频生成完成"""
        elapsed = 0
        while elapsed < max_wait:
            result = self.query_task(task_id)
            if result.get("status") == "completed":
                return result
            elif result.get("status") == "failed":
                return result
            print(f"等待中... ({elapsed}s)")
            time.sleep(interval)
            elapsed += interval
        return {"error": "等待超时"}
