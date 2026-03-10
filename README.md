# 🤖 小红书 AI Agent

一个强大的小红书运营 AI Agent 框架，支持搜索、发布、AI 对话、记忆等功能。

## ✨ 功能特性

- 🔍 **搜索** - 搜索小红书热门帖子
- 📝 **发布** - AI 生成内容并自动发布
- 🤖 **AI 对话** - 支持多轮对话
- 🧠 **记忆** - 对话历史自动保存
- 📚 **知识库** - 内置运营技巧知识库
- 🔌 **多 LLM** - 支持 OpenAI/Claude/智谱/Kimi/Minimax/Gemini
- 🛠️ **工具系统** - 文件读写、命令执行、网页搜索
- 📝 **日志系统** - 完整的运行日志

## 📁 项目结构

```
xiaohongshu_agent/           # 主包
├── __init__.py              # 包入口
├── __main__.py              # 命令行入口
├── agent/                   # Agent 核心
│   ├── loop.py             # 主循环
│   ├── context.py          # 上下文
│   ├── memory.py           # 对话记忆
│   └── tools/              # 工具系统
│       ├── base.py         # 工具基类
│       ├── registry.py     # 工具注册表
│       ├── filesystem.py   # 文件工具
│       ├── shell.py       # Shell 工具
│       └── web.py         # 网页工具
├── channels/               # 消息渠道
│   └── xiaohongshu.py    # 小红书 MCP
├── cli/                    # 命令行
│   └── commands.py         # typer 命令
├── config/                 # 配置
│   ├── loader.py           # 配置加载
│   └── validator.py       # 配置验证
├── providers/              # LLM 提供商
│   ├── base.py
│   ├── openai.py
│   ├── anthropic.py
│   ├── zhipu.py
│   ├── kimi.py
│   ├── minimax.py
│   └── gemini.py
├── storage/                # 存储
│   └── database.py         # SQLite
└── utils/                  # 工具
    └── logger.py           # 日志系统

pyproject.toml              # 项目配置
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

# 安装依赖
pip install -r requirements.txt

# 或安装项目
pip install -e .
```

### 3. 配置

创建配置文件 `~/.xiaohongshu_agent/config.json`:

```json
{
  "llm_provider": "minimax",
  "minimax_api_key": "your-api-key",
  "minimax_model": "minimax-m2.5"
}
```

或使用环境变量:

```bash
export MINIMAX_API_KEY=your-api-key
export LLM_PROVIDER=minimax
```

### 4. 启动 MCP 服务

```bash
./xiaohongshu-mcp-darwin-amd64
```

### 5. 运行 Agent

```bash
# 命令行模式
python3 -m xiaohongshu_agent --config    # 查看配置
python3 -m xiaohongshu_agent AI --search # 搜索
python3 -m xiaohongshu_agent --chat      # 对话

# 交互式菜单
python3 -m xiaohongshu_agent
```

## 📖 使用指南

### 命令行

```bash
xhs AI --search     # 搜索
xhs --stats        # 查看统计
xhs --chat         # AI 对话
xhs --config       # 显示配置
```

### Python API

```python
from xiaohongshu_agent import XiaohongshuAgent

# 创建 Agent
agent = XiaohongshuAgent(
    provider="minimax",
    model="minimax-m2.5",
    api_key="your-key"
)

# AI 对话
response = agent.chat("你好")

# 搜索帖子
posts = agent.search("AI Agent")

# 发布帖子
content = agent.generate_content("AI 工具")
result = agent.publish(
    title=content["title"],
    content=content["content"],
    images=["/path/to/image.jpg"],
    tags=content["tags"]
)
```

### 工具系统

```python
from xiaohongshu_agent.agent.tools import registry

# 获取工具
file_tool = registry.get("file_read")
result = file_tool.execute(path="/path/to/file.txt")

# 搜索网页
web_tool = registry.get("web_search")
result = web_tool.execute(query="AI 工具")
```

## 🔌 LLM 提供商

| 提供商 | 环境变量 | 默认模型 |
|--------|----------|----------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| 智谱 GLM | `ZHIPU_API_KEY` | glm-4 |
| Kimi | `KIMI_API_KEY` | kimi-flash-1.5 |
| Minimax | `MINIMAX_API_KEY` | minimax-m2.5 |
| Gemini | `GEMINI_API_KEY` | gemini-2.0-flash |

### 模型列表

- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo
- **Anthropic**: claude-sonnet-4, claude-4-opus, claude-3-opus, claude-3-sonnet, claude-3-haiku
- **智谱 GLM**: glm-4, glm-4-flash, glm-4-plus, glm-3-turbo
- **Kimi**: kimi-flash-1.5, kimi-pro-1.5, kimi-flash, kimi-pro
- **Minimax**: minimax-m2.5, abab6.5s-chat, abab6.5-chat, abab5.5s-chat
- **Gemini**: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash

### Base URL 配置 (代理)

```bash
export OPENAI_BASE_URL=https://api.proxy.com/v1
export ANTHROPIC_BASE_URL=https://api.proxy.com
```

## 🛠️ 工具系统

| 工具 | 说明 | 示例 |
|------|------|------|
| `file_read` | 读取文件 | `file_read(path="/tmp/test.txt")` |
| `file_write` | 写入文件 | `file_write(path="/tmp/test.txt", content="hello")` |
| `list_directory` | 列出目录 | `list_directory(path="~/Desktop")` |
| `shell_execute` | 执行命令 | `shell_execute(command="ls -la")` |
| `web_search` | 网页搜索 | `web_search(query="AI 工具")` |
| `web_fetch` | 网页抓取 | `web_fetch(url="https://example.com")` |

### 安全特性

- 文件操作：限制可访问目录
- Shell 执行：危险命令黑名单
- URL 验证：只允许 http/https

## 🧠 Memory 功能

Agent 自动保存对话历史：

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

## 📝 日志系统

日志自动保存到 `logs/` 目录：

```python
from xiaohongshu_agent.utils.logger import logger

logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
```

## ⚙️ 配置验证

启动时自动验证配置：

```bash
python3 -m xiaohongshu_agent --config
```

验证项目：
- API Key 是否配置
- MCP URL 是否正确
- 权限设置

## 📝 更新日志

### v1.2.0 (2026-03-10)
- 添加 loguru 日志系统
- MCP 通道添加重试机制、超时处理
- 添加工具系统：文件读写、Shell执行、网页搜索
- 添加配置验证器
- 支持键盘上下选择菜单

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
