#!/bin/bash
# 快速配置脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🔧 小红书 AI Agent 配置向导                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"

# 选择 LLM 提供商
echo "请选择 LLM 提供商:"
echo ""
echo "  1. OpenAI"
echo "  2. Anthropic (Claude)"
echo "  3. 智谱 GLM"
echo "  4. Kimi (月之暗面)"
echo "  5. Google Gemini"
echo "  6. Minimax"
echo ""

read -p "选择 (1-6): " choice

case $choice in
    1) PROVIDER="openai";;
    2) PROVIDER="anthropic";;
    3) PROVIDER="zhipu";;
    4) PROVIDER="kimi";;
    5) PROVIDER="gemini";;
    6) PROVIDER="minimax";;
    *) echo "无效选择"; exit 1;;
esac

# 获取 API Key
echo ""
echo "请输入 API Key:"
read -s -p "API Key: " API_KEY

if [ -n "$API_KEY" ]; then
    # 保存到配置文件
    mkdir -p ~/.xiaohongshu_agent

    # 更新或创建配置
    if [ -f ~/.xiaohongshu_agent/config.json ]; then
        # 更新现有配置
        python3 -c "
import json
import os

config_file = os.path.expanduser('~/.xiaohongshu_agent/config.json')

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {}

config['llm_provider'] = '$PROVIDER'

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print('配置已保存')
"
    else
        # 创建新配置
        echo "{\"llm_provider\": \"$PROVIDER\"}" > ~/.xiaohongshu_agent/config.json
    fi

    # 同时设置环境变量
    export ${PROVIDER^^}_API_KEY="$API_KEY"

    echo ""
    echo "✓ 配置完成!"
    echo "  提供商: $PROVIDER"
else
    echo ""
    echo "跳过 API Key 配置"
fi

echo ""
echo "要使用此配置，请运行:"
echo "  cd $SCRIPT_DIR"
echo "  python3 cli.py --gui"
