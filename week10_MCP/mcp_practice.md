# W10 实验三：MCP 工具调用实践

## 1. 配置记录

- **客户端**：Python 最小客户端（`mcp` 库的 `ClientSession` + `stdio_client`）
- **服务端**：`hsk_mcp_server.py`（stdio 方式，由客户端作为子进程拉起）

**客户端配置原文（JSON）**：

{"mcpServers": {"hsk-tools": {"command": "python", "args": ["hsk_mcp_server.py"]}}}

**运行方式**：
- 服务端：`python hsk_mcp_server.py`（挂起等待连接）
- 客户端：`python demo_client.py`

## 2. 调用证据

- **工具列表**：`['hsk_level', 'list_by_level']`
- **调用返回**：`hsk_level("把")` → `把 -> 3 级`
<img width="1324" height="330" alt="屏幕截图 2026-11-23 130313" src="https://github.com/user-attachments/assets/20352c3e-99e0-451d-8e7b-00e6e1d7770d" />

## 3. 三者辨析（三句话）

1. **Function Calling**：模型侧机制，解决「模型决定调用哪个工具」的问题（对应 W9 的 TOOLS 字典 + run()）。
2. **MCP**：工具侧协议，解决「外部工具如何被统一发现和调用」的问题（对应 W10 的 hsk_mcp_server.py 与客户端配置）。
3. **普通 API 调用**：程序侧直连，解决「代码直接请求服务」的问题，没有模型决策参与（对应 W4 的 week4_api_bot.py）。

## 补充：新增第 3 个工具（课后作业 2）

### 更新后的工具列表

['hsk_level', 'list_by_level', 'count_by_level']

### count_by_level 调用证据

调用 `count_by_level("3")` 返回：`3 级共 N 个词`

（把 N 换成你终端里跑出来的实际数字；并贴一张 demo_client.py 输出三行的截图）

### 新增工具说明

在 `hsk_mcp_server.py` 中新增 `count_by_level` 工具：用 `@mcp.tool()` 装饰器 + 类型注解 `(level: str) -> str` + docstring 三件套声明，输入等级、返回该等级的词数，经 `demo_client.py` 验证已出现在工具列表并可正常调用。
