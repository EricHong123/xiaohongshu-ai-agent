"""
视频生成器 - 使用可灵AI生成视频
"""
import os
import requests
import time
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class VideoGenerator:
    """可灵AI视频生成"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.klingai.com",
        model: str = "kling-v1"
    ):
        self.api_key = api_key or os.getenv("KLING_API_KEY", "")
        self.base_url = base_url
        self.model = model

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
        if not self.api_key:
            return {"error": "请配置 KLING_API_KEY 环境变量"}

        # 验证时长
        duration = min(max(duration, 3), 10)

        url = f"{self.base_url}/v1/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建请求
        data = {
            "model": self.model,
            "prompt": prompt,
            "duration": duration,
            "mode": "std",  # std 或 pro
            "aspect_ratio": aspect_ratio
        }

        if image_path:
            # 添加参考图
            import base64
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            data["image_url"] = f"data:image/jpeg;base64,{img_b64}"

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            result = resp.json()

            if "task_id" in result:
                return {
                    "status": "processing",
                    "task_id": result["task_id"],
                    "duration": duration
                }
            else:
                return {"error": result.get("message", "生成失败")}

        except Exception as e:
            return {"error": f"视频生成请求失败: {str(e)}"}

    def generate_from_script(
        self,
        shots: List[Dict[str, Any]],
        reference_image: str = ""
    ) -> List[Dict[str, Any]]:
        """
        根据分镜列表生成视频片段

        Args:
            shots: 分镜列表,每项包含 prompt 和 duration
            reference_image: 参考图(可选)

        Returns:
            分镜生成结果列表
        """
        results = []

        for i, shot in enumerate(shots):
            print(f"正在生成第 {i+1}/{len(shots)} 个分镜...")

            result = self.generate(
                prompt=shot.get("prompt", ""),
                image_path=reference_image if i == 0 else "",
                duration=shot.get("duration", 5),
                aspect_ratio="9:16"  # 小红书竖版
            )

            results.append({
                "index": shot.get("index", i + 1),
                "prompt": shot.get("prompt", ""),
                "result": result
            })

            # 避免请求过快
            if i < len(shots) - 1:
                time.sleep(1)

        return results

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态和结果
        """
        url = f"{self.base_url}/v1/images/generations/{task_id}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            result = resp.json()

            status = result.get("task_status", "")

            if status == "succeeded":
                return {
                    "status": "completed",
                    "video_url": result.get("task_result", {}).get("videos", [{}])[0].get("url", ""),
                    "cover_url": result.get("task_result", {}).get("videos", [{}])[0].get("cover_image_url", "")
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

        except Exception as e:
            return {"error": f"查询任务失败: {str(e)}"}

    def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 120,
        interval: int = 3
    ) -> Dict[str, Any]:
        """
        等待视频生成完成

        Args:
            task_id: 任务ID
            max_wait: 最大等待时间(秒)
            interval: 查询间隔(秒)

        Returns:
            最终结果
        """
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


# 兼容旧版本API的别名
class KlingVideoGenerator(VideoGenerator):
    """可灵视频生成器 (别名)"""
    pass
