#!/bin/bash
# 小红书 AI Agent 启动脚本

# 项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 加载环境变量
if [ -f "config/.env" ]; then
    export $(cat config/.env | grep -v '^#' | xargs)
fi

# 默认配置
export LLM_PROVIDER=${LLM_PROVIDER:-openai}
export XIAOHONGSHU_MCP_URL=${XIAOHONGSHU_MCP_URL:-http://localhost:18060/mcp}

# 解析参数
COMMAND=${1:-gui}

case "$COMMAND" in
    gui)
        exec python3 src/cli.py --gui "$@"
        ;;
    search|-s)
        shift
        exec python3 src/cli.py --search "$@"
        ;;
    stats)
        exec python3 src/cli.py --stats
        ;;
    chat|-c)
        exec python3 src/cli.py --chat
        ;;
    config)
        exec python3 src/cli.py --config
        ;;
    setup)
        exec python3 src/setup.py
        ;;
    -h|--help|help|*)
        echo "小红书 AI Agent CLI"
        echo ""
        echo "用法: ./start.sh [命令]"
        echo ""
        echo "命令:"
        echo "  gui        启动交互式界面"
        echo "  search     搜索帖子"
        echo "  stats      查看统计"
        echo "  chat       AI 对话"
        echo "  config     显示配置"
        echo "  setup      快速配置向导"
        ;;
esac
