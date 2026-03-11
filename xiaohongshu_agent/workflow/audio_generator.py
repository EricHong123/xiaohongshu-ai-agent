"""
音频生成器 - 使用海螺/MiniMax TTS生成配音
"""
import os
import requests
import json
import base64
from typing import Dict, Any, Optional


class AudioGenerator:
    """海螺/MiniMax TTS音频生成"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.minimax.chat",
        model: str = "speech-01-turbo"
    ):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = base_url
        self.model = model

    def generate(
        self,
        text: str,
        voice: str = "male-qn-qingse",
        speed: float = 1.0,
        volume: float = 1.0,
        pitch: float = 0.0,
        output_path: str = ""
    ) -> Dict[str, Any]:
        """
        生成音频

        Args:
            text: 要转换的文本
            voice: 音色选择
            speed: 语速 (0.5-2.0)
            volume: 音量 (0.1-2.0)
            pitch: 音调 (-12-12)
            output_path: 输出文件路径

        Returns:
            生成结果
        """
        if not self.api_key:
            return {"error": "请配置 MINIMAX_API_KEY 环境变量"}

        url = f"{self.base_url}/v1/t2a_v2"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "text": text,
            "voice_setting": {
                "voice_id": voice,
                "speed": int(speed * 100),  # 转换为整数百分比
                "volume": int(volume * 100),  # 转换为整数百分比
                "pitch": int(pitch)  # 转换为整数
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "wav"
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            result = resp.json()

            if "data" in result and "audio" in result["data"]:
                audio_data = result["data"]["audio"]

                # 解码base64
                audio_bytes = base64.b64decode(audio_data)

                # MiniMax返回的是PCM格式,需要添加WAV头
                if output_path:
                    # 保存为WAV格式
                    wav_path = output_path.replace('.mp3', '.wav')
                    try:
                        import wave
                        with wave.open(wav_path, 'wb') as wav_file:
                            wav_file.setnchannels(1)  # 单声道
                            wav_file.setsampwidth(2)  # 16位
                            wav_file.setframerate(32000)  # 32kHz
                            wav_file.writeframes(audio_bytes)
                        
                        # 同时保存原始PCM
                        pcm_path = output_path.replace('.mp3', '.pcm')
                        with open(pcm_path, 'wb') as f:
                            f.write(audio_bytes)
                        
                        return {
                            "status": "success",
                            "output_path": wav_path,
                            "duration": result.get("data", {}).get("audio_size", 0)
                        }
                    except Exception as e:
                        # 如果WAV创建失败,保存原始数据
                        with open(output_path, "wb") as f:
                            f.write(audio_bytes)
                        return {
                            "status": "success",
                            "output_path": output_path,
                            "duration": result.get("data", {}).get("audio_size", 0)
                        }
                else:
                    return {
                        "status": "success",
                        "audio_data": audio_bytes,
                        "duration": result.get("data", {}).get("audio_size", 0)
                    }
            else:
                return {"error": result.get("base_resp", {}).get("status_msg", "生成失败")}

        except Exception as e:
            return {"error": f"音频生成失败: {str(e)}"}

    def generate_from_script(
        self,
        script: Dict[str, Any],
        voice: str = "male-qn-qingse",
        output_dir: str = "output/audio"
    ) -> Dict[str, Any]:
        """
        根据脚本生成完整音频

        Args:
            script: 脚本字典,包含 hook, body, cta
            voice: 音色
            output_dir: 输出目录

        Returns:
            生成的音频信息
        """
        os.makedirs(output_dir, exist_ok=True)

        # 合并所有文本
        full_text = ""
        if "hook" in script:
            full_text += script["hook"] + " "
        if "body" in script:
            full_text += script["body"] + " "
        if "cta" in script:
            full_text += script["cta"]

        if not full_text.strip():
            return {"error": "脚本内容为空"}

        output_path = os.path.join(output_dir, "audio.wav")

        result = self.generate(
            text=full_text,
            voice=voice,
            output_path=output_path
        )

        return result

    def get_available_voices(self) -> Dict[str, List[str]]:
        """获取可用的音色列表"""
        return {
            "male": [
                "male-qn-qingse",  # 青涩青年
                "male-qn-jingying",  # 精英青年
                "male-qn-badao",  # 霸道总裁
                "male-qn-daqiao",  # 大乔
                "male-qn-xiaojie",  # 少女
            ],
            "female": [
                "female-shaonv",  # 活泼少女
                "female-yujie",  # 温柔御姐
                "female-chengshu",  # 成熟女性
                "female-badao",  # 霸道女总
            ]
        }

    def estimate_duration(
        self,
        text: str,
        speed: float = 1.0
    ) -> float:
        """
        估算音频时长

        Args:
            text: 文本
            speed: 语速

        Returns:
            预估时长(秒)
        """
        # 中文平均每分钟200-250字
        chars_per_minute = 225 * speed
        duration = (len(text) / chars_per_minute) * 60
        return duration
