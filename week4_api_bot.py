# W4 命令行学科问答机器人（API 版）—— 独立版
# 依赖：pip install openai python-dotenv
# 运行：python week4_api_bot.py "把字句的教学难点有哪些"
import os
import sys
import openai

# 1. 自动获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 读取同目录下的 .env 文件，加载密钥
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 3. API 配置（DeepSeek）
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

# 4. 日志文件路径（和脚本放在一起）
LOG_FILE = os.path.join(BASE_DIR, "chat_log.txt")

_client = None


def get_client():
    """按需创建客户端：没配密钥时抛出友好提示。"""
    global _client
    if _client is None:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("未配置 DEEPSEEK_API_KEY")
        _client = openai.OpenAI(base_url=BASE_URL, api_key=key)
    return _client


def ask(question, temperature=0.7, max_tokens=800):
    r = get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content


if __name__ == "__main__":
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("错误：未设置 DEEPSEEK_API_KEY。")
        print("  处理：请确认 .env 文件就在本脚本的同一个文件夹里，且里面填了密钥。")
        sys.exit(1)

    q = " ".join(sys.argv[1:]) or "把字句的教学难点有哪些"

    try:
        ans = ask(q,temperature=0.7,max_tokens=800)
    except openai.APITimeoutError:
        print("错误：请求超时，请检查网络或调大 timeout。")
        sys.exit(1)

    print(ans)

    # 追加日志
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("Q: %s\nA: %s\n\n" % (q, ans))