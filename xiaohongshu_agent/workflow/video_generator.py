"""
视频生成器 - 使用智谱CogVideoX
"""
import time
from typing import List, Dict, Any, Optional


class VideoGenerator:
    """智谱CogVideo视频生成器"""

    def __init__(
        self,
        api_key: str = "",
        model: str = "cogvideoX-3"
    ):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
        self.model = model

        # 延迟导入zhipuai SDK
        self._client = None

    def _get_client(self):
        """获取智谱客户端"""
        if self._client is None:
            import zhipuai
            self._client = zhipuai.ZhipuAI(api_key=self.api_key)
        return self._client

    def generate(
        self,
        prompt: str,
        image_path: str = "",
        duration: float = 5.0,
        aspect_ratio: str = "9:16"
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 视频生成提示词
            image_path: 参考图片路径(可选)
            duration: 时长(秒)
            aspect_ratio: 宽高比 (9:16, 16:9, 1:1)

        Returns:
            任务信息,包含task_id用于查询结果
        """
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY"}

        try:
            client = self._get_client()

            # 构建请求参数
            kwargs = {
                "model": self.model,
                "prompt": prompt
            }

            # 如果有图片，添加图片
            if image_path:
                import base64
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                kwargs["image_url"] = f"data:image/jpeg;base64,{img_b64}"

            # 调用生成接口
            response = client.videos.generations(**kwargs)

            if hasattr(response, 'id'):
                return {
                    "status": "processing",
                    "task_id": response.id,
                    "duration": duration
                }
            elif hasattr(response, 'task_status') and response.task_status == "SUCCESS":
                return {
                    "status": "completed",
                    "video_url": response.video_result[0].url if response.video_result else "",
                    "cover_url": response.video_result[0].cover_image_url if response.video_result else ""
                }
            else:
                return {"error": str(response)}

        except Exception as e:
            return {"error": f"生成失败: {str(e)}"}

    def generate_from_script(
        self,
        shots: List[Dict[str, Any]],
        reference_image: str = ""
    ) -> List[Dict[str, Any]]:
        """根据分镜列表生成视频片段"""
        results = []

        for i, shot in enumerate(shots):
            print(f"正在生成第 {i+1}/{len(shots)} 个分镜...")
            result = self.generate(
                prompt=shot.get("prompt", ""),
                image_path=reference_image if i == 0 else "",
                duration=shot.get("duration", 5)
            )
            results.append({
                "index": shot.get("index", i + 1),
                "prompt": shot.get("prompt", ""),
                "result": result
            })

            if i < len(shots) - 1:
                time.sleep(1)

        return results

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        try:
            client = self._get_client()
            result = client.videos.retrieve_videos_result(task_id)

            status = result.task_status

            if status == "SUCCESS":
                return {
                    "status": "completed",
                    "video_url": result.video_result[0].url if result.video_result else "",
                    "cover_url": result.video_result[0].cover_image_url if result.video_result else ""
                }
            elif status == "FAILED":
                return {
                    "status": "failed",
                    "error": "视频生成失败"
                }
            else:
                return {
                    "status": "processing",
                    "progress": 0
                }

        except Exception as e:
            return {"error": str(e)}

    def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 300,
        interval: int = 3
    ) -> Dict[str, Any]:
        """等待视频生成完成"""
        elapsed = 0

        while elapsed < max_wait:
            result = self.query_task(task_id)

            if result.get("status") == "completed":
                return result
            elif result.get("status") == "failed":
                return result

            print(f"等待中... ({elapsed}s)")
            time.sleep(interval)
            elapsed += interval

        return {"error": "等待超时"}
