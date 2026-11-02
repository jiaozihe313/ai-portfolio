# 第8周“学科智能问答助手 v1.0”阶段项目规划

## 一、项目目录结构规划
```text
Project_Assistant_v1/
├── core/
│   ├── llm.py          # 核心双引擎（本地Ollama + 云端API，带自动回退）
│   └── rag_qa.py       # RAG核心逻辑（加载、分块、向量化、检索、生成）
├── data/
│   └── 等级标准节选.txt  # 学科知识库源文件
├── chroma_db/          # 自动生成的本地向量数据库
├── main.py             # 主程序入口（接收用户输入，调用RAG，打印带出处的答案）
└── requirements.txt    # 依赖包清单
