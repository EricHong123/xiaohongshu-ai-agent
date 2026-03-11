"""
视频生成工作流 - 主流程编排
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .analyzer import ImageAnalyzer
from .script_generator import ScriptGenerator
from .video_generator import VideoGenerator
from .audio_generator import AudioGenerator
from .editor import VideoEditor
from .publisher import XiaohongshuPublisher


class VideoWorkflow:
    """
    小红书视频生成工作流

    流程:
    1. 分析产品图片 (多模态LLM)
    2. 生成脚本文案
    3. 生成视频片段 (可灵AI)
    4. 生成配音 (海螺TTS)
    5. 整合剪辑 (FFmpeg)
    6. 发布到小红书
    """

    def __init__(
        self,
        output_dir: str = "output/videos",
        config: Dict[str, Any] = None
    ):
        """
        初始化工作流

        Args:
            output_dir: 输出目录
            config: 配置字典
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 配置
        self.config = config or {}
        
        # 确保 config 是字典
        if self.config is None:
            self.config = {}

        # 初始化各模块
        self.analyzer = ImageAnalyzer(
            api_key=self.config.get("zhipu_api_key", os.getenv("ZHIPU_API_KEY")),
            model=self.config.get("image_analyzer_model", "glm-4.6v")
        )

        self.script_gen = ScriptGenerator(
            api_key=self.config.get("zhipu_api_key", os.getenv("ZHIPU_API_KEY")),
            model=self.config.get("script_model", "glm-4.6v")
        )

        self.video_gen = VideoGenerator(
            api_key=self.config.get("zhipu_api_key", os.getenv("ZHIPU_API_KEY")),
            model=self.config.get("video_model", "cogvideoX-3")
        )

        self.audio_gen = AudioGenerator(
            api_key=self.config.get("minimax_api_key", os.getenv("MINIMAX_API_KEY")),
            model=self.config.get("audio_model", "speech-01-turbo")
        )

        self.editor = VideoEditor(output_dir=output_dir)

        self.publisher = XiaohongshuPublisher(
            mcp_url=self.config.get("mcp_url", os.getenv("XHS_MCP_URL")),
            cookie=self.config.get("xhs_cookie", os.getenv("XHS_COOKIE"))
        )

    def run(
        self,
        image_paths: List[str],
        product_name: str = "",
        context: str = "",
        duration: int = 10,
        auto_publish: bool = False,
        voice: str = "male-qn-qingse"
    ) -> Dict[str, Any]:
        """
        执行完整工作流

        Args:
            image_paths: 产品图片路径列表
            product_name: 产品名称
            context: 额外上下文
            duration: 视频时长(秒)
            auto_publish: 是否自动发布到小红书
            voice: 配音音色

        Returns:
            完整结果字典
        """
        start_time = datetime.now()
        result = {
            "status": "started",
            "start_time": start_time.isoformat(),
            "steps": {}
        }

        # Step 1: 分析图片
        print("=" * 50)
        print("Step 1: 分析产品图片...")
        analysis_result = self.analyzer.analyze(
            image_paths=image_paths,
            product_name=product_name,
            context=context
        )
        result["steps"]["analysis"] = analysis_result

        if "error" in analysis_result:
            result["status"] = "failed"
            result["error"] = f"图片分析失败: {analysis_result['error']}"
            return result

        print(f"✅ 分析完成: {analysis_result.get('product_name', 'Unknown')}")

        # Step 2: 生成脚本
        print("=" * 50)
        print("Step 2: 生成视频脚本...")

        # 如果分析结果已经有脚本,直接使用
        if "script" in analysis_result and "shots" in analysis_result:
            script = analysis_result["script"]
            shots = analysis_result["shots"]
            print("✅ 使用分析生成的脚本")
        else:
            # 调用脚本生成器
            script_result = self.script_gen.generate(
                product_info={
                    "name": product_name,
                    "features": analysis_result.get("product_features", []),
                    "style": analysis_result.get("video_style", "种草")
                },
                duration=duration
            )

            if "error" in script_result:
                result["status"] = "failed"
                result["error"] = f"脚本生成失败: {script_result['error']}"
                return result

            script = script_result
            shots = script_result.get("shots", [])

        result["steps"]["script"] = {"script": script, "shots": shots}
        print(f"✅ 脚本生成完成: {script.get('title', '')}")

        # Step 3: 生成视频
        print("=" * 50)
        print("Step 3: 生成视频片段...")

        video_clips = []
        reference_image = image_paths[0] if image_paths else ""

        for i, shot in enumerate(shots):
            print(f"  生成第 {i+1}/{len(shots)} 个分镜...")

            video_result = self.video_gen.generate(
                prompt=shot.get("prompt", ""),
                image_path=reference_image if i == 0 else "",
                duration=shot.get("duration", 3),
                aspect_ratio="9:16"
            )

            # 等待视频生成完成
            if "task_id" in video_result:
                task_id = video_result["task_id"]
                print(f"    任务ID: {task_id}, 等待生成...")
                wait_result = self.video_gen.wait_for_completion(task_id)

                if wait_result.get("status") == "completed":
                    video_url = wait_result.get("video_url", "")
                    # 下载视频
                    clip_path = self._download_video(video_url, f"clip_{i+1}.mp4")
                    video_clips.append(clip_path)
                    print(f"    ✅ 第{i+1}个分镜完成")
                else:
                    print(f"    ❌ 第{i+1}个分镜失败: {wait_result.get('error', '未知错误')}")
            else:
                print(f"    ⚠️ 跳过: {video_result.get('error', '生成失败')}")

        result["steps"]["video"] = {"clips": video_clips}

        if not video_clips:
            result["status"] = "failed"
            result["error"] = "没有成功生成任何视频片段"
            return result

        # Step 4: 合并视频
        print("=" * 50)
        print("Step 4: 合并视频片段...")

        concat_result = self.editor.concat_videos(
            video_paths=video_clips,
            output_path=os.path.join(self.output_dir, "merged.mp4")
        )

        if "error" in concat_result:
            result["status"] = "failed"
            result["error"] = f"视频合并失败: {concat_result['error']}"
            return result

        merged_video = concat_result["output_path"]
        print(f"✅ 视频合并完成: {merged_video}")

        # Step 5: 生成配音
        print("=" * 50)
        print("Step 5: 生成配音...")

        audio_result = self.audio_gen.generate_from_script(
            script=script,
            voice=voice,
            output_dir=self.output_dir
        )

        if "error" in audio_result:
            result["status"] = "failed"
            result["error"] = f"音频生成失败: {audio_result['error']}"
            return result

        audio_path = audio_result.get("output_path", "")
        print(f"✅ 配音生成完成: {audio_path}")

        # Step 6: 合成最终视频
        print("=" * 50)
        print("Step 6: 合成最终视频...")

        final_result = self.editor.add_audio(
            video_path=merged_video,
            audio_path=audio_path,
            output_path=os.path.join(self.output_dir, "final.mp4"),
            fade_in=0.5,
            fade_out=1.0
        )

        if "error" in final_result:
            result["status"] = "failed"
            result["error"] = f"视频合成失败: {final_result['error']}"
            return result

        final_video = final_result["output_path"]
        result["steps"]["final"] = {
            "video": final_video,
            "audio": audio_path,
            "script": script
        }

        # Step 7: 发布
        if auto_publish:
            print("=" * 50)
            print("Step 7: 发布到小红书...")

            publish_result = self.publisher.publish(
                video_path=final_video,
                title=script.get("title", ""),
                content=script.get("hook", "") + "\n\n" + script.get("body", ""),
                tags=analysis_result.get("product_features", [])[:5]
            )

            result["steps"]["publish"] = publish_result

            if publish_result.get("status") == "success":
                print(f"✅ 发布成功! Note ID: {publish_result.get('note_id', '')}")
            else:
                print(f"⚠️ 发布准备就绪,请手动发布")

        # 完成
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result["status"] = "completed"
        result["end_time"] = end_time.isoformat()
        result["duration"] = duration
        result["output"] = {
            "video": final_video,
            "audio": audio_path,
            "script": script
        }

        print("=" * 50)
        print(f"🎉 工作流完成! 耗时: {duration:.1f}秒")
        print(f"📹 视频: {final_video}")

        return result

    def _download_video(self, url: str, filename: str) -> str:
        """下载视频"""
        import requests

        output_path = os.path.join(self.output_dir, filename)

        try:
            resp = requests.get(url, timeout=120)
            with open(output_path, "wb") as f:
                f.write(resp.content)
            return output_path
        except Exception as e:
            print(f"下载视频失败: {e}")
            return ""

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        return self.video_gen.query_task(task_id)

    def test(self) -> Dict[str, Any]:
        """测试所有组件连接"""
        results = {}

        # 测试智谱API
        try:
            test_result = self.script_gen.generate(
                product_info={"name": "测试产品", "features": ["测试"]},
                duration=5
            )
            if isinstance(test_result, dict):
                results["zhipu"] = "✅ OK" if "error" not in test_result else f"❌ {test_result.get('error', '未知错误')}"
            else:
                results["zhipu"] = "✅ OK"
        except Exception as e:
            results["zhipu"] = f"❌ {str(e)}"

        # 测试可灵API
        if os.getenv("KLING_ACCESS_KEY"):
            results["cogvideo"] = "✅ 已配置 (cogvideoX-3)"
        else:
            results["cogvideo"] = "⚠️ 未配置 ZHIPU_API_KEY"

        # 测试海螺API
        if os.getenv("MINIMAX_API_KEY"):
            results["minimax"] = "✅ 已配置"
        else:
            results["minimax"] = "⚠️ 未配置 MINIMAX_API_KEY"

        return results
