"""
小红书发布器 - 集成现有MCP通道发布视频
"""
import os
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path


class XiaohongshuPublisher:
    """小红书视频发布"""

    def __init__(
        self,
        mcp_url: str = "http://localhost:9000",
        cookie: str = ""
    ):
        self.mcp_url = mcp_url or os.getenv("XHS_MCP_URL", "http://localhost:9000")
        self.cookie = cookie or os.getenv("XHS_COOKIE", "")

    def publish(
        self,
        video_path: str,
        title: str,
        content: str,
        tags: List[str] = None,
        images: List[str] = None,
        location: str = ""
    ) -> Dict[str, Any]:
        """
        发布视频到小红书

        Args:
            video_path: 视频文件路径
            title: 标题
            content: 正文内容
            tags: 标签列表
            images: 附带图片(可选)
            location: 位置信息(可选)

        Returns:
            发布结果
        """
        if not os.path.exists(video_path):
            return {"error": f"视频文件不存在: {video_path}"}

        # 调用MCP接口发布
        try:
            # 方法1: 通过MCP服务
            result = self._publish_via_mcp(
                video_path=video_path,
                title=title,
                content=content,
                tags=tags or [],
                images=images or [],
                location=location
            )
            return result

        except Exception as e:
            return {"error": f"发布失败: {str(e)}"}

    def _publish_via_mcp(
        self,
        video_path: str,
        title: str,
        content: str,
        tags: List[str],
        images: List[str],
        location: str
    ) -> Dict[str, Any]:
        """通过MCP服务发布"""

        # 读取视频文件
        with open(video_path, "rb") as f:
            video_data = f.read()

        # 构建请求
        # 这里需要根据实际的MCP接口调整
        # 假设MCP提供了一个publish_video工具

        # 方案1: 直接调用MCP的HTTP接口
        try:
            url = f"{self.mcp_url}/api/publish/video"

            files = {
                "video": ("video.mp4", video_data, "video/mp4")
            }

            data = {
                "title": title,
                "content": content,
                "tags": ",".join(tags),
                "location": location
            }

            resp = requests.post(url, files=files, data=data, timeout=120)

            if resp.status_code == 200:
                return {
                    "status": "success",
                    "note_id": resp.json().get("note_id", ""),
                    "url": resp.json().get("url", "")
                }
            else:
                return {"error": f"发布失败: {resp.text}"}

        except requests.exceptions.ConnectionError:
            # MCP服务未运行,返回提示
            return {
                "status": "ready_to_publish",
                "video_path": video_path,
                "title": title,
                "content": content,
                "tags": tags,
                "message": "MCP服务未运行,请手动发布"
            }

    def create_post_data(
        self,
        video_path: str,
        title: str,
        content: str,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        创建发布数据结构 (用于手动发布)

        Returns:
            发布数据
        """
        return {
            "video": {
                "path": video_path,
                "exists": os.path.exists(video_path)
            },
            "title": title,
            "content": content,
            "tags": tags or [],
            "length": self._format_content_length(content)
        }

    def _format_content_length(self, content: str) -> str:
        """格式化内容长度"""
        length = len(content)
        if length < 100:
            return "短"
        elif length < 300:
            return "中"
        else:
            return "长"

    def batch_publish(
        self,
        videos: List[Dict[str, Any]],
        delay: int = 10
    ) -> List[Dict[str, Any]]:
        """
        批量发布

        Args:
            videos: 视频列表,每项包含 video_path, title, content, tags
            delay: 两条发布之间的延迟(秒)

        Returns:
            发布结果列表
        """
        import time
        results = []

        for i, video in enumerate(videos):
            print(f"正在发布第 {i+1}/{len(videos)} 条...")

            result = self.publish(
                video_path=video["video_path"],
                title=video.get("title", ""),
                content=video.get("content", ""),
                tags=video.get("tags", [])
            )

            results.append(result)

            # 避免发布过快
            if i < len(videos) - 1:
                time.sleep(delay)

        return results
