"""
视频生成工作流 API 模块
"""
import os
from flask import jsonify, request
from xiaohongshu_agent.workflow import VideoWorkflow


def register_video_routes(app):
    """注册视频工作流相关路由"""

    @app.route('/video')
    def video_page():
        from flask import render_template; return render_template('video.html')

    @app.route('/api/video/test')
    def video_test():
        """测试视频工作流组件"""
        try:
            workflow = VideoWorkflow()
            status = workflow.test()
            return jsonify({'status': status, 'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/video/voices')
    def video_voices():
        """获取可用音色"""
        try:
            from xiaohongshu_agent.workflow import AudioGenerator
            gen = AudioGenerator()
            voices = gen.get_available_voices()
            return jsonify({'voices': voices, 'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/video/generate', methods=['POST'])
    def video_generate():
        """生成视频"""
        data = request.json or {}
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
            return jsonify({'error': str(e)}), 500

    @app.route('/api/video/config', methods=['GET', 'POST'])
    def video_config():
        """视频工作流配置"""
        if request.method == 'POST':
            data = request.json or {}
            for key in ['zhipu_api_key', 'kling_api_key', 'minimax_api_key']:
                if key in data and data[key]:
                    os.environ[key.upper()] = data[key]
            return jsonify({'success': True, 'message': '配置已保存'})

        return jsonify({
            'success': True,
            'config': {
                'zhipu': bool(os.getenv('ZHIPU_API_KEY')),
                'kling': bool(os.getenv('KLING_API_KEY')),
                'minimax': bool(os.getenv('MINIMAX_API_KEY'))
            }
        })
