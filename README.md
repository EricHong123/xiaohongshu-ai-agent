# 🤖 小红书 AI Agent 系统

一个强大的小红书运营 AI Agent，支持搜索、发布、自动回复等功能。

## 📁 项目结构

```
xiaohongshu-agent/
├── src/                    # 源代码
│   ├── agent.py           # 基础 Agent
│   ├── enhanced_agent.py   # 增强版 Agent
│   ├── cli.py             # 命令行界面
│   ├── config_manager.py  # 配置管理
│   ├── computer_control.py # 电脑控制
│   ├── database.py        # 数据库
│   ├── llm_adapter.py    # LLM 适配器
│   ├── rag.py            # RAG 知识库
│   ├── security.py        # 安全模块
│   └── terminal.py       # 终端界面
├── config/                 # 配置目录
├── data/                  # 数据目录
├── logs/                  # 日志目录
├── xiaohongshu           # 启动脚本
└── setup.py              # 配置向导
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- macOS / Linux / Windows
- 网络访问权限

### 2. 安装依赖

```bash
cd xiaohongshu-agent
pip install -r requirements.txt
```

### 3. 配置

#### 方式一：交互式配置

```bash
./xiaohongshu setup
```

按照提示选择 LLM 提供商并输入 API Key。

#### 方式二：环境变量配置

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
# OpenAI (默认)
export OPENAI_API_KEY=your_openai_key
export LLM_PROVIDER=openai

# 或者使用其他提供商：

# Anthropic (Claude)
export ANTHROPIC_API_KEY=your_claude_key
export LLM_PROVIDER=anthropic

# 智谱 GLM
export ZHIPU_API_KEY=your_zhipu_key
export LLM_PROVIDER=zhipu

# Kimi
export KIMI_API_KEY=your_kimi_key
export LLM_PROVIDER=kimi

# Google Gemini
export GEMINI_API_KEY=your_gemini_key
export LLM_PROVIDER=gemini

# Minimax
export MINIMAX_API_KEY=your_minimax_key
export LLM_PROVIDER=minimax
```

### 4. 启动

```bash
# 交互式界面
./xiaohongshu gui

# 或使用 Python
python3 src/cli.py --gui
```

## 📖 使用指南

### 命令行模式

```bash
# 搜索帖子
./xiaohongshu search -k "AI Agent"

# 查看统计
./xiaohongshu stats

# AI 对话
./xiaohongshu chat

# 查看配置
./xiaohongshu config
```

### 交互式界面功能

```
═══════════════════════════════════════
          主菜单
═══════════════════════════════════════
  [1]  🔍 搜索热门帖子
  [2]  📝 创建并发布帖子
  [3]  📊 查看数据统计
  [4]  📁 文件管理
  [5]  💻 电脑控制
  [6]  🤖 AI 对话
  [S]  ⚙️ 系统设置
  [Q]  🚪 退出
```

### 系统设置 (S)

- **1**: 选择 LLM 提供商 (OpenAI/Claude/智谱/Kimi/Gemini/Minimax)
- **2**: 配置 API Key
- **3**: 配置 MCP 地址
- **4**: 配置权限
- **5**: 查看当前配置

## 🔌 LLM 提供商支持

| 提供商 | 环境变量 | 默认模型 |
|--------|----------|----------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4 |
| 智谱 GLM | `ZHIPU_API_KEY` | glm-4 |
| Kimi | `KIMI_API_KEY` | kimi-flash-1.5 |
| Gemini | `GEMINI_API_KEY` | gemini-2.0-flash |
| Minimax | `MINIMAX_API_KEY` | abab6.5s-chat |

## 🔐 权限控制

系统包含安全模块，支持以下权限：

| 权限 | 说明 |
|------|------|
| `file_read` | 读取文件 |
| `file_write` | 写入文件 |
| `command_exec` | 执行系统命令 |
| `browser_control` | 控制浏览器 |
| `screenshot` | 截取屏幕 |
| `clipboard` | 读写剪贴板 |

### 启用权限

```bash
# 命令行
python3 src/cli.py --permissions file_read file_write command_exec

# 或在界面中配置
```

## 📊 功能列表

### 小红书功能
- 🔍 搜索热门帖子
- 📝 发布图文内容
- 💬 自动回复评论
- 📊 数据统计
- 🧠 AI 内容生成

### 电脑控制功能
- 📁 文件管理 (读/写/列目录)
- 🌐 打开网页
- 📸 屏幕截图
- 📋 剪贴板操作
- 🔔 系统通知
- 🔊 语音播报
- 💻 执行命令

## ⚙️ 配置说明

配置文件位置: `~/.xiaohongshu_agent/config.json`

```json
{
  "llm_provider": "openai",
  "mcp_url": "http://localhost:18060/mcp",
  "permissions": ["file_read", "browser_control", "clipboard"],
  "openai_model": "gpt-4o"
}
```

## 🔧 故障排除

### MCP 连接失败

确保小红书 MCP 服务正在运行：

```bash
# 检查服务
curl http://localhost:18060/health

# 启动服务
cd /path/to/xiaohongshu-mcp-darwin-arm64
./xiaohongshu-mcp-darwin-arm64 &
```

### API Key 无效

```bash
# 检查配置
./xiaohongshu config

# 重新配置
./xiaohongshu setup
```

### 权限问题

在设置中启用相应权限，或使用 `--permissions` 参数。

## 📝 更新日志

### v1.0.0 (2026-03-09)
- 初始版本
- 支持多种 LLM 提供商
- 集成小红书 MCP
- 安全权限控制
- 电脑控制功能

## 📄 许可证

MIT License
