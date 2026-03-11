"""
小红书视频生成工作流

功能:
- 多模态LLM分析产品图片
- 生成脚本文案和运镜分镜
- 调用可灵AI生成视频
- 调用海螺生成音频
- FFmpeg整合剪辑
- 自动发布到小红书
"""

from .pipeline import VideoWorkflow
from .analyzer import ImageAnalyzer
from .script_generator import ScriptGenerator
from .video_generator import VideoGenerator
from .audio_generator import AudioGenerator
from .editor import VideoEditor
from .publisher import XiaohongshuPublisher

__all__ = [
    "VideoWorkflow",
    "ImageAnalyzer",
    "ScriptGenerator",
    "VideoGenerator",
    "AudioGenerator",
    "VideoEditor",
    "XiaohongshuPublisher",
]
