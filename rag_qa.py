import os
import requests
import openai
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# 1. 路径与环境准备
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(BASE_DIR, "等级标准节选.txt")
PERSIST = os.path.join(BASE_DIR, "chroma_db")

# 加载 .env (用于云端大模型，如果你只用本地，不配也行)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 2. 定义统一的大模型入口 (极简版，兼容本地和云端)
def llm_ask(prompt, prefer="local"):
    if prefer == "local":
        try:
            r = requests.post("http://localhost:11434/api/chat", json={
                "model": "qwen2.5:0.5b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }, timeout=60)
            r.raise_for_status()
            return r.json()["message"]["content"]
        except Exception as e:
            print(f"[本地失败] {e}")
            return "本地模型调用失败"
    else:
        client = openai.OpenAI(base_url="https://api.deepseek.com/v1", api_key=os.getenv("DEEPSEEK_API_KEY"))
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content

# 3. RAG 核心：建库与检索
def get_retriever(k=2, rebuild=False):
    emb = OllamaEmbeddings(model="nomic-embed-text")
    if not rebuild and os.path.exists(PERSIST) and os.listdir(PERSIST):
        vs = Chroma(persist_directory=PERSIST, embedding_function=emb)
    else:
        docs = TextLoader(CORPUS, encoding="utf-8").load()
        splits = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20).split_documents(docs)
        vs = Chroma.from_documents(splits, emb, persist_directory=PERSIST)
    return vs.as_retriever(search_kwargs={"k": k})

def retrieve(question):
    return "\n".join(d.page_content for d in get_retriever().invoke(question))

# 4. RAG 核心：生成
def rag_qa(question, prefer="local"):
    ctx = retrieve(question)
    print(f"\n--- 🔍 检索到的参考资料 ---\n{ctx}\n--------------------------")
    
    prompt = f"根据以下资料回答问题，资料中没有的内容就如实说「资料中未提及」：\n{ctx}\n\n问题：{question}"
    return llm_ask(prompt, prefer=prefer)

# 5. 运行测试（生成你的作业数据）
if __name__ == "__main__":
    q = "HSK四级阅读考试时长是多久？"
    
    print("=====================================")
    print(f"❓ 测试问题：{q}")
    
    print("\n🚫 1. 裸答（直接问，不给资料）：")
    print(llm_ask(q, prefer="local"))
    
    print("\n✅ 2. RAG 答（给了资料再问）：")
    print(rag_qa(q, prefer="local"))
    print("=====================================")
