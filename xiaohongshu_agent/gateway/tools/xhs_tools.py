"""
xhs_automation 工具注册
将小红书自动化功能注册为 Gateway Tool
"""
from xiaohongshu_agent.gateway.tools.xhs_automation import get_xhs_automation


def register_xhs_tools(gateway) -> None:
    """注册小红书自动化工具"""

    # ==================== 登录工具 ====================

    gateway.register({
        "name": "xhs_check_login",
        "description": "检查小红书登录状态",
        "parameters": {
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def check_login_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.check_login()

    gateway.register_handler("xhs_check_login", check_login_handler)

    # ==================== 获取二维码 ====================

    gateway.register({
        "name": "xhs_get_qrcode",
        "description": "获取小红书登录二维码",
        "parameters": {
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def get_qrcode_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.get_qrcode()

    gateway.register_handler("xhs_get_qrcode", get_qrcode_handler)

    # ==================== 等待登录 ====================

    gateway.register({
        "name": "xhs_wait_login",
        "description": "等待扫码登录完成",
        "parameters": {
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "账号名称"},
                "timeout": {"type": "number", "description": "超时时间(秒)"}
            }
        }
    })

    async def wait_login_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.wait_login(timeout=params.get("timeout", 120))

    gateway.register_handler("xhs_wait_login", wait_login_handler)

    # ==================== 搜索 ====================

    gateway.register({
        "name": "xhs_search",
        "description": "搜索小红书笔记",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "搜索关键词"},
                "sort_by": {"type": "string", "description": "排序方式"},
                "note_type": {"type": "string", "description": "笔记类型"},
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def search_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.search(
            keyword=params.get("keyword", ""),
            sort_by=params.get("sort_by", ""),
            note_type=params.get("note_type", "")
        )

    gateway.register_handler("xhs_search", search_handler)

    # ==================== 获取 Feed 详情 ====================

    gateway.register({
        "name": "xhs_get_feed_detail",
        "description": "获取笔记详情",
        "parameters": {
            "type": "object",
            "properties": {
                "feed_id": {"type": "string", "description": "笔记ID"},
                "xsec_token": {"type": "string", "description": "xsec_token"},
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def feed_detail_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.get_feed_detail(
            feed_id=params.get("feed_id", ""),
            xsec_token=params.get("xsec_token", "")
        )

    gateway.register_handler("xhs_get_feed_detail", feed_detail_handler)

    # ==================== 点赞 ====================

    gateway.register({
        "name": "xhs_like",
        "description": "点赞笔记",
        "parameters": {
            "type": "object",
            "properties": {
                "feed_id": {"type": "string", "description": "笔记ID"},
                "xsec_token": {"type": "string", "description": "xsec_token"},
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def like_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.like(
            feed_id=params.get("feed_id", ""),
            xsec_token=params.get("xsec_token", "")
        )

    gateway.register_handler("xhs_like", like_handler)

    # ==================== 收藏 ====================

    gateway.register({
        "name": "xhs_favorite",
        "description": "收藏笔记",
        "parameters": {
            "type": "object",
            "properties": {
                "feed_id": {"type": "string", "description": "笔记ID"},
                "xsec_token": {"type": "string", "description": "xsec_token"},
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def favorite_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.favorite(
            feed_id=params.get("feed_id", ""),
            xsec_token=params.get("xsec_token", "")
        )

    gateway.register_handler("xhs_favorite", favorite_handler)

    # ==================== 评论 ====================

    gateway.register({
        "name": "xhs_comment",
        "description": "发表评论",
        "parameters": {
            "type": "object",
            "properties": {
                "feed_id": {"type": "string", "description": "笔记ID"},
                "xsec_token": {"type": "string", "description": "xsec_token"},
                "content": {"type": "string", "description": "评论内容"},
                "account": {"type": "string", "description": "账号名称"}
            }
        }
    })

    async def comment_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.comment(
            feed_id=params.get("feed_id", ""),
            xsec_token=params.get("xsec_token", ""),
            content=params.get("content", "")
        )

    gateway.register_handler("xhs_comment", comment_handler)

    # ==================== 发布图文 ====================

    gateway.register({
        "name": "xhs_publish",
        "description": "发布图文笔记",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "标题"},
                "content": {"type": "string", "description": "正文内容"},
                "images": {"type": "array", "description": "图片路径列表"},
                "tags": {"type": "array", "description": "标签列表"},
                "original": {"type": "boolean", "description": "是否原创"},
                "account": {"type": "string", "description": "账号名称"}
            },
            "required": ["title", "content", "images"]
        }
    })

    async def publish_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.publish(
            title=params.get("title", ""),
            content=params.get("content", ""),
            images=params.get("images", []),
            tags=params.get("tags", []),
            original=params.get("original", False)
        )

    gateway.register_handler("xhs_publish", publish_handler)

    # ==================== 发布视频 ====================

    gateway.register({
        "name": "xhs_publish_video",
        "description": "发布视频笔记",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "标题"},
                "content": {"type": "string", "description": "正文内容"},
                "video_path": {"type": "string", "description": "视频文件路径"},
                "tags": {"type": "array", "description": "标签列表"},
                "account": {"type": "string", "description": "账号名称"}
            },
            "required": ["title", "content", "video_path"]
        }
    })

    async def publish_video_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation(params.get("account", ""))
        return await xhs.publish_video(
            title=params.get("title", ""),
            content=params.get("content", ""),
            video_path=params.get("video_path", ""),
            tags=params.get("tags", [])
        )

    gateway.register_handler("xhs_publish_video", publish_video_handler)

    # ==================== 账号管理 ====================

    gateway.register({
        "name": "xhs_list_accounts",
        "description": "列出所有账号",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    })

    async def list_accounts_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation()
        return await xhs.list_accounts()

    gateway.register_handler("xhs_list_accounts", list_accounts_handler)

    gateway.register({
        "name": "xhs_add_account",
        "description": "添加账号",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "账号名称"},
                "description": {"type": "string", "description": "账号描述"}
            },
            "required": ["name"]
        }
    })

    async def add_account_handler(params: dict, context: dict) -> dict:
        xhs = get_xhs_automation()
        return await xhs.add_account(
            name=params.get("name", ""),
            description=params.get("description", "")
        )

    gateway.register_handler("xhs_add_account", add_account_handler)
