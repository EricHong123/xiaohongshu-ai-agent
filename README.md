# 🤖 小红书 AI Agent

一个强大的小红书运营 AI Agent 框架，支持搜索、发布、AI 对话、记忆等功能。

## ✨ 功能特性

- 🔍 **搜索** - 搜索小红书热门帖子
- 📝 **发布** - AI 生成内容并自动发布
- 🤖 **AI 对话** - 支持多轮对话
- 🧠 **记忆** - 对话历史自动保存
- 📚 **知识库** - 内置运营技巧知识库
- 🔌 **多 LLM** - 支持 OpenAI/Claude/智谱/Kimi

## 📁 项目结构

```
xiaohongshu_agent/           # 主包
├── __init__.py              # 包入口
├── __main__.py              # 命令行入口
├── agent/                   # Agent 核心
│   ├── loop.py             # 主循环
│   ├── context.py          # 上下文
│   └── memory.py           # 对话记忆
├── channels/                # 消息渠道
│   └── xiaohongshu.py     # 小红书 MCP
├── cli/                    # 命令行
│   └── commands.py         # typer 命令
├── config/                 # 配置
│   └── loader.py           # 配置加载
├── providers/              # LLM 提供商
│   ├── base.py
│   ├── openai.py
│   ├── anthropic.py
│   ├── zhipu.py
│   └── kimi.py
├── storage/                # 存储
│   └── database.py         # SQLite
└── utils/                  # 工具

pyproject.toml               # 项目配置
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- macOS / Linux
- 网络访问权限

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/EricHong123/xiaohongshu-ai-agent.git
cd xiaohongshu-ai-agent

# 安装项目
pip install -e .
```

### 3. 配置

创建配置文件 `~/.xiaohongshu_agent/config.json`:

```json
{
  "llm_provider": "openai",
  "openai_api_key": "your-api-key",
  "mcp_url": "http://localhost:18060/mcp"
}
```

或使用环境变量:

```bash
export OPENAI_API_KEY=your-api-key
export LLM_PROVIDER=openai
```

### 4. 启动 MCP 服务

```bash
./xiaohongshu-mcp-darwin-amd64
```

### 5. 运行 Agent

```bash
# 命令行模式
xhs search "AI Agent"
xhs --stats
xhs --chat

# 或使用 Python
python -m xiaohongshu_agent --chat
```

## 📖 使用指南

### 命令行

```bash
xhs --search "关键词"     # 搜索
xhs --stats              # 查看统计
xhs --chat              # AI 对话
xhs --config            # 显示配置
```

### Python API

```python
from xiaohongshu_agent import XiaohongshuAgent

# 创建 Agent
agent = XiaohongshuAgent(
    provider="openai",
    model="gpt-4",
    api_key="your-key",
    mcp_url="http://localhost:18060/mcp"
)

# AI 对话
response = agent.chat("你好")
print(response)

# 搜索帖子
posts = agent.search("AI Agent")
for p in posts[:5]:
    print(p["title"], p["likes"])

# 发布帖子
content = agent.generate_content("AI 工具")
result = agent.publish(
    title=content["title"],
    content=content["content"],
    images=["/path/to/image.jpg"],
    tags=content["tags"]
)
```

## 🔌 LLM 提供商

| 提供商 | 环境变量 | 默认模型 |
|--------|----------|----------|
| OpenAI | `OPENAI_API_KEY` | gpt-4 |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4 |
| 智谱 GLM | `ZHIPU_API_KEY` | glm-4 |
| Kimi | `KIMI_API_KEY` | kimi-flash-1.5 |

### Base URL 配置 (代理)

```bash
export OPENAI_BASE_URL=https://api.proxy.com/v1
export ANTHROPIC_BASE_URL=https://api.proxy.com
```

## 🧠 Memory 功能

Agent 自动保存对话历史，支持：

- 多轮对话上下文
- 持久化存储 (SQLite)
- 最多保存 50 条对话

```python
# 查看记忆状态
status = agent.get_memory_status()
print(f"对话历史: {status['count']}/{status['limit']} 条")

# 清空记忆
agent.clear_memory()
```

## 📝 更新日志

### v1.1.0 (2026-03-10)
- 重构为模块化架构 (nanobot 风格)
- 新增对话 Memory 功能
- CLI 使用 typer + rich
- 支持多个 LLM 提供商

### v1.0.0 (2026-03-09)
- 初始版本

## 📄 许可证

MIT License

## 👤 作者

Eric Hong
