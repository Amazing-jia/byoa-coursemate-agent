# Submission Answers

## Repo Link

https://github.com/Amazing-jia/byoa-coursemate-agent

## Q4 Answer, Chinese Version

我设计的 Agent 名为 **CourseMate Agent**，是一个面向课程学习场景的单一用途智能助手，主要用于读取本地课程资料并回答相关问题。该 Agent 的主要功能包括：读取本地 PPT/PDF/TXT 文件内容、根据用户问题检索关键词、将检索到的课程内容作为上下文发送给外部 API，并生成更自然的问答或摘要结果。

在工具（Skills）方面，我实现了多个核心工具：**read_local_file** 用于读取本地课程文件，**search_in_text** 用于从提取出的文本中检索相关内容，**answer_with_openai** 用于调用外部 OpenAI API 生成最终回答。项目还提供了一个基于 Python 内置 HTTP 服务的简单网页界面，方便用户输入问题并查看回答与检索上下文。

在上下文（context）集成方面，我采用了基于函数调用的工具集成方式。Agent 会先读取本地课程资料，再进行关键词检索，最后把检索到的真实课程内容作为外部上下文传入 API，从而实现基于课程材料的问答，而不是只依赖模型自身知识。

## Reflection

在开发过程中，我使用 AI 工具帮助生成项目初始代码，包括文件读取、关键词检索、API 调用和网页界面。之后我进一步修改代码结构，将本地资料检索逻辑和外部 API 问答逻辑分开，使命令行和网页页面可以共用同一个 Agent。这个过程让我意识到，AI 可以快速生成可运行原型，但仍需要人工明确任务边界、检查依赖配置、验证 API 调用和本地文件读取是否真正连通。

## Suggested Screenshots

1. Project file structure showing `agent.py`, `app.py`, `tools.py`, `prompts/system_prompt.txt`, and `data/Week 13-15.pptx`.
2. Terminal running `python app.py`.
3. Browser page at `http://127.0.0.1:5000`.
4. Web page answering a question such as `prompting` or `summarize the main content`.

## Simple Architecture

```text
User Question
    ↓
CourseMate Agent Web UI
    ↓
Tool 1: read_local_file
    ↓
Extracted course material text
    ↓
Tool 2: search_in_text
    ↓
Relevant local context
    ↓
External OpenAI API
    ↓
Final grounded answer
```
