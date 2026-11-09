# 学科智能问答助手 v1.0 (14组 周家宏)

## 功能
基于RAG的学科问答助手，支持“纯对话”与“基于资料检索”两种模式。

## 怎么装
1. 运行 `pip install -r requirements.txt`
2. 运行 `ollama pull qwen2.5:0.5b`
3. 运行 `ollama pull nomic-embed-text`
4. 确保根目录有 `.env` 文件并填入 `DEEPSEEK_API_KEY`

## 怎么用
在终端运行 `python assistant_v1.py`，程序会自动跑通三问三答。

## 已知问题
未启动 Ollama 时，本地模式会报错。解决办法：启动 Ollama 或者将代码中的 prefer="local" 改为 prefer="api" 走云端。