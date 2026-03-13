#!/usr/bin/env python3
"""
小红书 AI Agent 控制面板 V2
一站式管理所有服务、功能和配置
"""
import os
import signal
import subprocess
import threading
import time
import sqlite3
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import datetime

# 项目根目录
PROJECT_DIR = Path(__file__).parent

# 服务配置
SERVICES = {
    "web": {
        "name": "Web UI",
        "description": "小红书 AI Agent 网页界面",
        "command": ["python3", "-m", "xiaohongshu_agent.web"],
        "port": 5003,
        "url": "http://127.0.0.1:5003/",
        "cwd": str(PROJECT_DIR),
    },
    "gateway": {
        "name": "Gateway 服务器",
        "description": "V2 Gateway API + WebSocket",
        "command": ["python3", "run_server.py"],
        "port": 3000,
        "url": "http://127.0.0.1:3000/",
        "cwd": str(PROJECT_DIR),
    },
    "mcp": {
        "name": "MCP 服务",
        "description": "小红书自动化 MCP 服务",
        "command": ["./xiaohongshu-mcp-darwin-amd64"],
        "cwd": str(PROJECT_DIR),
    },
}

# 运行中的服务
running_services = {}

def get_env():
    """获取环境变量"""
    env = os.environ.copy()
    for var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
        env.pop(var, None)
    return env

def start_service(service_id: str) -> dict:
    """启动服务"""
    if service_id in running_services:
        return {"success": False, "error": "服务已在运行"}

    service = SERVICES.get(service_id)
    if not service:
        return {"success": False, "error": "未找到服务"}

    try:
        process = subprocess.Popen(
            service["command"],
            cwd=service.get("cwd", str(PROJECT_DIR)),
            env=get_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None,
        )

        running_services[service_id] = {
            "process": process,
            "service": service,
            "started_at": time.time(),
        }

        return {"success": True, "message": f"{service['name']} 已启动"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def stop_service(service_id: str) -> dict:
    """停止服务"""
    if service_id not in running_services:
        return {"success": False, "error": "服务未运行"}

    try:
        service_info = running_services[service_id]
        process = service_info["process"]

        if os.name == 'nt':
            process.terminate()
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        del running_services[service_id]
        return {"success": True, "message": f"{SERVICES[service_id]['name']} 已停止"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def get_status() -> dict:
    """获取所有服务状态"""
    status = {}
    for service_id, service in SERVICES.items():
        info = running_services.get(service_id)
        if info:
            process = info["process"]
            if process.poll() is None:
                status[service_id] = {
                    "name": service["name"],
                    "status": "running",
                    "port": service.get("port"),
                    "url": service.get("url"),
                }
            else:
                del running_services[service_id]
                status[service_id] = {"name": service["name"], "status": "stopped"}
        else:
            status[service_id] = {
                "name": service["name"],
                "description": service.get("description"),
                "status": "stopped",
                "port": service.get("port"),
                "url": service.get("url"),
            }
    return status

# ==================== xhs_automation 功能 ====================

def run_xhs_command(args: list) -> dict:
    """运行 xhs_automation 命令"""
    try:
        cmd = ["python3", "xhs_automation/cli.py"] + args
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_DIR),
            env=get_env(),
            capture_output=True,
            text=True,
            timeout=60
        )
        try:
            output = json.loads(result.stdout) if result.stdout else {}
        except:
            output = {"raw": result.stdout, "stderr": result.stderr}

        return {
            "success": result.returncode == 0,
            "data": output,
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_xhs_status() -> dict:
    """获取小红书状态"""
    result = run_xhs_command(["check-login"])
    return result

def xhs_login() -> dict:
    """获取登录二维码"""
    return run_xhs_command(["get-qrcode"])

def xhs_search(keyword: str) -> dict:
    """搜索"""
    return run_xhs_command(["search-feeds", "--keyword", keyword])

def xhs_list_accounts() -> dict:
    """列出账号"""
    return run_xhs_command(["list-accounts"])

# ==================== 数据库功能 ====================

def get_database_info() -> dict:
    """获取数据库信息"""
    db_path = PROJECT_DIR / "xiaohongshu_agent.db"
    if not db_path.exists():
        return {"exists": False}

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        info = {"exists": True, "path": str(db_path), "tables": {}}

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            info["tables"][table] = count

        conn.close()
        return info
    except Exception as e:
        return {"exists": True, "error": str(e)}

def get_recent_logs(limit: int = 50) -> list:
    """获取最近日志"""
    log_dir = PROJECT_DIR / "logs"
    if not log_dir.exists():
        return []

    logs = []
    for log_file in sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        try:
            lines = log_file.read_text(encoding='utf-8').strip().split('\n')
            logs.extend([f"[{log_file.name}] {line}" for line in lines[-limit:]])
        except:
            pass

    return logs[-limit:]

# ==================== 配置功能 ====================

def get_config() -> dict:
    """获取配置"""
    config = {}

    # 环境变量
    env_vars = [
        "LLM_PROVIDER", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
        "ZHIPU_API_KEY", "KIMI_API_KEY", "MINIMAX_API_KEY",
        "GEMINI_API_KEY", "KLING_API_KEY"
    ]

    for var in env_vars:
        value = os.environ.get(var, "")
        config[var] = "***已设置***" if value else "未设置"

    return config

def get_system_info() -> dict:
    """获取系统信息"""
    import platform

    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "project_dir": str(PROJECT_DIR),
        "uptime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ==================== 命令执行 ====================

def run_cli_command(args: list) -> dict:
    """运行 CLI 命令"""
    try:
        cmd = ["python3", "-m", "xiaohongshu_agent"] + args
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_DIR),
            env=get_env(),
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== HTTP 服务器 ====================

HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书 AI Agent 控制中心</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 { font-size: 1.5rem; }
        .header .time { color: #888; font-size: 0.9rem; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 {
            font-size: 1.1rem;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card h2 .icon { font-size: 1.3rem; }

        /* 服务卡片 */
        .service-list { display: flex; flex-direction: column; gap: 12px; }
        .service-item {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .service-info h3 { font-size: 0.95rem; margin-bottom: 3px; }
        .service-info p { font-size: 0.8rem; color: #888; }
        .service-info a { color: #4fc3f7; text-decoration: none; }
        .status {
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .status.running { background: #10b981; }
        .status.stopped { background: #ef4444; }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        .btn-start { background: #10b981; color: white; }
        .btn-start:hover { background: #059669; }
        .btn-stop { background: #ef4444; color: white; }
        .btn-stop:hover { background: #dc2626; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }

        /* 小红书状态 */
        .xhs-status { text-align: center; padding: 20px; }
        .xhs-status .icon { font-size: 3rem; margin-bottom: 10px; }
        .xhs-status .logged-in { color: #10b981; }
        .xhs-status .logged-out { color: #ef4444; }
        .btn-group { display: flex; gap: 10px; justify-content: center; margin-top: 15px; }
        .btn-group .btn { padding: 10px 20px; }

        /* 搜索 */
        .search-box { display: flex; gap: 10px; }
        .search-box input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 0.9rem;
        }
        .search-box input:focus { outline: none; border-color: #4fc3f7; }
        .search-results {
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        .search-result-item {
            background: rgba(0,0,0,0.2);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 0.85rem;
        }

        /* 日志 */
        .log-container {
            background: #0a0a0a;
            border-radius: 8px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            line-height: 1.5;
        }
        .log-item { color: #888; margin-bottom: 3px; }
        .log-item.error { color: #ef4444; }
        .log-item.warning { color: #f59e0b; }

        /* 配置 */
        .config-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .config-item {
            background: rgba(0,0,0,0.3);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.85rem;
        }
        .config-item .key { color: #888; margin-bottom: 3px; }
        .config-item .value { color: #4fc3f7; }

        /* 系统信息 */
        .sys-info { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .sys-item {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .sys-item .value { font-size: 1.5rem; color: #4fc3f7; }
        .sys-item .label { font-size: 0.8rem; color: #888; margin-top: 5px; }

        /* 数据库 */
        .db-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .db-item {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .db-item .value { font-size: 1.2rem; color: #4fc3f7; }
        .db-item .label { font-size: 0.75rem; color: #888; margin-top: 5px; }

        /* Tab 导航 */
        .tabs { display: flex; gap: 5px; margin-bottom: 20px; }
        .tab {
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border: none;
            border-radius: 8px 8px 0 0;
            color: #888;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab.active { background: rgba(255,255,255,0.1); color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* 控制台输出 */
        .console-output {
            background: #0a0a0a;
            border-radius: 8px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            white-space: pre-wrap;
            color: #10b981;
        }

        /* 快捷操作 */
        .quick-actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .quick-action {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        .quick-action:hover { border-color: #4fc3f7; }
        .quick-action .icon { font-size: 1.5rem; margin-bottom: 8px; }
        .quick-action .label { font-size: 0.85rem; }

        /* 刷新按钮 */
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            color: white;
            border: none;
        }
        .refresh-btn:hover { background: rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 小红书 AI Agent 控制中心</h1>
        <div class="time" id="time"></div>
    </div>

    <div class="container">
        <!-- Tab 导航 -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('services')">🚀 服务</button>
            <button class="tab" onclick="showTab('xhs')">📕 小红书</button>
            <button class="tab" onclick="showTab('tools')">🛠️ 工具</button>
            <button class="tab" onclick="showTab('logs')">📋 日志</button>
            <button class="tab" onclick="showTab('config')">⚙️ 配置</button>
            <button class="tab" onclick="showTab('system')">💻 系统</button>
        </div>

        <!-- 服务管理 -->
        <div id="services" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h2><span class="icon">🚀</span> 服务管理</h2>
                    <div class="service-list" id="service-list"></div>
                </div>
                <div class="card">
                    <h2><span class="icon">⚡</span> 快捷操作</h2>
                    <div class="quick-actions">
                        <div class="quick-action" onclick="runCommand(['--stats'])">
                            <div class="icon">📊</div>
                            <div class="label">查看统计</div>
                        </div>
                        <div class="quick-action" onclick="runCommand(['--config'])">
                            <div class="icon">⚙️</div>
                            <div class="label">查看配置</div>
                        </div>
                        <div class="quick-action" onclick="runCommand(['--gui'])">
                            <div class="icon">💬</div>
                            <div class="label">交互模式</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <h3 style="font-size: 0.9rem; margin-bottom: 10px;">命令输出:</h3>
                        <div class="console-output" id="console-output">等待命令...</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 小红书 -->
        <div id="xhs" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2><span class="icon">📕</span> 登录状态</h2>
                    <div class="xhs-status" id="xhs-status">
                        <div class="icon">⏳</div>
                        <div>检查中...</div>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-start" onclick="xhsLogin()">获取二维码</button>
                        <button class="btn" style="background: #4fc3f7; color: white;" onclick="refreshXhs()">刷新</button>
                    </div>
                </div>
                <div class="card">
                    <h2><span class="icon">🔍</span> 搜索笔记</h2>
                    <div class="search-box">
                        <input type="text" id="search-keyword" placeholder="输入搜索关键词..." onkeypress="if(event.key==='Enter')xhsSearch()">
                        <button class="btn btn-start" onclick="xhsSearch()">搜索</button>
                    </div>
                    <div class="search-results" id="search-results"></div>
                </div>
                <div class="card">
                    <h2><span class="icon">👥</span> 账号管理</h2>
                    <div id="account-list"></div>
                </div>
            </div>
        </div>

        <!-- 工具 -->
        <div id="tools" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2><span class="icon">📊</span> 数据库统计</h2>
                    <div class="db-stats" id="db-stats"></div>
                </div>
                <div class="card">
                    <h2><span class="icon">📁</span> 文件信息</h2>
                    <div class="config-list" id="file-info"></div>
                </div>
            </div>
        </div>

        <!-- 日志 -->
        <div id="logs" class="tab-content">
            <div class="card">
                <h2><span class="icon">📋</span> 运行日志</h2>
                <div class="log-container" id="log-container"></div>
            </div>
        </div>

        <!-- 配置 -->
        <div id="config" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2><span class="icon">⚙️</span> 环境变量配置</h2>
                    <div class="config-list" id="config-list"></div>
                </div>
                <div class="card">
                    <h2><span class="icon">🔑</span> API 密钥设置</h2>
                    <div style="padding: 20px; text-align: center; color: #888;">
                        <p>请在终端设置环境变量：</p>
                        <pre style="margin-top: 15px; text-align: left; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-size: 0.8rem;">
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export ZHIPU_API_KEY="your-key"
export KIMI_API_KEY="your-key"
export MINIMAX_API_KEY="your-key"
                        </pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- 系统 -->
        <div id="system" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2><span class="icon">💻</span> 系统信息</h2>
                    <div class="sys-info" id="sys-info"></div>
                </div>
                <div class="card">
                    <h2><span class="icon">📂</span> 项目结构</h2>
                    <div style="padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; font-size: 0.85rem; line-height: 1.8;">
                        <div>📁 xiaohongshu_agent/</div>
                        <div style="padding-left: 20px; color: #888;">├── gateway/ (V2 网关)</div>
                        <div style="padding-left: 20px; color: #888;">├── agent/ (Agent 核心)</div>
                        <div style="padding-left: 20px; color: #888;">├── providers/ (LLM 提供商)</div>
                        <div style="padding-left: 20px; color: #888;">├── web/ (网页界面)</div>
                        <div>📁 xhs_automation/</div>
                        <div style="padding-left: 20px; color: #888;">├── cli.py (自动化 CLI)</div>
                        <div>📁 config/ (配置文件)</div>
                        <div>📁 logs/ (日志目录)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <button class="refresh-btn" onclick="refreshAll()">🔄 刷新</button>

    <script>
        // Tab 切换
        function showTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }

        // 更新时间
        function updateTime() {
            document.getElementById('time').textContent = new Date().toLocaleString('zh-CN');
        }
        setInterval(updateTime, 1000);
        updateTime();

        // 刷新所有
        function refreshAll() {
            refreshServices();
            refreshXhs();
            refreshLogs();
            refreshConfig();
            refreshSystem();
            refreshDb();
        }

        // 服务管理
        async function refreshServices() {
            const response = await fetch('/api/services');
            const services = await response.json();

            const container = document.getElementById('service-list');
            container.innerHTML = '';

            for (const [id, service] of Object.entries(services)) {
                const item = document.createElement('div');
                item.className = 'service-item';
                item.innerHTML = `
                    <div class="service-info">
                        <h3>${service.name}</h3>
                        <p>${service.description || ''} ${service.port ? '端口: ' + service.port : ''}</p>
                        ${service.url ? `<a href="${service.url}" target="_blank">${service.url}</a>` : ''}
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span class="status ${service.status}">${service.status === 'running' ? '运行中' : '已停止'}</span>
                        ${service.status === 'running'
                            ? `<button class="btn btn-stop" onclick="stopService('${id}')">停止</button>`
                            : `<button class="btn btn-start" onclick="startService('${id}')">启动</button>`
                        }
                    </div>
                `;
                container.appendChild(item);
            }
        }

        async function startService(id) {
            await fetch('/api/service/start/' + id, { method: 'POST' });
            refreshServices();
        }

        async function stopService(id) {
            await fetch('/api/service/stop/' + id, { method: 'POST' });
            refreshServices();
        }

        // 小红书状态
        async function refreshXhs() {
            const response = await fetch('/api/xhs/status');
            const result = await response.json();

            const container = document.getElementById('xhs-status');
            if (result.success && result.data && result.data.logged_in) {
                container.innerHTML = `
                    <div class="icon logged-in">✅</div>
                    <div class="logged-in">已登录</div>
                `;
            } else {
                container.innerHTML = `
                    <div class="icon logged-out">❌</div>
                    <div class="logged-out">未登录</div>
                `;
            }

            // 账号列表
            const accountsRes = await fetch('/api/xhs/accounts');
            const accountsResult = await accountsRes.json();
            const accountContainer = document.getElementById('account-list');
            if (accountsResult.success && accountsResult.data && accountsResult.data.accounts) {
                const accounts = accountsResult.data.accounts;
                if (accounts.length > 0) {
                    accountContainer.innerHTML = accounts.map(acc => `
                        <div style="padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; margin-bottom: 8px;">
                            <strong>${acc.name}</strong>
                            <p style="color: #888; font-size: 0.8rem;">${acc.description || '无描述'}</p>
                        </div>
                    `).join('');
                } else {
                    accountContainer.innerHTML = '<div style="color: #888; text-align: center;">暂无账号</div>';
                }
            }
        }

        async function xhsLogin() {
            const response = await fetch('/api/xhs/login', { method: 'POST' });
            const result = await response.json();
            if (result.success && result.data) {
                alert('二维码已生成，请打开浏览器扫码登录');
                if (result.data.qrcode_path) {
                    // 打开二维码图片
                }
            } else {
                alert('获取二维码失败: ' + (result.error || '未知错误'));
            }
            refreshXhs();
        }

        async function xhsSearch() {
            const keyword = document.getElementById('search-keyword').value;
            if (!keyword) return;

            const response = await fetch('/api/xhs/search?keyword=' + encodeURIComponent(keyword));
            const result = await response.json();

            const container = document.getElementById('search-results');
            if (result.success && result.data && result.data.feeds) {
                const feeds = result.data.feeds;
                if (feeds.length > 0) {
                    container.innerHTML = feeds.slice(0, 10).map(feed => `
                        <div class="search-result-item">
                            <div>${feed.title || '无标题'}</div>
                            <div style="color: #888; font-size: 0.75rem; margin-top: 5px;">
                                👍 ${feed.likes || 0} | 💬 ${feed.comments || 0} | ⭐ ${feed.collects || 0}
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div style="color: #888; text-align: center;">未找到相关笔记</div>';
                }
            } else {
                container.innerHTML = '<div style="color: #ef4444;">搜索失败: ' + (result.error || '未知错误') + '</div>';
            }
        }

        // 日志
        async function refreshLogs() {
            const response = await fetch('/api/logs');
            const logs = await response.json();

            const container = document.getElementById('log-container');
            if (logs.length > 0) {
                container.innerHTML = logs.slice(-30).map(log => {
                    let cls = 'log-item';
                    if (log.includes('ERROR')) cls += ' error';
                    else if (log.includes('WARNING')) cls += ' warning';
                    return `<div class="${cls}">${log}</div>`;
                }).join('');
            } else {
                container.innerHTML = '<div style="color: #888; text-align: center;">暂无日志</div>';
            }
        }

        // 配置
        async function refreshConfig() {
            const response = await fetch('/api/config');
            const config = await response.json();

            const container = document.getElementById('config-list');
            container.innerHTML = Object.entries(config).map(([key, value]) => `
                <div class="config-item">
                    <div class="key">${key}</div>
                    <div class="value">${value}</div>
                </div>
            `).join('');
        }

        // 系统信息
        async function refreshSystem() {
            const response = await fetch('/api/system');
            const info = await response.json();

            const container = document.getElementById('sys-info');
            container.innerHTML = `
                <div class="sys-item">
                    <div class="value">${info.platform ? info.platform.split(' ')[0] : '-'}</div>
                    <div class="label">系统</div>
                </div>
                <div class="sys-item">
                    <div class="value">${info.python || '-'}</div>
                    <div class="label">Python 版本</div>
                </div>
                <div class="sys-item">
                    <div class="value">${info.uptime || '-'}</div>
                    <div class="label">启动时间</div>
                </div>
            `;

            // 文件信息
            const fileInfo = document.getElementById('file-info');
            fileInfo.innerHTML = `
                <div class="config-item">
                    <div class="key">项目目录</div>
                    <div class="value" style="font-size: 0.75rem;">${info.project_dir || '-'}</div>
                </div>
            `;
        }

        // 数据库
        async function refreshDb() {
            const response = await fetch('/api/database');
            const db = await response.json();

            const container = document.getElementById('db-stats');
            if (db.exists && !db.error) {
                const tables = Object.entries(db.tables || {});
                const total = tables.reduce((sum, [, count]) => sum + count, 0);
                container.innerHTML = `
                    <div class="db-item">
                        <div class="value">${tables.length}</div>
                        <div class="label">数据表</div>
                    </div>
                    <div class="db-item">
                        <div class="value">${total}</div>
                        <div class="label">总记录</div>
                    </div>
                    <div class="db-item">
                        <div class="value" style="font-size: 0.9rem;">${(db.path || '').split('/').pop()}</div>
                        <div class="label">数据库文件</div>
                    </div>
                `;
            } else {
                container.innerHTML = '<div style="grid-column: span 3; color: #888; text-align: center;">数据库不存在</div>';
            }
        }

        // 运行命令
        async function runCommand(args) {
            const response = await fetch('/api/cli?' + new URLSearchParams({args: args.join(',')}));
            const result = await response.json();

            const container = document.getElementById('console-output');
            if (result.success) {
                container.textContent = result.stdout || result.stderr || '命令执行成功';
            } else {
                container.textContent = '错误: ' + (result.error || result.stderr);
            }
        }

        // 初始化
        refreshAll();
        setInterval(refreshAll, 10000);
    </script>
</body>
</html>
"""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/services':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_status()).encode())

        elif path == '/api/xhs/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_xhs_status()).encode())

        elif path == '/api/xhs/accounts':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(xhs_list_accounts()).encode())

        elif path.startswith('/api/xhs/search'):
            keyword = parse_qs(parsed.query).get('keyword', [''])[0]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(xhs_search(keyword)).encode())

        elif path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_recent_logs()).encode())

        elif path == '/api/config':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_config()).encode())

        elif path == '/api/system':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_system_info()).encode())

        elif path == '/api/database':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_database_info()).encode())

        elif path.startswith('/api/cli'):
            args = parse_qs(parsed.query).get('args', [''])[0].split(',') if parse_qs(parsed.query).get('args') else []
            args = [a for a in args if a]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(run_cli_command(args)).encode())

        elif path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/xhs/login':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(xhs_login()).encode())

        elif path.startswith('/api/service/start/'):
            service_id = path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(start_service(service_id)).encode())

        elif path.startswith('/api/service/stop/'):
            service_id = path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stop_service(service_id)).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║        🤖 小红书 AI Agent 控制中心 V2                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  控制面板: http://127.0.0.1:{port}/                               ║
║  访问局域网: http://你的IP:{port}/                                 ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
