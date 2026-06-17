# Submission Answers

## Repo Link

https://github.com/Amazing-jia/byoa-coursemate-agent

## Q4 Answer, Chinese Version

我设计的 Agent 名为 **CourseMate Agent**，是一个面向课程学习场景的单一用途智能助手，主要用于读取本地课程资料并回答相关问题。该 Agent 的主要功能包括：读取本地 PPT/PDF/TXT 文件内容、根据用户问题检索关键词、基于课程资料生成简要总结与问答。

在工具（Skills）方面，我实现了两个核心工具：**read_local_file**，用于读取本地文件内容；**search_in_text**，用于在提取出的文本中进行关键词检索。同时，项目中还包含 **summarize_text**，用于生成课程资料的简短摘要。

在上下文（context）集成方面，我采用了基于函数调用的工具集成方式，将本地课程文件作为外部上下文输入给 Agent，使其回答不依赖模型自身知识，而是基于真实课程材料完成任务。

## Reflection

在开发过程中，我使用 AI 工具帮助生成项目初始代码，包括文件读取函数、关键词检索函数和主程序框架。之后我对代码进行了整理，使其能够读取本地 PPT/PDF/TXT 文件，并通过关键词检索返回与问题相关的课程内容。这个过程让我意识到，AI 可以显著提高开发效率，但仍需要人工明确任务边界、检查代码结构，并通过实际运行验证结果是否符合实验要求。

## Suggested Screenshots

1. Project file structure showing `main.py`, `tools.py`, `README.md`, `prompts/system_prompt.txt`, and `data/Week 13-15.pptx`.
2. Terminal running `python main.py`.
3. Agent answering a question such as `Experiment 2`.
4. Agent answering another keyword question such as `prompting`.

## Simple Architecture

```text
User Question
    ↓
CourseMate Agent
    ↓
Tool 1: read_local_file
    ↓
Extracted course material text
    ↓
Tool 2: search_in_text
    ↓
Relevant content
    ↓
Agent answer
```
