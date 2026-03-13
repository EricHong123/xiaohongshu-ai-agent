#!/usr/bin/env python3
"""
服务管理面板
一键启动/停止所有服务
"""
import os
import signal
import subprocess
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json

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
    "commands": {
        "name": "命令测试",
        "description": "测试 Gateway 命令系统",
        "command": ["python3", "run_commands.py"],
        "cwd": str(PROJECT_DIR),
        "run_once": True,
    },
    "mcp": {
        "name": "MCP 服务",
        "description": "小红书自动化 MCP 服务",
        "command": ["./xiaohongshu-mcp-darwin-amd64"],
        "cwd": str(PROJECT_DIR),
    },
    "cli": {
        "name": "CLI 交互界面",
        "description": "命令行交互界面",
        "command": ["python3", "-m", "xiaohongshu_agent", "--gui"],
        "cwd": str(PROJECT_DIR),
    },
}

# 运行中的服务
running_services = {}

def start_service(service_id: str) -> dict:
    """启动服务"""
    if service_id in running_services:
        return {"success": False, "error": "服务已在运行"}

    service = SERVICES.get(service_id)
    if not service:
        return {"success": False, "error": "未找到服务"}

    try:
        # 设置环境变量，禁用代理
        env = os.environ.copy()
        for var in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
            env.pop(var, None)

        process = subprocess.Popen(
            service["command"],
            cwd=service.get("cwd", str(PROJECT_DIR)),
            env=env,
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
                status[service_id] = {
                    "name": service["name"],
                    "status": "stopped",
                }
        else:
            status[service_id] = {
                "name": service["name"],
                "description": service.get("description"),
                "status": "stopped",
                "port": service.get("port"),
                "url": service.get("url"),
            }
    return status

# HTTP 服务器
HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书 AI Agent 控制面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2rem;
        }
        .services {
            display: grid;
            gap: 15px;
        }
        .service-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .service-card:hover {
            transform: translateY(-2px);
        }
        .service-info h3 {
            color: #333;
            margin-bottom: 5px;
        }
        .service-info p {
            color: #666;
            font-size: 0.9rem;
        }
        .service-info .port {
            color: #999;
            font-size: 0.8rem;
            margin-top: 3px;
        }
        .status {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .status.running {
            background: #10b981;
            color: white;
        }
        .status.stopped {
            background: #ef4444;
            color: white;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-start {
            background: #10b981;
            color: white;
        }
        .btn-start:hover {
            background: #059669;
        }
        .btn-stop {
            background: #ef4444;
            color: white;
        }
        .btn-stop:hover {
            background: #dc2626;
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .actions {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 小红书 AI Agent 控制面板</h1>
        <div class="services" id="services"></div>
    </div>
    <button class="refresh-btn" onclick="refresh()">🔄 刷新</button>

    <script>
        async function refresh() {
            const response = await fetch('/api/status');
            const services = await response.json();

            const container = document.getElementById('services');
            container.innerHTML = '';

            for (const [id, service] of Object.entries(services)) {
                const card = document.createElement('div');
                card.className = 'service-card';

                const portInfo = service.port ? `端口: ${service.port}` : '';
                const urlInfo = service.url ? `<a href="${service.url}" target="_blank">${service.url}</a>` : '';

                card.innerHTML = `
                    <div class="service-info">
                        <h3>${service.name}</h3>
                        <p>${service.description || ''}</p>
                        <div class="port">${portInfo} ${urlInfo}</div>
                    </div>
                    <div class="actions">
                        <span class="status ${service.status}">${service.status === 'running' ? '运行中' : '已停止'}</span>
                        ${service.status === 'running'
                            ? `<button class="btn btn-stop" onclick="stop('${id}')">停止</button>`
                            : `<button class="btn btn-start" onclick="start('${id}')">启动</button>`
                        }
                    </div>
                `;
                container.appendChild(card);
            }
        }

        async function start(id) {
            await fetch('/api/start/' + id, { method: 'POST' });
            refresh();
        }

        async function stop(id) {
            await fetch('/api/stop/' + id, { method: 'POST' });
            refresh();
        }

        refresh();
        setInterval(refresh, 5000);
    </script>
</body>
</html>
"""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_status()).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/start/'):
            service_id = self.path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(start_service(service_id)).encode())
        elif self.path.startswith('/api/stop/'):
            service_id = self.path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stop_service(service_id)).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # 禁用日志

def run_server(port=5000):
    """运行管理面板服务器"""
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║     🤖 小红书 AI Agent 控制面板                           ║
╠═══════════════════════════════════════════════════════════╣
║  控制面板: http://127.0.0.1:{port}/                        ║
╚═══════════════════════════════════════════════════════════╝
    """)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
