# AI辅助编程实录

## 1. 任务与提示词
**任务**：读生词表CSV -> 筛HSK4 -> 生成填空题（把目标词挖空成 ___）。
**我的提示词**：让AI在现有的 vocab_tool.py 脚本里扩展一个生成填空题的功能。要求提供多种模板，随机选择以丰富句子，并且能兼容不同词性。

## 2. AI初版代码
```python
# AI生成的初版 vocab_tool.py
import os
import csv
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

DATA = weekpath.data_path("生词表.csv")

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
    out = out or weekpath.root_path("练习.txt")
    
    templates = {
        "动词": "我每天都坚持{词}，所以进步很快。",
        "名词": "这个{词}很重要，我们要好好理解。",
        "成语": "他做事有{词}，从不轻易放弃。",
        "介词": "请把{词}放在桌子上。",
        "动词短语": "他们正在{词}，非常辛苦。",
        "名词短语": "这{词}表示时间的变化。",
    }
    
    default_template = "请用“{词}”造一个句子。"
    
    with open(out, "w", encoding="utf-8") as f:
        for w in words:
            word = w["词汇"]
            pos = w["词性"]
            
            template = templates.get(pos, default_template)
            
            if template == default_template:
                f.write("用“%s”造一个句子。（%s）\n" % (word, pos))
            else:
                sentence = template.format(词=word)
                blank_sentence = sentence.replace(word, "___")
                f.write("%s （目标词：%s）\n" % (blank_sentence, word))
                

if __name__ == "__main__":
    words = load_words()
    lv4 = filter_by_level(words, "4")
    print("总词汇 %d 个，其中 HSK4 词汇 %d 个，词性分布：%s"
          % (len(words), len(lv4), count_by_pos(lv4)))
    
    out = weekpath.root_path("练习.txt")
    gen_fill_in_the_blank(lv4, out)
    print("已生成填空题：%s" % out)
```
## 3. 我的修改点（≥3条，每条写清“为什么”）

① **替换路径依赖：去掉了 `weekpath` 模块，改用 `os.path` 自动定位。**
   - **为什么**：AI初版代码依赖老师项目的 `weekpath` 模块，我复制到桌面上单独运行时直接报错 `ModuleNotFoundError`。改成 `os.path.dirname(os.path.abspath(__file__))` 后，代码能自动找到同文件夹下的 `生词表.csv`。

② **优化文件读写安全：加上 `encoding="utf-8"`。**
   - **为什么**：解决读写包含中文的CSV和TXT文件时出现乱码的问题。

③ **提升句子多样性：将单一模板改为“列表+随机选择”。**
   - **为什么**：AI初版只给每个词性分配了一个模板，导致所有动词生成的句子一模一样（全是用“坚持”造句）。我改成了模板列表，并用 `random.choice()` 随机挑选，让练习更丰富。

④ **修复基本搭配逻辑：修改了动词的模板。**
   - **为什么**：AI给的动词模板是“不要着急{词}”，导致生成“不要着急感动”这种明显的病句。我把句式改成了“关于{词}的故事”，使大多数动词都能套用。

⑤ **解决AI语义盲区：建立 `SPECIAL_TEMPLATES` 特殊词汇库。**
   - **为什么**：AI完全无法区分“动作动词（商量）”、“心理动词（感动）”和“语法点（把字句）”，导致出现“讨论感动的问题”这种荒谬的填空。我人工设立了特殊词库，为“把字句”和“感动”量身定制了专属句子，彻底修复了逻辑漏洞。

## 4. 最终版 vs 初版差异说明

通过这次“AI结对编程”，我深刻体会到：**AI极其擅长搭建代码骨架（如读文件、条件判断、循环），但它在处理具体的语义搭配时是“盲目”的。** AI只认“词性”，不懂“词义”。
最终的成品之所以能直接用于教学，是因为人工介入了两次关键的纠偏：一次是把模板抽象化以兼容更多动词，第二次是直接给特殊词汇“开小灶”编写专属模板。这证明了在AI辅助编程中，人类的常识和逻辑判断是不可替代的最后一道防线。
