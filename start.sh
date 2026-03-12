#!/bin/bash
# 小红书 AI Agent 启动脚本

# 项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# #region agent log
agent_log() {
  # NDJSON debug log (no secrets)
  local event="$1"
  shift || true
  local log_dir="${SCRIPT_DIR}/.cursor"
  mkdir -p "$log_dir" 2>/dev/null || true
  local log_path="${log_dir}/debug-d2d076.log"
  echo "[debug] SCRIPT_DIR=$SCRIPT_DIR event=$event log_path=$log_path" 1>&2
  # Always write at least one NDJSON line using bash only.
  # (This guarantees evidence even if python3 is missing/broken.)
  local ts
  ts="$(date +%s 2>/dev/null || echo 0)"
  printf '%s\n' "{\"sessionId\":\"d2d076\",\"runId\":\"post-fix\",\"hypothesisId\":\"H1\",\"location\":\"start.sh:agent_log\",\"message\":\"start.sh invoked\",\"data\":{\"event\":\"${event}\"},\"timestamp\":${ts}}" >> "$log_path" 2>/dev/null || true

  # Best-effort richer payload (keeps existing behavior if python3 works).
  DEBUG_EVENT="$event" DEBUG_ARGS="$*" DEBUG_LOG_PATH="$log_path" python3 -c "import json,os,time;payload={'sessionId':'d2d076','runId':'post-fix','hypothesisId':'H1','location':'start.sh:agent_log','message':'start.sh invoked','data':{'event':os.environ.get('DEBUG_EVENT'),'argsRaw':os.environ.get('DEBUG_ARGS',''),'logPath':os.environ.get('DEBUG_LOG_PATH')},'timestamp':int(time.time()*1000)};open(os.environ['DEBUG_LOG_PATH'],'a',encoding='utf-8').write(json.dumps(payload,ensure_ascii=False)+'\\n')" 2>/dev/null || true
}
# #endregion

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
        shift
        agent_log "gui" "$@"
        exec python3 -m xiaohongshu_agent --gui "$@"
        ;;
    search|-s)
        shift
        agent_log "search" "$@"
        exec python3 -m xiaohongshu_agent --search "$@"
        ;;
    stats)
        shift
        agent_log "stats"
        exec python3 -m xiaohongshu_agent --stats
        ;;
    chat|-c)
        shift
        agent_log "chat"
        exec python3 -m xiaohongshu_agent --chat
        ;;
    config)
        shift
        agent_log "config"
        exec python3 -m xiaohongshu_agent --config
        ;;
    setup)
        shift
        agent_log "setup"
        exec python3 -m xiaohongshu_agent --gui
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
