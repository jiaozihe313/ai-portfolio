# RAG 5行映射表对照

| 行 | 官方流水线 | llm-universe对应章节 | 我自己的代码 (`rag_qa.py` / `assistant_v1.py`) |
| :--- | :--- | :--- | :--- |
| 1 | Load + Split | C3「数据处理：读取、清洗与切片」 | 使用了 `TextLoader` 读取《等级标准节选.txt》，并用 `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50) 分块。 |
| 2 | Embed + Store | C3「搭建并使用向量数据库」 | 使用 `OllamaEmbeddings(model="nomic-embed-text")` 进行向量化，并用 `Chroma` 在本地持久化存储。 |
| 3 | Retrieve | C4「基于LangChain搭建检索问答链」 | 定义了 `retrieve()` 函数，使用 `as_retriever(search_kwargs={"k": 2})` 获取 top-2 相似片段。`use_rag=True` 时优先调用。 |
| 4 | Prompt + Generate | C4「将LLM接入LangChain」 | 用 `build_prompt()` 将 `SYSTEM_HINT` + 检索到的 `ctx` + `question` 拼接，最终交给 W6 写的 `LLM().ask(prefer=...)` 生成。 |
| 5 | Deploy + Evaluate | C4「Streamlit部署」；C5「系统评估」 | 目前在命令行终端运行；W7写的“幻觉对照表”是最基础的评估证据；W15将尝试用 Streamlit 发布。 |
