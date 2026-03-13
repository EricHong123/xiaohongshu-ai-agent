# 🤖 小红书 AI Agent

一个强大的小红书运营 AI Agent 框架，支持搜索、发布、AI 对话、记忆等功能。

## ✨ 新版本特性 (V2)

### 🚀 Gateway AI Agent 网关

V2 版本新增 **Gateway AI Agent 网关**，提供统一的 Agent 管理、命令系统和 HTTP/WebSocket API：

- **多 Agent 路由** - 支持关键词路由、轮询、首选可用 Agent
- **会话管理** - 自动保存对话历史，支持多会话隔离
- **工具网关** - 统一工具注册和调用
- **命令系统** - 快捷命令 `/xhs`, `/doctor`, `/agent` 等
- **HTTP API** - RESTful 接口支持
- **WebSocket** - 实时消息推送

### 📡 Gateway 命令

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

### 🎯 Gateway 架构

```
┌─────────────────────────────────────────┐
│              Gateway                     │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐       │
│  │  Session   │  │   Agent     │       │
│  │  Manager   │  │  Registry   │       │
│  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐       │
│  │    Tool    │  │  Command    │       │
│  │  Gateway   │  │  Registry   │       │
│  └─────────────┘  └─────────────┘       │
│  ┌─────────────────────────────────┐   │
│  │    xhs_automation CLI           │   │
│  │  (登录/搜索/发布/互动)           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## ✨ 功能特性

- 🔍 **搜索** - 搜索小红书热门帖子
- 📝 **发布** - AI 生成内容并自动发布
- 🎬 **视频生成** - AI 分析图片生成种草视频
- 🤖 **AI 对话** - 支持多轮对话
- 🧠 **记忆** - 对话历史自动保存
- 📚 **知识库** - 内置运营技巧知识库
- 🔌 **多 LLM** - 支持 OpenAI/Claude/智谱/Kimi/Minimax/Gemini
- 🛠️ **工具系统** - 文件读写、命令执行、网页搜索
- 📝 **日志系统** - 完整的运行日志
- 📝 **工作流** - 内嵌电商产品导演skills写scriptgenerator
- 🤖 **Claude Code Skills** - 集成小红书自动化技能（认证、发布、搜索、互动）

## Claude Code Skills (小红书自动化)

项目集成了 Claude Code Skills，可通过自然语言控制小红书：

| 技能 | 说明 | 核心能力 |
|------|------|----------|
| **xhs-auth** | 认证管理 | 登录检查、扫码登录、多账号切换 |
| **xhs-publish** | 内容发布 | 图文 / 视频 / 长文发布、分步预览 |
| **xhs-explore** | 内容发现 | 关键词搜索、笔记详情、用户主页、首页推荐 |
| **xhs-interact** | 社交互动 | 评论、回复、点赞、收藏 |
| **xhs-content-ops** | 复合运营 | 竞品分析、热点追踪、批量互动 |

### 安装 Skills

```bash
# Skills 已集成在 .claude/skills 目录
# 安装 Python 依赖
cd xhs_automation
uv sync
```

### 使用方式

安装 Skills 后，直接用自然语言与 Claude Code 对话：

> "登录小红书" / "搜索关于AI的笔记" / "帮我发一条图文笔记"

### CLI 命令

```bash
cd xhs_automation

# 启动 Chrome
python scripts/chrome_launcher.py

# 检查登录状态
python scripts/cli.py check-login

# 搜索笔记
python scripts/cli.py search-feeds --keyword "关键词"

# 发布图文
python scripts/cli.py publish --title-file title.txt --content-file content.txt --images "/path/pic1.jpg"
```

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
├── gateway/                 # V2 新增：Gateway 网关
│   ├── __init__.py        # 网关入口
│   ├── types.py           # 类型定义
│   ├── commands.py         # 命令系统
│   ├── core/               # 核心模块
│   │   ├── session.py     # 会话管理
│   │   ├── registry.py    # Agent 注册
│   │   ├── tool.py        # 工具网关
│   │   └── orchestrator.py # 多Agent编排
│   ├── tools/              # 工具实现
│   │   ├── xhs_automation.py  # xhs_automation 封装
│   │   └── xhs_tools.py   # 工具注册
│   ├── server/             # HTTP/WebSocket 服务器
│   │   ├── http.py        # HTTP API
│   │   ├── websocket.py    # WebSocket
│   │   └── combined.py    # 组合服务器
│   └── adapter/            # 适配器
│       └── xiaohongshu.py # 小红书Agent适配
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
├── workflow/                # 视频生成工作流
└── utils/                  # 工具
    └── logger.py           # 日志系统

xhs_automation/            # 小红书自动化 (CDP 引擎)
├── scripts/               # Python CLI 工具
│   ├── cli.py             # 统一 CLI 入口
│   ├── chrome_launcher.py # Chrome 进程管理
│   ├── xhs/               # 核心自动化包
│   └── ...
└── pyproject.toml         # 项目配置

.claude/skills/             # Claude Code Skills
├── xhs-auth/              # 认证技能
├── xhs-publish/           # 发布技能
├── xhs-explore/           # 搜索发现技能
├── xhs-interact/          # 互动技能
├── xhs-content-ops/       # 复合运营技能
└── SKILL.md               # 技能入口

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

# Gateway 服务器模式
python3 run_server.py   # HTTP + WebSocket
python3 run_commands.py # 测试命令系统
```

