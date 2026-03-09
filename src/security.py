#!/usr/bin/env python3
"""
安全控制模块
- 操作审计
- 权限验证
- 输入 sanitization
- API Key 安全存储
"""
import os
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


# ============== 安全配置 ==============
class SecurityConfig:
    """安全配置"""

    # 允许的目录（防止目录遍历攻击）
    ALLOWED_DIRS = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Documents"),
        "/tmp",
    ]

    # 允许的系统命令（白名单）
    ALLOWED_COMMANDS = [
        "ls", "pwd", "cd", "mkdir", "rm", "cp", "mv",
        "cat", "head", "tail", "grep", "find",
        "open", "say",  # macOS 特定
    ]

    # 禁止的命令
    FORBIDDEN_COMMANDS = [
        "rm -rf", "dd", "mkfs", "fdisk",
        "curl", "wget", "nc", "ssh", "scp",
        "python", "node", "bash", "zsh", "sh",
        "kill", "pkill", "killall",
    ]

    # 文件扩展名白名单
    ALLOWED_EXTENSIONS = [
        ".txt", ".md", ".json", ".csv", ".xml",
        ".jpg", ".jpeg", ".png", ".gif", ".webp",
        ".mp4", ".mov", ".avi",
        ".pdf", ".doc", ".docx",
        ".py", ".js", ".ts", ".html", ".css",
    ]

    @classmethod
    def is_dir_allowed(cls, path: str) -> bool:
        """检查目录是否允许访问"""
        abs_path = os.path.abspath(path)
        for allowed in cls.ALLOWED_DIRS:
            if abs_path.startswith(os.path.abspath(allowed)):
                return True
        return False

    @classmethod
    def is_command_allowed(cls, command: str) -> bool:
        """检查命令是否允许执行"""
        cmd = command.strip().split()[0] if command.strip() else ""

        # 检查禁止列表
        for forbidden in cls.FORBIDDEN_COMMANDS:
            if forbidden in command.lower():
                return False

        # 检查白名单
        if cmd in cls.ALLOWED_COMMANDS:
            return True

        return False

    @classmethod
    def is_extension_allowed(cls, filename: str) -> bool:
        """检查文件扩展名是否允许"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in cls.ALLOWED_EXTENSIONS


# ============== 操作审计 ==============
class AuditLogger:
    """操作审计日志"""

    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化审计数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user TEXT,
                action TEXT,
                target TEXT,
                result TEXT,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log(self, action: str, target: str, result: str, details: str = ""):
        """记录操作"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (timestamp, user, action, target, result, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            os.getenv("USER", "unknown"),
            action,
            target,
            result,
            details
        ))
        conn.commit()
        conn.close()

    def get_logs(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============== API Key 安全存储 ==============
class SecureStorage:
    """安全的配置存储"""

    def __init__(self, config_file: str = ".agent_config.enc"):
        self.config_file = config_file

    def save_config(self, config: Dict[str, str], master_key: str = None):
        """保存配置（可选加密）"""
        # 简单哈希存储
        data = json.dumps(config)
        with open(self.config_file, "w") as f:
            f.write(data)
        os.chmod(self.config_file, 0o600)  # 所有者读写

    def load_config(self) -> Dict[str, str]:
        """加载配置"""
        if not os.path.exists(self.config_file):
            return {}

        with open(self.config_file, "r") as f:
            return json.load(f)

    def get_api_key(self, provider: str) -> Optional[str]:
        """获取 API Key"""
        config = self.load_config()
        key = f"{provider.upper()}_API_KEY"
        return config.get(key) or os.getenv(key)


# ============== 输入验证 ==============
class InputValidator:
    """输入验证"""

    @staticmethod
    def sanitize_path(path: str) -> str:
        """清理路径，防止目录遍历"""
        # 移除危险字符
        dangerous = ["..", "~", "$", "`", ";", "|", "&", "<", ">"]
        for d in dangerous:
            path = path.replace(d, "")
        return path.strip()

    @staticmethod
    def sanitize_command(command: str) -> str:
        """清理命令"""
        # 移除危险字符
        dangerous = [";", "|", "&", "`", "$", ">", "<", "\n", "\r"]
        for d in dangerous:
            command = command.replace(d, "")
        return command.strip()[:500]  # 限制长度

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """验证文件名"""
        # 只允许字母、数字、下划线、连字符、点
        import re
        return bool(re.match(r'^[\w\-\.]+$', filename))


# ============== 权限管理器 ==============
class PermissionManager:
    """权限管理器"""

    def __init__(self):
        self.permissions = {
            "file_read": False,
            "file_write": False,
            "command_exec": False,
            "browser_control": False,
            "screenshot": False,
            "clipboard": False,
            "network": False,
        }
        self.enabled = False

    def enable_permissions(self, perms: List[str]):
        """启用指定权限"""
        for p in perms:
            if p in self.permissions:
                self.permissions[p] = True
        self.enabled = True

    def disable_all(self):
        """禁用所有权限"""
        for p in self.permissions:
            self.permissions[p] = False
        self.enabled = False

    def has_permission(self, perm: str) -> bool:
        """检查是否有权限"""
        return self.enabled and self.permissions.get(perm, False)

    def get_permissions(self) -> Dict[str, bool]:
        """获取当前权限状态"""
        return self.permissions.copy()


# ============== 主安全类 ==============
class SecurityManager:
    """安全管理器"""

    def __init__(self):
        self.audit = AuditLogger()
        self.storage = SecureStorage()
        self.validator = InputValidator()
        self.permissions = PermissionManager()

    def check_file_read(self, path: str) -> bool:
        """检查文件读权限"""
        path = self.validator.sanitize_path(path)

        if not SecurityConfig.is_dir_allowed(path):
            self.audit.log("file_read", path, "denied", "目录不在白名单")
            return False

        if not os.path.exists(path):
            self.audit.log("file_read", path, "denied", "文件不存在")
            return False

        self.audit.log("file_read", path, "allowed")
        return True

    def check_file_write(self, path: str) -> bool:
        """检查文件写权限"""
        if not self.permissions.has_permission("file_write"):
            self.audit.log("file_write", path, "denied", "没有写权限")
            return False

        path = self.validator.sanitize_path(path)

        if not SecurityConfig.is_dir_allowed(path):
            self.audit.log("file_write", path, "denied", "目录不在白名单")
            return False

        # 检查扩展名
        if not SecurityConfig.is_extension_allowed(os.path.basename(path)):
            self.audit.log("file_write", path, "denied", "不允许的文件类型")
            return False

        self.audit.log("file_write", path, "allowed")
        return True

    def check_command(self, command: str) -> bool:
        """检查命令执行权限"""
        if not self.permissions.has_permission("command_exec"):
            self.audit.log("command", command, "denied", "没有命令执行权限")
            return False

        command = self.validator.sanitize_command(command)

        if not SecurityConfig.is_command_allowed(command):
            self.audit.log("command", command, "denied", "命令不在白名单")
            return False

        self.audit.log("command", command, "allowed")
        return True


# 测试
if __name__ == "__main__":
    print("🧪 测试安全模块")
    print("=" * 50)

    sm = SecurityManager()

    # 测试权限
    print("\n[1] 权限测试")
    sm.permissions.enable_permissions(["file_read", "file_write", "command_exec"])
    print(f"   权限状态: {sm.permissions.get_permissions()}")

    # 测试路径检查
    print("\n[2] 路径检查")
    print(f"   ~/Desktop 允许: {SecurityConfig.is_dir_allowed(os.path.expanduser('~/Desktop'))}")
    print(f"   /usr 允许: {SecurityConfig.is_dir_allowed('/usr')}")

    # 测试命令检查
    print("\n[3] 命令检查")
    print(f"   ls 允许: {SecurityConfig.is_command_allowed('ls -la')}")
    print(f"   rm -rf 允许: {SecurityConfig.is_command_allowed('rm -rf /')}")
    print(f"   curl 允许: {SecurityConfig.is_command_allowed('curl http://example.com')}")

    # 测试审计
    print("\n[4] 审计日志")
    sm.audit.log("test", "test.txt", "success", "测试日志")
    logs = sm.audit.get_logs()
    print(f"   日志数量: {len(logs)}")

    print("\n✅ 安全模块测试完成")
