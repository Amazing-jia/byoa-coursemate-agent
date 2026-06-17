# Submission Answers

## Repo Link

https://github.com/Amazing-jia/byoa-coursemate-agent

## Q4 Answer, Chinese Version

我设计的 Agent 名为 **CourseMate Agent**，是一个面向课程学习场景的单一用途智能助手，主要用于读取用户上传的本地课程资料并回答相关问题。该 Agent 的主要功能包括：上传并读取 PPT/PDF/TXT 文件、根据用户问题检索关键词、将检索到的课程内容作为上下文发送给外部 AI API，并生成基于资料的问答或摘要结果。

在工具（Skills）方面，我实现了多个核心工具：**read_local_file** 用于读取用户上传的课程文件，**search_in_text** 用于从提取出的文本中检索相关内容，**answer_with_external_api** 用于调用外部 OpenAI-compatible API 生成最终回答。项目还提供了一个中文网页界面，用户可以在页面中输入 API Key、选择模型、填写 API Base URL，并上传自己电脑中的课程资料文件。

在上下文（context）集成方面，我采用了基于函数调用的工具集成方式。Agent 会先读取用户上传的课程资料，再进行关键词检索，最后把检索到的真实课程内容作为外部上下文传入 API，从而实现基于课程材料的问答，而不是只依赖模型自身知识。

## Reflection

在开发过程中，我使用 AI 工具帮助生成项目初始代码，包括文件读取、关键词检索、外部 API 调用和网页界面。之后我进一步修改代码结构，取消默认课程文件，要求用户在网页中上传自己的资料文件，使 Agent 的上下文来源更加明确。这个过程让我意识到，AI 可以快速生成可运行原型，但仍需要人工检查代码逻辑、依赖配置和用户操作流程，确保系统真正符合实验要求。

## Suggested Screenshots

1. 项目文件结构截图，能看到 `agent.py`、`app.py`、`tools.py`、`templates/index.html`、`prompts/system_prompt.txt`。
2. 终端运行 `python app.py` 的截图。
3. 中文网页截图，能看到上传文件、API Key、API Base URL 和模型设置。
4. 上传课程资料并提问后的回答截图，能看到 Agent 回答和检索到的课程上下文。

## Simple Architecture

```text
用户问题 + 用户上传的本地资料
    ↓
CourseMate Agent 中文网页
    ↓
工具 1：read_local_file
    ↓
提取课程资料文本
    ↓
工具 2：search_in_text
    ↓
相关本地上下文
    ↓
外部 OpenAI-compatible API
    ↓
最终回答
```
