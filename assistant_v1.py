import os
from llm import LLM 
from rag_qa import retrieve, build_prompt 

# W2的提示词库落地
SYSTEM_HINT = "你是国际中文教学助手，面向HSK3-4学习者，回答需给出依据。"

llm = LLM()

def answer(question, use_rag=True, prefer="local"):
    if use_rag:
        ctx = retrieve(question)
        prompt = SYSTEM_HINT + "\n" + build_prompt(question, ctx)
    else:
        prompt = SYSTEM_HINT + "\n" + question
    return llm.ask(prompt, prefer=prefer)

if __name__ == "__main__":
    questions = [
        "把字句的教学难点有哪些",
        "HSK4词汇量要求是多少",
        "《愚公移山》可以设计什么课堂活动"
    ]
    
    for q in questions:
        print(f"Q: {q}")
        try:
            # 这里你可以故意改成 use_rag=False 看看纯对话的区别
            ans = answer(q, use_rag=True, prefer="local") 
            print(f"A: {ans}")
        except Exception as e:
            print(f"A: [运行失败] {str(e)}")
        print("-" * 40)