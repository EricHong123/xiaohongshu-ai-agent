"""
视频生成器 - 使用智谱 CogVideoX (直接调用 HTTP API，避免 SDK 与 Python 3.14 兼容性问题)
"""
import os
import time
from typing import List, Dict, Any, Optional

import requests


class VideoGenerator:
    """智谱 CogVideoX 视频生成器"""

    def __init__(
        self,
        api_key: str = "",
        model: str = "cogvideox-3",
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY", "")
        self.model = model

        _raw_base = (base_url or os.getenv("ZHIPU_BASE_URL") or "").strip()
        # 仅当配置为合法 URL（含 scheme）时使用，避免误把 API Key 填到 ZHIPU_BASE_URL
        if _raw_base and (_raw_base.startswith("http://") or _raw_base.startswith("https://")):
            self.base_url = _raw_base.rstrip("/")
        else:
            self.base_url = "https://open.bigmodel.cn/api"
        # 备用网关（当前网关连接失败时自动尝试）
        self._fallback_base_url = (
            "https://api.z.ai/api"
            if "open.bigmodel.cn" in self.base_url
            else "https://open.bigmodel.cn/api"
        )

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
            aspect_ratio: 宽高比 (9:16)

        Returns:
            任务信息,包含task_id用于查询结果
        """
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 构建请求参数（对齐官方文档 /paas/v4/videos/generations）
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
        }

        # 如果有参考图片，按 data:image/jpeg;base64, 传入 image_url
        if image_path:
            import base64

            try:
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                payload["image_url"] = f"data:image/jpeg;base64,{img_b64}"
            except OSError as e:  # 文件读失败直接返回
                return {"error": f"参考图片读取失败: {e}"}

        def _do_post(post_url: str):
            resp = requests.post(post_url, json=payload, headers=headers, timeout=30)
            if resp.status_code != 200:
                try:
                    err_json = resp.json()
                    return {"error": f"HTTP {resp.status_code}: {err_json.get('message', err_json)}"}
                except Exception:
                    return {"error": f"HTTP {resp.status_code}: {resp.text}"}
            return resp.json()

        last_error: Optional[Exception] = None
        last_url: Optional[str] = None

        for base in [self.base_url, self._fallback_base_url]:
            url = f"{base}/paas/v4/videos/generations"
            for attempt in range(2):
                try:
                    resp_data = _do_post(url)
                    if isinstance(resp_data, dict) and "error" in resp_data:
                        return resp_data
                    data = resp_data
                    if "id" in data:
                        return {
                            "status": data.get("task_status", "processing"),
                            "task_id": data["id"],
                            "duration": duration,
                        }
                    if data.get("task_status") == "SUCCESS":
                        videos = data.get("video_result") or []
                        first = videos[0] if videos else {}
                        return {
                            "status": "completed",
                            "video_url": first.get("url", ""),
                            "cover_url": first.get("cover_image_url", ""),
                        }
                    return {"error": f"未知响应格式: {data}"}
                except requests.exceptions.RequestException as e:
                    last_error = e
                    last_url = url
                    if attempt < 1:
                        time.sleep(2)
                        continue
                    break
            # 当前网关都失败，尝试下一个 base
            if last_error and "Connection" in str(last_error):
                time.sleep(1)
                continue
            break

        if last_error:
            msg = str(last_error)
            hint = f"尝试过的地址: {last_url or 'N/A'}。请检查网络、代理或 config/.env 中 ZHIPU_BASE_URL。"
            if "Connection" in msg or "Timeout" in msg:
                return {"error": f"无法连接智谱视频服务: {msg}。{hint}"}
            return {"error": f"生成失败: {msg}"}

        return {"error": "生成失败: 未知错误"}

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
        """查询任务状态（调用 GET /paas/v4/async-result/{id}）"""
        if not self.api_key:
            return {"error": "请配置 ZHIPU_API_KEY"}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        for base in [self.base_url, self._fallback_base_url]:
            url = f"{base}/paas/v4/async-result/{task_id}"
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    try:
                        err_json = resp.json()
                        return {"error": f"HTTP {resp.status_code}: {err_json.get('message', err_json)}"}
                    except Exception:
                        return {"error": f"HTTP {resp.status_code}: {resp.text}"}
                data = resp.json()
                status = data.get("task_status", "").upper()
                if status == "SUCCESS":
                    videos = data.get("video_result") or []
                    first = videos[0] if videos else {}
                    return {
                        "status": "completed",
                        "video_url": first.get("url", ""),
                        "cover_url": first.get("cover_image_url", ""),
                    }
                if status == "FAIL":
                    return {"status": "failed", "error": "视频生成失败"}
                return {"status": "processing", "progress": 0}
            except requests.exceptions.RequestException as e:
                if base == self._fallback_base_url:
                    return {"error": f"查询任务失败: {e}"}
                continue
        return {"error": "查询任务失败: 两个网关均无法连接"}

    def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 600,
        interval: int = 5
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
