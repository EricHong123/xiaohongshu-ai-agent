# 🤖 小红书 AI Agent

一个强大的小红书运营 AI Agent 框架，支持搜索、发布、AI 对话、记忆等功能。
CLI
<img width="1964" height="1696" alt="image" src="https://github.com/user-attachments/assets/3f8eee98-2ff2-4cfa-bffc-967401c47119" />

<img width="1160" height="696" alt="image" src="https://github.com/user-attachments/assets/ba154fae-1092-4303-a175-ea2569315e89" />
Web UI 地址：http://127.0.0.1:5003/
<img width="2880" height="1626" alt="image" src="https://github.com/user-attachments/assets/a191058e-a9b4-4263-94b9-27da7113271f" />

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
├── workflow/                # 视频生成工作流
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
