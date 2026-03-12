"""
Web 服务启动入口
"""
import os
from pathlib import Path

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / "config" / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from xiaohongshu_agent.web.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5003))
    print(f"🚀 启动 Web 服务: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