## 📖 使用指南

### 命令行

```bash
xhs AI --search     # 搜索
xhs --stats        # 查看统计
xhs --chat         # AI 对话
xhs --config       # 显示配置
```

### Gateway API

```bash
# 启动 Gateway 服务器
python3 run_server.py

# HTTP API
curl -X POST http://localhost:3000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "hello"}'

# WebSocket
ws://localhost:3001/socket.io
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


## 🎬 视频生成工作流

从产品图片自动生成小红书种草视频

### 工作流程

```
┌────────────┐    ┌────────────┐    ┌─────────────┐
│ 1. 分析图片 │ -> │ 2. 生成脚本 │ -> │ 3. 生成视频   │
│  (GLM-4.6V)│    (Minimax-m2.5)│   │ Seedance2.0)│
└────────────┘    └────────────┘    └─────────────┘
                                              │
                                              ▼
┌────────────┐    ┌────────────┐    ┌─────────────┐
│ 6. 发布     │ <- │ 5. 整合剪辑 │ <- │ 4. 生成音频 │
│  小红书    │     │  (FFmpeg)  │    │  (海螺TTS)  │
└────────────┘    └────────────┘    └─────────────┘
```

### 成本估算 (7-15秒视频)

| 环节 | 服务 | 成本 |
|------|------|------|
| 图片分析 | 智谱 GLM-4.6V | ¥0.01 |
| 脚本生成 | Minimax-m2.5 | ¥0.005 |
| 视频生成 | Seedance2.0 | ¥1.5-3 |
| 音频生成 | 海螺 TTS | ¥0.3-0.5 |
| **合计** | | **¥2-4/条** |

### 环境配置

```bash
# 智谱 (图片分析 + 脚本)
export ZHIPU_API_KEY="your-zhipu-key"

# 可灵 (视频生成)
export KLING_API_KEY="your-kling-key"

# 海螺/MiniMax (音频)
export MINIMAX_API_KEY="your-minimax-key"
```

### 命令行使用

```bash
# 生成视频
python3 -m xiaohongshu_agent --video create \
  --images "product1.jpg,product2.jpg" \
  --product "护肤品" \
  --duration 10

# 测试连接
python3 -m xiaohongshu_agent --video test

# 查看可用音色
python3 -m xiaohongshu_agent --video voices
```

### Python API

```python
from xiaohongshu_agent.workflow import VideoWorkflow

# 初始化
workflow = VideoWorkflow(
    output_dir="output/videos",
    config={
        "zhipu_api_key": "your-key",
        "kling_api_key": "your-key",
        "minimax_api_key": "your-key"
    }
)

# 运行工作流
result = workflow.run(
    image_paths=["img1.jpg", "img2.jpg"],
    product_name="护肤品",
    duration=10,
    auto_publish=False
)

print(f"视频: {result['output']['video']}")
```

### 可用音色

| 类型 | 音色ID |
|------|--------|
| 男声 | male-qn-qingse (青涩青年) |
| 男声 | male-qn-jingying (精英青年) |
| 男声 | male-qn-badao (霸道总裁) |
| 女声 | female-shaonv (活泼少女) |
| 女声 | female-yujie (温柔御姐) |

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
- **智谱 GLM**: glm-4, glm-4-flash, glm-4-plus, glm-4.6v, glm-3-turbo
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

### V2 (2026-03-13)
- 新增 Gateway AI Agent 网关
- 多 Agent 路由系统（关键词/轮询/首选可用）
- 会话管理器（历史保存、多会话隔离）
- 命令系统 `/xhs`, `/doctor`, `/agent` 等
- HTTP API + WebSocket 服务器
- 集成 xhs_automation 到 Gateway
- 修复代理问题（NO_PROXY）

### v1.3.1 (2026-03-11)
- 视频生成集成电商导演Skill专业分镜头模板
- 支持7/10/15秒多种视频时长
- 自动适配美妆/数码/家居等风格配置
- Web UI优化，首页添加视频生成入口
- 支持智谱CogVideoX-3视频生成
- API速率限制自动跳过逻辑
- 图片分析模型升级为 glm-4.6v

### v1.3.0 (2026-03-11)
- 新增视频生成工作流模块
- 支持多模态LLM分析产品图片
- 集成可灵AI视频生成
- 集成海螺TTS音频生成
- FFmpeg视频剪辑整合
- CLI新增 --video 命令
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
