# 🤖 小红书 AI Agent

一个强大的小红书运营 AI Agent 框架，支持搜索、发布、AI 对话、记忆等功能。

## ✨ V2 新版本特性

### 🚀 控制面板

V2 版本提供**可视化控制面板**，一站式管理所有服务：

- 启动/停止服务（Web UI、Gateway、MCP）
- 小红书操作（登录、搜索、发布、账号管理）
- 实时日志查看
- 系统配置监控

### 🎯 Gateway AI Agent 网关

**Gateway AI Agent 网关**，提供统一的 Agent 管理、命令系统和 HTTP/WebSocket API：

- **多 Agent 路由** - 支持关键词路由、轮询、首选可用 Agent
- **会话管理** - 自动保存对话历史，支持多会话隔离
- **工具网关** - 统一工具注册和调用
- **命令系统** - 快捷命令 `/xhs`, `/doctor`, `/agent` 等
- **HTTP API** - RESTful 接口支持
- **WebSocket** - 实时消息推送

---

## ⚡ 快速启动

### 1. 控制面板（推荐）

```bash
python3 run_dashboard.py
```

然后访问：**http://127.0.0.1:8080**

### 2. 命令行启动

```bash
# 启动 Gateway
python3 run_server.py

# 启动 Web UI
python3 -m xiaohongshu_agent.web

# 启动 CLI
python3 -m xiaohongshu_agent
```

### 3. 统一入口

```bash
python3 -m xiaohongshu_agent gateway   # Gateway
python3 -m xiaohongshu_agent web      # Web
python3 -m xiaohongshu_agent agent    # CLI
python3 -m xiaohongshu_agent dashboard # 控制面板
```

---

## 📁 项目结构

```
xiaohongshu_agent/           # 主包 (V2.0.0)
├── __init__.py            # 统一导出
│
├── services/              # 📦 服务层（V2 新增）
│   ├── chat.py           # 对话服务
│   ├── search.py        # 搜索服务
│   ├── publish.py       # 发布服务
│   ├── stats.py         # 统计服务
│   ├── content.py       # 内容生成
│   ├── prompts.py       # 提示词模板
│   ├── knowledge.py    # 知识库
│   └── constants.py    # 常量定义
│
├── gateway/               # V2 Gateway 网关
│   ├── __init__.py      # 网关入口
│   ├── types.py         # 类型定义
│   ├── commands.py     # 命令系统
│   ├── core/           # 核心模块
│   │   ├── session.py     # 会话管理
│   │   ├── registry.py    # Agent 注册
│   │   ├── tool.py       # 工具网关
│   │   └── orchestrator.py # 多Agent编排
│   ├── tools/           # 工具实现
│   │   ├── xhs_automation.py  # xhs_automation 封装
│   │   └── xhs_tools.py  # 工具注册
│   ├── server/          # HTTP/WebSocket
│   │   ├── http.py      # HTTP API
│   │   ├── websocket.py # WebSocket
│   │   └── combined.py  # 组合服务器
│   └── adapter/         # 适配器
│       └── xiaohongshu.py
│
├── agent/                # Agent 核心
│   ├── loop.py         # 主循环
│   ├── context.py     # 上下文
│   ├── memory.py      # 对话记忆
│   └── tools/         # 工具系统
│
├── providers/           # LLM 提供商 (12+)
│   ├── openai.py
│   ├── anthropic.py
│   ├── zhipu.py
│   ├── kimi.py
│   ├── minimax.py
│   ├── gemini.py
│   └── ...
│
├── web/                 # Web 服务
├── cli/                 # CLI 入口
├── config/              # 配置管理
├── storage/             # 存储 (SQLite)
├── workflow/            # 视频生成
└── utils/               # 工具函数

xhs_automation/         # 小红书自动化 (CDP)
├── cli.py              # 统一 CLI
├── chrome_launcher.py  # Chrome 管理
└── xhs/               # 核心自动化

run_dashboard.py         # 控制面板
run_server.py            # Gateway 服务器
```

---

## 🔧 功能特性

| 功能 | 说明 |
|------|------|
| 🔍 搜索 | 搜索小红书热门帖子 |
| 📝 发布 | AI 生成内容并自动发布 |
| 🎬 视频 | AI 分析图片生成种草视频 |
| 🤖 对话 | 支持多轮对话 |
| 🧠 记忆 | 对话历史自动保存 |
| 📚 知识库 | 内置运营技巧 |
| 🔌 多 LLM | OpenAI/Claude/智谱/Kimi/Minimax/Gemini |
| 🛠️ 工具 | 文件读写、Shell执行、网页搜索 |

---

## 📡 Gateway 命令

通过 `/` 前缀使用快捷命令：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/status` | 系统状态 |
| `/xhs login` | 获取登录二维码 |
| `/xhs check-login` | 检查登录状态 |
| `/xhs search <关键词>` | 搜索笔记 |
| `/xhs publish <内容>` | 发布笔记 |
| `/doctor` | 系统诊断 |
| `/doctor fix` | 自动修复 |
| `/gateway config` | Gateway 配置 |

---

## 💻 控制面板功能

| Tab | 功能 |
|-----|------|
| 🚀 服务 | 启动/停止 Web UI、Gateway、MCP |
| 📕 小红书 | 登录、搜索、发布、账号管理 |
| 🛠️ 工具 | 数据库统计、文件信息 |
| 📋 日志 | 实时运行日志 |
| ⚙️ 配置 | 环境变量、API 密钥 |
| 💻 系统 | 系统信息、项目结构 |

---

## 🔌 LLM 提供商

| 提供商 | 环境变量 | 默认模型 |
|--------|----------|----------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4 |
| 智谱 GLM | `ZHIPU_API_KEY` | glm-4 |
| Kimi | `KIMI_API_KEY` | kimi-flash-1.5 |
| Minimax | `MINIMAX_API_KEY` | minimax-m2.5 |
| Gemini | `GEMINI_API_KEY` | gemini-2.0-flash |

---

## 🛠️ 环境配置

```bash
# 克隆项目
git clone https://github.com/EricHong123/xiaohongshu-ai-agent.git
cd xiaohongshu-ai-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export MINIMAX_API_KEY="your-key"
export LLM_PROVIDER="minimax"

# 启动 MCP（可选）
./xiaohongshu-mcp-darwin-amd64
```

---

## 📖 使用示例

### Python API

```python
from xiaohongshu_agent import XiaohongshuAgent, chat, search_notes, publish_note

# 创建 Agent
agent = XiaohongshuAgent(provider="minimax", model="minimax-m2.5")

# AI 对话
response = agent.chat("你好")

# 搜索
posts = search_notes(agent, "护肤")

# 发布
publish_note(agent, title="标题", content="内容", images=["a.jpg"])
```

### Gateway API

```bash
# HTTP API
curl -X POST http://localhost:3000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "hello"}'

# WebSocket
ws://localhost:3001/socket.io
```

---

## 📝 更新日志

### V2.0.0 (2026-03-13)
- 新增控制面板 (run_dashboard.py)
- 新增 services/ 服务层模块
- 新增 Gateway AI Agent 网关
- 多 Agent 路由系统
- 命令系统 (/xhs, /doctor)
- HTTP API + WebSocket
- 统一 CLI 入口

### V1.x
- 视频生成工作流
- 多 LLM 支持
- 工具系统
- Memory 功能

---

## 📄 许可证

MIT License

## 👤 作者

Eric Hong
