"""
视频生成工作流 API 模块
"""
import os
from flask import jsonify, request, send_from_directory
from xiaohongshu_agent.workflow import VideoWorkflow

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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

    @app.route('/api/video/list')
    def video_list():
        """获取视频列表"""
        try:
            videos = []
            video_dirs = ["output/web_videos", "output/videos", "output/test_video"]
            
            for video_dir in video_dirs:
                full_dir = os.path.join(PROJECT_ROOT, video_dir)
                if os.path.exists(full_dir):
                    for f in os.listdir(full_dir):
                        if f.endswith('.mp4'):
                            filepath = os.path.join(full_dir, f)
                            stat = os.stat(filepath)
                            videos.append({
                                'name': f,
                                'path': os.path.join(video_dir, f),
                                'dir': video_dir,
                                'size': stat.st_size,
                                'time': stat.st_mtime
                            })
            
            # 按时间排序
            videos.sort(key=lambda x: x['time'], reverse=True)
            
            return jsonify({'videos': videos[:20], 'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # 服务视频文件
    @app.route('/files/<path:subpath>')
    def serve_file(subpath):
        """服务文件下载"""
        # 安全检查
        if '..' in subpath or subpath.startswith('/'):
            return "Forbidden", 403
        
        # 使用项目根目录
        full_path = os.path.join(PROJECT_ROOT, subpath)
        
        # 确保文件存在
        if not os.path.exists(full_path):
            return "File not found", 404
        
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)

    @app.route('/api/video/upload', methods=['POST'])
    def video_upload():
        """上传图片"""
        try:
            from werkzeug.utils import secure_filename
            import uuid
            
            if 'images' not in request.files:
                return jsonify({'error': '没有文件'}), 400
            
            files = request.files.getlist('images')
            if not files:
                return jsonify({'error': '没有文件'}), 400
            
            # 确保上传目录存在
            upload_dir = os.path.join(PROJECT_ROOT, 'output', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            saved_paths = []
            for f in files:
                if f.filename:
                    ext = os.path.splitext(f.filename)[1]
                    filename = f"{uuid.uuid4().hex}{ext}"
                    filepath = os.path.join(upload_dir, filename)
                    f.save(filepath)
                    # 返回可以访问的路径
                    saved_paths.append(f"/output/uploads/{filename}")
            
            return jsonify({'success': True, 'paths': saved_paths})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/output/<path:subpath>')
    def serve_output(subpath):
        """服务output目录下的文件"""
        if '..' in subpath:
            return "Forbidden", 403
        full_path = os.path.join(PROJECT_ROOT, 'output', subpath)
        if not os.path.exists(full_path):
            return "File not found", 404
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)
