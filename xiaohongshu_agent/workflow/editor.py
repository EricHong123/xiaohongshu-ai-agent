"""
视频剪辑器 - 使用MoviePy整合视频和音频
"""
import os
import subprocess
from typing import List, Dict, Any, Optional


class VideoEditor:
    """视频剪辑整合"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def concat_videos(
        self,
        video_paths: List[str],
        output_path: str = "",
        transitions: List[str] = None
    ) -> Dict[str, Any]:
        """
        合并多个视频

        Args:
            video_paths: 视频路径列表
            output_path: 输出路径
            transitions: 转场效果列表

        Returns:
            结果
        """
        if not video_paths:
            return {"error": "没有视频文件"}

        if not output_path:
            output_path = os.path.join(self.output_dir, "concat.mp4")

        # 使用FFmpeg合并
        try:
            # 创建临时文件列表
            list_path = os.path.join(self.output_dir, "video_list.txt")
            with open(list_path, "w") as f:
                for path in video_paths:
                    if not path:
                        continue
                    # 如果是绝对路径或包含output_dir前缀,提取文件名
                    if os.path.isabs(path):
                        filename = os.path.basename(path)
                    elif self.output_dir and path.startswith(self.output_dir):
                        filename = path[len(self.output_dir)+1:]
                    else:
                        filename = os.path.basename(path)
                    f.write(f"file '{filename}'\n")

            # FFmpeg合并命令
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_path,
                "-c", "copy",
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            os.remove(list_path)

            return {
                "status": "success",
                "output_path": output_path
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"视频合并失败: {e.stderr.decode() if e.stderr else str(e)}"}
        except FileNotFoundError:
            return {"error": "请安装FFmpeg: brew install ffmpeg"}

    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str = "",
        audio_volume: float = 1.0,
        fade_in: float = 0,
        fade_out: float = 0
    ) -> Dict[str, Any]:
        """
        为视频添加音频

        Args:
            video_path: 视频路径
            audio_path: 音频路径
            output_path: 输出路径
            audio_volume: 音频音量
            fade_in: 音频淡入时长
            fade_out: 音频淡出时长

        Returns:
            结果
        """
        if not output_path:
            output_path = video_path.replace(".mp4", "_with_audio.mp4")

        try:
            cmd = ["ffmpeg", "-y"]

            # 输入视频
            cmd.extend(["-i", video_path])

            # 输入音频
            cmd.extend(["-i", audio_path])

            # 音频处理
            if fade_in > 0 or fade_out > 0:
                # 构建音频滤镜
                audio_filter = f"volume={audio_volume}"
                if fade_in > 0:
                    audio_filter += f",afade=t=in:st=0:d={fade_in}"
                if fade_out > 0:
                    # 需要获取视频时长
                    duration = self.get_duration(video_path)
                    audio_filter += f",afade=t=out:st={duration - fade_out}:d={fade_out}"

                cmd.extend(["-af", audio_filter])
            else:
                cmd.extend(["-filter:a", f"volume={audio_volume}"])

            # 复制视频流,替换音频
            cmd.extend(["-c:v", "copy", "-c:a", "aac", "-shortest", output_path])

            subprocess.run(cmd, check=True, capture_output=True)

            return {
                "status": "success",
                "output_path": output_path
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"添加音频失败: {e.stderr.decode() if e.stderr else str(e)}"}
        except FileNotFoundError:
            return {"error": "请安装FFmpeg: brew install ffmpeg"}

    def add_subtitle(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str = "",
        style: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        添加字幕

        Args:
            video_path: 视频路径
            subtitle_path: 字幕文件路径(.srt)
            output_path: 输出路径
            style: 字幕样式

        Returns:
            结果
        """
        if not output_path:
            output_path = video_path.replace(".mp4", "_subtitled.mp4")

        if style is None:
            style = {
                "font": "Arial",
                "font_size": 24,
                "font_color": "white",
                "background_color": "black@0.5",
                "position": "bottom"
            }

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", f"subtitles='{subtitle_path}'",
                "-c:a", "copy",
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            return {
                "status": "success",
                "output_path": output_path
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"添加字幕失败: {str(e)}"}

    def resize(
        self,
        video_path: str,
        width: int = 1080,
        height: int = 1920,
        output_path: str = ""
    ) -> Dict[str, Any]:
        """
        调整视频尺寸

        Args:
            video_path: 视频路径
            width: 目标宽度
            height: 目标高度
            output_path: 输出路径

        Returns:
            结果
        """
        if not output_path:
            output_path = video_path.replace(".mp4", "_resized.mp4")

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vf", f"scale={width}:{height}",
                "-c:a", "copy",
                output_path
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            return {
                "status": "success",
                "output_path": output_path
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"调整尺寸失败: {str(e)}"}

    def get_duration(self, video_path: str) -> float:
        """获取视频时长"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return 0

    def create_vertical_from_horizontal(
        self,
        video_path: str,
        output_path: str = "",
        blur_background: bool = True
    ) -> Dict[str, Any]:
        """
        横屏转竖屏 (加模糊背景)

        Args:
            video_path: 视频路径
            output_path: 输出路径
            blur_background: 是否模糊背景

        Returns:
            结果
        """
        if not output_path:
            output_path = video_path.replace(".mp4", "_vertical.mp4")

        try:
            if blur_background:
                # 使用boxblur滤镜创建模糊背景,然后叠加视频
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,boxblur=20:5,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
                    "-c:a", "copy",
                    output_path
                ]
            else:
                # 直接居中填充黑边
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                    "-c:a", "copy",
                    output_path
                ]

            subprocess.run(cmd, check=True, capture_output=True)

            return {
                "status": "success",
                "output_path": output_path
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"转换失败: {str(e)}"}
