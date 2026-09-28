# 修改后的 vocab_tool.py（最终优化版）
import os
import csv
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "生词表.csv")
OUTPUT = os.path.join(BASE_DIR, "练习.txt")

# 人类专属“特殊词汇”模板库，专门修正AI的语义盲区
SPECIAL_TEMPLATES = {
    "把字句": [
        "请用“把字句”改写句子：他关上了门。",
        "请用“把字句”造一个句子。"
    ],
    "感动": [
        "听到这个故事，大家都非常___。",
        "这部电影的情节让他深深___。"
    ],
    "商量": [
        "我们明天一起___这件事吧。"
    ],
    "坚持": [
        "他给我讲了一个关于___的故事。",
        "由于他的___，最终完成了任务。"
    ]
}

def load_words(path=DATA):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def filter_by_level(words, level="4"):
    return [w for w in words if str(w["HSK等级"]) == str(level)]

def count_by_pos(words):
    d = {}
    for w in words:
        d[w["词性"]] = d.get(w["词性"], 0) + 1
    return d

def gen_fill_in_the_blank(words, out=None):
    """生成填空题：把目标词挖空成 ___"""
    out = out or OUTPUT

    # 通用词性模板
    templates = {
        "动词": [
            "关于{词}，每个人都有自己的想法。", 
            "他给我讲了一个关于{词}的故事。"
        ],
        "名词": [
            "这个{词}非常重要。",
            "我们需要了解{词}的意思。"
        ],
        "成语": [
            "他做事总是有{词}的精神。",
            "古人用{词}来比喻坚持不懈。"
        ],
        "介词": [
            "请把{词}放在桌子上。"
        ],
        "动词短语": [
            "他们正在{词}，非常辛苦。",
            "我们要学习{词}的精神。"
        ],
        "名词短语": [
            "这{词}表示时间的变化。"
        ]
    }

    default_templates = ["请用“{词}”造一个句子。"]

    with open(out, "w", encoding="utf-8") as f:
        for w in words:
            word = w["词汇"]
            pos = w["词性"]

            # 优先使用人工设定的特殊模板，如果没有，再走通用词性模板
            if word in SPECIAL_TEMPLATES:
                template = random.choice(SPECIAL_TEMPLATES[word])
            elif pos in templates:
                template = random.choice(templates[pos])
            else:
                template = random.choice(default_templates)
            
            # 生成句子并挖空
            sentence = template.format(词=word)
            blank_sentence = sentence.replace(word, "___")
            f.write("%s （目标词：%s，词性：%s）\n" % (blank_sentence, word, pos))

if __name__ == "__main__":
    words = load_words()
    lv4 = filter_by_level(words, "4")
    print("总词汇 %d 个，其中 HSK4 词汇 %d 个，词性分布：%s"
          % (len(words), len(lv4), count_by_pos(lv4)))
    gen_fill_in_the_blank(lv4)
    print("已生成填空题：%s" % OUTPUT)
