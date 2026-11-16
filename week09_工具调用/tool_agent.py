# W9 手写最小工具调用循环（不用框架）
# 依赖：pip install openai python-dotenv
import os
import csv
import sys
import ast
import json
import re
import operator
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  数据路径 + 加载 .env

weekpath.load_env()

import openai  # noqa: E402

VOCAB = weekpath.data_path("生词表.csv")

# 默认走 DeepSeek 云端；教师机演示可通过环境变量切到本机 Ollama
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("未配置 DEEPSEEK_API_KEY，请先在 .env 中填写")
        base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        _client = openai.OpenAI(base_url=base, api_key=key)
    return _client


def get_time():
    return str(datetime.datetime.now())


# ---- 安全计算：白名单 AST，绝不使用裸 eval ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只允许数字与 + - * / ** % 运算")


def calc(expr):
    """教学演示用：只做四则运算。"""
    try:
        return str(_eval_node(ast.parse(str(expr), mode="eval")))
    except ZeroDivisionError:
        return "错误：除数为 0"
    except Exception as e:
        return "拒绝计算：%s" % e


def hsk_level(word):
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["词汇"].strip() == str(word).strip():
                return "%s 是 %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


# ---- 新增：作业2的第四工具（课文难度评估） ----
def evaluate_text(text, target_level):
    """评估课文难度：输入一段文字和目标等级（如'HSK 3'），返回超纲词列表。"""
    word_dict = {}
    try:
        with open(VOCAB, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                lvl_str = row["HSK等级"].strip().replace("HSK", "").strip()
                word_dict[row["词汇"].strip()] = lvl_str
    except Exception as e:
        return "读取生词表失败：%s" % e

    out_of_syllabus = []
    target_str = str(target_level).replace("HSK", "").strip()
    
    for char in text:
        if char in word_dict:
            level = word_dict[char]
            try:
                if int(target_str) < int(level):
                    out_of_syllabus.append(char)
            except ValueError:
                pass
    
    out_of_syllabus = list(set(out_of_syllabus))
    if not out_of_syllabus:
        return "没有超纲词，完美符合 HSK %s 难度！" % target_str
    else:
        return "超纲词有：%s" % "、".join(out_of_syllabus)


# 把新工具加进字典里
TOOLS = {
    "get_time": get_time, 
    "calc": calc, 
    "hsk_level": hsk_level,
    "evaluate_text": evaluate_text
}

# 更新提示词，告诉模型有4个工具
SYS = ("你是国际中文助教。可用工具只有这 4 个：get_time（查当前时间，无参数）、"
       "calc（四则运算，如 calc('35*24')）、hsk_level（查生词 HSK 等级，如 hsk_level('把')）、"
       "evaluate_text（评估课文难度，如 evaluate_text('我们学习中文', 'HSK 2')）。"
       '如需调用，只输出一行 JSON，格式：{"tool": "工具名", "args": [参数]}；'
       "一次只调用一个工具，绝不编造不存在的工具名；无需工具时直接回答。")


def parse_calls(txt):
    """容错解析：剥掉 ```json 围栏与前后客套话，返回全部工具调用（0/1/多个）。"""
    s = (txt or "").strip()
    s = s.replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
        return [obj] if isinstance(obj, dict) else []
    except Exception:
        m = re.search(r"\{.*\}", s, re.S)
        if m:
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict):
                    return [obj]
            except Exception:
                pass
        calls = []
        for blk in re.findall(r"\{[^{}]*\}", s):
            try:
                obj = json.loads(blk)
            except Exception:
                continue
            if isinstance(obj, dict):
                calls.append(obj)
        return calls


def run(user_msg, max_calls=2):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user_msg}]
    for _ in range(max_calls):
        txt = get_client().chat.completions.create(
            model=MODEL, messages=msgs).choices[0].message.content
        calls = [c for c in parse_calls(txt)
                 if isinstance(c.get("tool"), str) and c.get("tool") in TOOLS]
        if not calls:
            return txt
        results = []
        for call in calls:
            args = call.get("args") or []
            if not isinstance(args, list):
                results.append("工具参数格式错误：%r" % (args,))
                continue
            try:
                results.append("%s%r → %s" % (call["tool"], args, TOOLS[call["tool"]](*args)))
            except Exception as e:
                results.append("工具执行失败：%s" % e)
        msgs += [{"role": "assistant", "content": txt},
                 {"role": "user", "content": "工具返回：%s。请据此作答。" % "；".join(results)}]
    return get_client().chat.completions.create(
        model=MODEL, messages=msgs).choices[0].message.content


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？"
    print("用户输入：", q)
    print("助手：", run(q))
