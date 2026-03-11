"""
Flask Web 应用
"""
import os
from flask import Flask, render_template, request, jsonify, session
from xiaohongshu_agent import XiaohongshuAgent
from xiaohongshu_agent.config import load_config, validate_config
from xiaohongshu_agent.providers import get_available_providers
from xiaohongshu_agent.utils.logger import logger


# 全局 Agent 实例
agent = None


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.urandom(24)

    # 配置
    app.config['JSON_AS_ASCII'] = False

    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def chat():
        """AI 对话"""
        global agent

        data = request.json
        message = data.get('message', '')

        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        try:
            if agent is None:
                init_agent()

            response = agent.chat(message)
            return jsonify({'response': response, 'success': True})
        except Exception as e:
            logger.error(f"对话失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/search', methods=['POST'])
    def search():
        """搜索帖子"""
        global agent

        data = request.json
        keyword = data.get('keyword', '')

        if not keyword:
            return jsonify({'error': '关键词不能为空'}), 400

        try:
            if agent is None:
                init_agent()

            posts = agent.search(keyword)
            return jsonify({'posts': posts, 'success': True})
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/publish', methods=['POST'])
    def publish():
        """发布帖子"""
        global agent

        data = request.json
        title = data.get('title', '')
        content = data.get('content', '')
        images = data.get('images', [])
        tags = data.get('tags', [])

        if not images:
            return jsonify({'error': '需要图片'}), 400

        try:
            if agent is None:
                init_agent()

            result = agent.publish(title, content, images, tags)
            return jsonify(result)
        except Exception as e:
            logger.error(f"发布失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate', methods=['POST'])
    def generate_content():
        """AI 生成内容"""
        global agent

        data = request.json
        keyword = data.get('keyword', '')

        try:
            if agent is None:
                init_agent()

            content = agent.generate_content(keyword)
            return jsonify({'content': content, 'success': True})
        except Exception as e:
            logger.error(f"生成内容失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/stats')
    def stats():
        """获取统计"""
        global agent

        try:
            if agent is None:
                init_agent()

            stats = agent.get_stats()
            return jsonify({'stats': stats, 'success': True})
        except Exception as e:
            logger.error(f"获取统计失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/config', methods=['GET', 'POST'])
    def config():
        """配置管理"""
        global agent

        if request.method == 'POST':
            data = request.json
            cfg = load_config()

            # 更新配置
            if 'provider' in data:
                cfg.set('llm_provider', data['provider'])
            if 'model' in data:
                provider = data.get('provider', cfg.get('llm_provider', 'openai'))
                cfg.set(f"{provider}_model", data['model'])
            if 'api_key' in data:
                provider = data.get('provider', cfg.get('llm_provider', 'openai'))
                cfg.set(f"{provider}_api_key", data['api_key'])
            if 'mcp_url' in data:
                cfg.set('mcp_url', data['mcp_url'])

            cfg.save()

            # 重新初始化 Agent
            init_agent()

            return jsonify({'success': True, 'message': '配置已保存'})

        # GET: 返回当前配置
        cfg = load_config()
        providers = get_available_providers()
        provider = cfg.get('llm_provider', 'openai')

        return jsonify({
            'success': True,
            'config': {
                'provider': provider,
                'model': cfg.get_model(),
                'mcp_url': cfg.get('mcp_url'),
                'api_key': '***' if cfg.get_api_key() else '',
            },
            'providers': {k: {
                'name': v['name'],
                'models': v['models']
            } for k, v in providers.items()}
        })

    @app.route('/api/memory')
    def memory():
        """获取对话历史"""
        global agent

        try:
            if agent is None:
                init_agent()

            history = agent.memory.get_history(50)
            status = agent.get_memory_status()
            return jsonify({
                'success': True,
                'history': history,
                'status': status
            })
        except Exception as e:
            logger.error(f"获取记忆失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/memory/clear', methods=['POST'])
    def clear_memory():
        """清空对话历史"""
        global agent

        try:
            if agent is None:
                init_agent()

            agent.clear_memory()
            return jsonify({'success': True, 'message': '已清空'})
        except Exception as e:
            logger.error(f"清空记忆失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/agent/init', methods=['POST'])
    def init_agent_api():
        """初始化 Agent"""
        global agent

        try:
            init_agent()
            return jsonify({'success': True, 'message': 'Agent 已初始化'})
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health')
    def health():
        """健康检查"""
        global agent
        return jsonify({
            'success': True,
            'agent_initialized': agent is not None
        })

    # ========== 视频生成工作流 ==========

    @app.route('/video')
    def video_page():
        """视频生成页面"""
        return render_template('video.html')

    @app.route('/api/video/test', methods=['GET'])
    def video_test():
        """测试视频工作流组件"""
        from xiaohongshu_agent.workflow import VideoWorkflow

        try:
            workflow = VideoWorkflow()
            status = workflow.test()
            return jsonify({'status': status, 'success': True})
        except Exception as e:
            logger.error(f"测试失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/video/voices', methods=['GET'])
    def video_voices():
        """获取可用音色"""
        from xiaohongshu_agent.workflow import AudioGenerator

        try:
            gen = AudioGenerator()
            voices = gen.get_available_voices()
            return jsonify({'voices': voices, 'success': True})
        except Exception as e:
            logger.error(f"获取音色失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/video/generate', methods=['POST'])
    def video_generate():
        """生成视频"""
        from xiaohongshu_agent.workflow import VideoWorkflow

        data = request.json
        images = data.get('images', [])
        product_name = data.get('product_name', '')
        context = data.get('context', '')
        duration = data.get('duration', 10)
        voice = data.get('voice', 'male-qn-qingse')
        auto_publish = data.get('auto_publish', False)

        if not images:
            return jsonify({'error': '需要提供产品图片'}), 400

        try:
            workflow = VideoWorkflow(
                output_dir="output/web_videos",
                config={
                    "zhipu_api_key": os.getenv("ZHIPU_API_KEY"),
                    "kling_api_key": os.getenv("KLING_API_KEY"),
                    "minimax_api_key": os.getenv("MINIMAX_API_KEY")
                }
            )

            result = workflow.run(
                image_paths=images,
                product_name=product_name,
                context=context,
                duration=duration,
                voice=voice,
                auto_publish=auto_publish
            )

            return jsonify(result)
        except Exception as e:
            logger.error(f"视频生成失败: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/video/config', methods=['GET', 'POST'])
    def video_config():
        """视频工作流配置"""
        if request.method == 'POST':
            data = request.json

            if 'zhipu_api_key' in data:
                os.environ['ZHIPU_API_KEY'] = data['zhipu_api_key']
            if 'kling_api_key' in data:
                os.environ['KLING_API_KEY'] = data['kling_api_key']
            if 'minimax_api_key' in data:
                os.environ['MINIMAX_API_KEY'] = data['minimax_api_key']

            return jsonify({'success': True, 'message': '配置已保存'})

        return jsonify({
            'success': True,
            'config': {
                'zhipu': bool(os.getenv('ZHIPU_API_KEY')),
                'kling': bool(os.getenv('KLING_API_KEY')),
                'minimax': bool(os.getenv('MINIMAX_API_KEY'))
            }
        })


    @app.route('/api/channel/check_login', methods=['POST'])
    def check_login():
        """检查小红书登录状态"""
        global agent

        try:
            if agent is None:
                init_agent()

            result = agent.channel.check_login()
            return jsonify(result)
        except Exception as e:
            logger.error(f"检查登录失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/channel/status')
    @app.route('/api/channel/qrcode', methods=['POST'])
    def get_login_qrcode():
        """获取登录二维码"""
        global agent

        try:
            if agent is None:
                init_agent()

            result = agent.channel.get_login_qrcode()
            return jsonify(result)
        except Exception as e:
            logger.error(f"获取二维码失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    def channel_status():
        """获取通道状态"""
        global agent

        try:
            if agent is None:
                init_agent()

            return jsonify({
                'success': True,
                'connected': agent.channel._initialized,
                'mcp_url': agent.channel.url
            })
        except Exception as e:
            logger.error(f"获取通道状态失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    return app


def init_agent():
    """初始化 Agent"""
    global agent

    cfg = load_config()
    api_key = cfg.get_api_key()
    model = cfg.get_model()
    provider = cfg.get('llm_provider', 'minimax')
    mcp_url = cfg.get('mcp_url', 'http://localhost:18060/mcp')

    if api_key:
        os.environ[f"{provider.upper()}_API_KEY"] = api_key

    logger.info(f"初始化 Web Agent: {provider}/{model}")
    agent = XiaohongshuAgent(
        provider=provider,
        model=model,
        api_key=api_key,
        mcp_url=mcp_url
    )


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5003)), debug=True)
