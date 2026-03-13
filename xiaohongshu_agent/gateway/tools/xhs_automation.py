"""
xhs_automation CLI 封装层
将命令行工具封装为 Python 类，供 Agent 调用
"""
import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

# xhs_automation 路径
XHS_AUTOMATION_DIR = Path(__file__).parent.parent.parent.parent / "xhs_automation"
CLI_PATH = XHS_AUTOMATION_DIR / "cli.py"


class XHSAutomation:
    """小红书自动化工具封装"""

    def __init__(self, account: str = "", port: int = 9222):
        self.account = account
        self.port = port
        self.host = "127.0.0.1"

    def _build_args(self, command: str, **kwargs) -> List[str]:
        """构建命令行参数 - 全局选项必须在子命令之前"""
        args = ["python3", str(CLI_PATH)]
        # 全局选项 (必须在子命令之前)
        args.extend(["--host", self.host])
        args.extend(["--port", str(self.port)])
        if self.account:
            args.extend(["--account", self.account])
        # 子命令
        args.append(command)
        # 子命令参数
        for key, value in kwargs.items():
            if value is not None and value is not False:
                flag = f"--{key.replace('_', '-')}"
                if value is True:
                    args.append(flag)
                else:
                    args.extend([flag, str(value)])

        return args

    async def _run(self, command: str, **kwargs) -> Dict[str, Any]:
        """执行 CLI 命令"""
        args = self._build_args(command, **kwargs)

        # 禁用代理，避免 502 错误
        env = os.environ.copy()
        env.pop("http_proxy", None)
        env.pop("https_proxy", None)
        env.pop("HTTP_PROXY", None)
        env.pop("HTTPS_PROXY", None)

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(XHS_AUTOMATION_DIR),
                env=env
            )

            try:
                output = json.loads(result.stdout) if result.stdout else {}
            except json.JSONDecodeError:
                output = {"raw": result.stdout, "stderr": result.stderr}

            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "data": output,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 登录相关 ====================

    async def check_login(self) -> Dict[str, Any]:
        """检查登录状态"""
        return await self._run("check-login")

    async def get_qrcode(self) -> Dict[str, Any]:
        """获取登录二维码"""
        return await self._run("get-qrcode")

    async def wait_login(self, timeout: float = 120) -> Dict[str, Any]:
        """等待扫码登录"""
        return await self._run("wait-login", timeout=timeout)

    async def phone_login(self, phone: str, code: str = "") -> Dict[str, Any]:
        """手机号验证码登录"""
        return await self._run("phone-login", phone=phone, code=code)

    async def logout(self) -> Dict[str, Any]:
        """退出登录"""
        return await self._run("delete-cookies")

    # ==================== 内容获取 ====================

    async def list_feeds(self) -> Dict[str, Any]:
        """获取首页 Feed"""
        return await self._run("list-feeds")

    async def search(
        self,
        keyword: str,
        sort_by: str = "",
        note_type: str = "",
        publish_time: str = ""
    ) -> Dict[str, Any]:
        """搜索内容"""
        return await self._run(
            "search-feeds",
            keyword=keyword,
            sort_by=sort_by,
            note_type=note_type,
            publish_time=publish_time
        )

    async def get_feed_detail(
        self,
        feed_id: str,
        xsec_token: str,
        load_all_comments: bool = False
    ) -> Dict[str, Any]:
        """获取笔记详情"""
        return await self._run(
            "get-feed-detail",
            feed_id=feed_id,
            xsec_token=xsec_token,
            load_all_comments=load_all_comments
        )

    async def get_user_profile(self, user_id: str, xsec_token: str) -> Dict[str, Any]:
        """获取用户主页"""
        return await self._run(
            "user-profile",
            user_id=user_id,
            xsec_token=xsec_token
        )

    # ==================== 互动操作 ====================

    async def like(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """点赞"""
        return await self._run(
            "like-feed",
            feed_id=feed_id,
            xsec_token=xsec_token
        )

    async def unlike(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """取消点赞"""
        return await self._run(
            "like-feed",
            feed_id=feed_id,
            xsec_token=xsec_token,
            unlike=True
        )

    async def favorite(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """收藏"""
        return await self._run(
            "favorite-feed",
            feed_id=feed_id,
            xsec_token=xsec_token
        )

    async def unfavorite(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """取消收藏"""
        return await self._run(
            "favorite-feed",
            feed_id=feed_id,
            xsec_token=xsec_token,
            unfavorite=True
        )

    async def comment(self, feed_id: str, xsec_token: str, content: str) -> Dict[str, Any]:
        """发表评论"""
        return await self._run(
            "post-comment",
            feed_id=feed_id,
            xsec_token=xsec_token,
            content=content
        )

    async def reply(
        self,
        feed_id: str,
        xsec_token: str,
        content: str,
        comment_id: str = "",
        user_id: str = ""
    ) -> Dict[str, Any]:
        """回复评论"""
        return await self._run(
            "reply-comment",
            feed_id=feed_id,
            xsec_token=xsec_token,
            content=content,
            comment_id=comment_id,
            user_id=user_id
        )

    # ==================== 发布 ====================

    async def publish(
        self,
        title: str,
        content: str,
        images: List[str],
        tags: Optional[List[str]] = None,
        original: bool = False
    ) -> Dict[str, Any]:
        """发布图文笔记"""

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tf:
            title_file = tf.name
            tf.write(title)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as cf:
            content_file = cf.name
            cf.write(content)

        try:
            result = await self._run(
                "publish",
                title_file=title_file,
                content_file=content_file,
                images=images,
                tags=tags or [],
                original=original
            )
        finally:
            # 清理临时文件
            for f in [title_file, content_file]:
                try:
                    os.unlink(f)
                except:
                    pass

        return result

    async def publish_video(
        self,
        title: str,
        content: str,
        video_path: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """发布视频笔记"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tf:
            title_file = tf.name
            tf.write(title)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as cf:
            content_file = cf.name
            cf.write(content)

        try:
            result = await self._run(
                "publish-video",
                title_file=title_file,
                content_file=content_file,
                video=video_path,
                tags=tags or []
            )
        finally:
            for f in [title_file, content_file]:
                try:
                    os.unlink(f)
                except:
                    pass

        return result

    # ==================== 账号管理 ====================

    async def add_account(self, name: str, description: str = "") -> Dict[str, Any]:
        """添加账号"""
        return await self._run("add-account", name=name, description=description)

    async def list_accounts(self) -> Dict[str, Any]:
        """列出账号"""
        return await self._run("list-accounts")

    async def remove_account(self, name: str) -> Dict[str, Any]:
        """删除账号"""
        return await self._run("remove-account", name=name)


# 全局实例
_default_xhs: Optional[XHSAutomation] = None


def get_xhs_automation(account: str = "") -> XHSAutomation:
    """获取 XHS Automation 实例"""
    global _default_xhs
    if _default_xhs is None or _default_xhs.account != account:
        _default_xhs = XHSAutomation(account=account)
    return _default_xhs
