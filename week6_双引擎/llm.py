import os
import requests
import openai
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class LocalEngine:
    def __init__(self, model=None):
        self.model = model or "qwen2.5:0.5b"

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json()["message"]["content"]

class APIEngine:
    def __init__(self):
        self.client = None

    def _ensure_client(self):
        if self.client is None:
            self.client = openai.OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=os.getenv("DEEPSEEK_API_KEY")
            )

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        self._ensure_client()
        r = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return r.choices[0].message.content

class LLM:
    def __init__(self, local_model=None):
        self.local = LocalEngine(local_model)
        self.api = APIEngine()

    def ask(self, prompt, prefer="local"):
        if prefer == "local":
            try:
                return self.local.ask(prompt)
            except Exception as e:
                print(f"[本地失败，自动切换云端] 原因：{type(e).__name__} - {e}")
                return self.api.ask(prompt)
        elif prefer == "api":
            try:
                return self.api.ask(prompt)
            except Exception as e:
                print(f"[云端失败，自动切换本地] 原因：{type(e).__name__} - {e}")
                return self.local.ask(prompt)
        else:
            raise ValueError("prefer 必须是 'local' 或 'api'")
