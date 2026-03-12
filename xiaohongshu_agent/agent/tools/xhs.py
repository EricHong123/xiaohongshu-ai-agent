"""
小红书自动化工具
基于 xhs_automation CLI 的封装
"""
import subprocess
import json
import os
from typing import Any, Dict
from .base import Tool, ToolResult, registry


SCRIPT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "xhs_automation", "scripts"
)
CLI_PATH = os.path.join(SCRIPT_DIR, "cli.py")


def run_cli(args: list) -> Dict:
    """执行 CLI 命令"""
    cmd = ["python3", CLI_PATH] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=SCRIPT_DIR
        )
        output = result.stdout.strip()
        # 尝试解析 JSON
        try:
            return json.loads(output) if output else {}
        except json.JSONDecodeError:
            return {"raw": output, "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}


@registry.register("xhs")
class XiaohongshuTool(Tool):
    """小红书自动化工具"""

    name = "xhs"
    description = """
    小红书自动化操作，包括：
    - 登录检查和登录
    - 搜索笔记
    - 获取笔记详情
    - 发布图文/视频
    - 点赞、收藏、评论
    - 获取用户信息
    """

    def execute(self, action: str, **kwargs) -> ToolResult:
        """执行小红书操作"""
        action_map = {
            # 认证
            "check_login": ["check-login"],
            "login": ["login"],
            "logout": ["delete-cookies"],

            # 内容发现
            "list_feeds": ["list-feeds"],
            "search": ["search-feeds", "--keyword", kwargs.get("keyword", "")],
            "feed_detail": ["get-feed-detail",
                           "--feed-id", kwargs.get("feed_id", ""),
                           "--xsec-token", kwargs.get("xsec_token", "")],
            "user_profile": ["user-profile", "--user-id", kwargs.get("user_id", "")],

            # 发布
            "publish": ["publish",
                       "--title-file", kwargs.get("title_file", ""),
                       "--content-file", kwargs.get("content_file", ""),
                       "--images"] + kwargs.get("images", []),
            "publish_video": ["publish-video",
                            "--title-file", kwargs.get("title_file", ""),
                            "--content-file", kwargs.get("content_file", ""),
                            "--video", kwargs.get("video", "")],

            # 互动
            "like": ["like-feed",
                    "--feed-id", kwargs.get("feed_id", ""),
                    "--xsec-token", kwargs.get("xsec_token", "")],
            "favorite": ["favorite-feed",
                        "--feed-id", kwargs.get("feed_id", ""),
                        "--xsec-token", kwargs.get("xsec_token", "")],
            "comment": ["post-comment",
                       "--feed-id", kwargs.get("feed_id", ""),
                       "--xsec-token", kwargs.get("xsec_token", ""),
                       "--content", kwargs.get("content", "")],
            "reply": ["reply-comment",
                     "--feed-id", kwargs.get("feed_id", ""),
                     "--xsec-token", kwargs.get("xsec_token", ""),
                     "--comment-id", kwargs.get("comment_id", ""),
                     "--content", kwargs.get("content", "")],
        }

        if action not in action_map:
            return ToolResult(
                success=False,
                error=f"未知操作: {action}，支持: {list(action_map.keys())}"
            )

        args = action_map[action]
        # 过滤空字符串
        args = [arg for arg in args if arg]

        result = run_cli(args)
        return ToolResult(
            success="error" not in result,
            data=result
        )

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作类型",
                        "enum": [
                            "check_login", "login", "logout",
                            "list_feeds", "search", "feed_detail", "user_profile",
                            "publish", "publish_video",
                            "like", "favorite", "comment", "reply"
                        ]
                    },
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "feed_id": {"type": "string", "description": "笔记ID"},
                    "xsec_token": {"type": "string", "description": "XSS token"},
                    "content": {"type": "string", "description": "评论/回复内容"},
                    "title_file": {"type": "string", "description": "标题文件路径"},
                    "content_file": {"type": "string", "description": "内容文件路径"},
                    "images": {"type": "array", "description": "图片路径列表"},
                    "video": {"type": "string", "description": "视频路径"},
                    "user_id": {"type": "string", "description": "用户ID"},
                    "comment_id": {"type": "string", "description": "评论ID"},
                },
                "required": ["action"]
            }
        }
