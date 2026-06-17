# CourseMate Agent：本地课程资料学习助手

## 项目简介

CourseMate Agent 是一个面向课程学习场景的单一用途 Agent。用户在网页中上传自己电脑里的课程资料文件，然后输入问题。系统会先读取并检索上传文件中的内容，再把检索到的上下文发送给外部 AI API，生成基于资料的回答。

本项目默认不内置课程资料文件，也不会自动调用任何默认文件。每次使用时都需要由用户上传 PPTX、PDF 或 TXT 文件。网页支持一次上传多个文件，并会在回答下方显示与当前问题最接近的一段原文片段，而不是展示完整课程原文。

## 主要功能

- 上传一个或多个本机课程资料文件
- 支持读取 `.pptx`、`.pdf`、`.txt`
- 根据用户问题进行混合检索，匹配中文问题、英文资料和常见课程术语
- 显示与问题最接近的原文片段，避免暴露整份资料
- API Key 输入框使用密码模式，并在提交后自动清空
- 支持关闭外部 AI，只查看本地检索结果
- 支持通过 OpenAI-compatible API 调用多个 AI 平台
- 提供中文网页界面

## 工具 / Skills

1. `read_local_file`：读取用户上传的 PPTX、PDF 或 TXT 文件
2. `rank_passages`：对提取出的文本片段进行关键词、同义词和模糊匹配排序
3. `answer_with_external_api`：调用外部 OpenAI-compatible API 生成最终回答

## Context 集成方式

本项目采用基于函数调用的上下文集成方式。Agent 会先调用本地文件读取工具提取课程资料文本，再用混合检索方法找到和问题相关的片段，最后把检索结果作为外部上下文传入 AI API。

当用户上传多个文件时，Agent 会依次读取每个文件，将文件切分为 slide/page/段落片段，再根据用户问题进行排序。检索会结合关键词、中文到英文课程术语映射、模糊匹配；如果用户提供了 API Key，还会用外部 AI 对候选片段做一次轻量重排。页面只展示最相关原文片段，用于证明回答来源，同时避免显示过长的完整资料。

## 核心 Prompt

核心 prompt 存放在：

```text
prompts/system_prompt.txt
```

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 启动网页

```bash
python app.py
```

然后在浏览器打开：

```text
http://127.0.0.1:5000
```

## 使用步骤

1. 打开网页。
2. 上传一个或多个 `.pptx`、`.pdf`、`.txt` 课程资料文件。
3. 输入问题。
4. 在右侧填写 API Key、API Base URL 和模型名称。
5. 点击“开始回答”。
6. 页面会显示 Agent 回答、检索到的课程上下文，以及最相关原文片段。

如果只想测试本地读取和检索功能，可以取消勾选“调用外部 AI”。

## API 设置示例

```text
OpenAI
Base URL: https://api.openai.com/v1
Model: gpt-4.1-mini

DeepSeek
Base URL: https://api.deepseek.com/v1
Model: deepseek-chat

通义千问 DashScope
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
Model: qwen-plus

Kimi / Moonshot
Base URL: https://api.moonshot.cn/v1
Model: moonshot-v1-8k

智谱 GLM
Base URL: https://open.bigmodel.cn/api/paas/v4
Model: glm-4-flash
```

## 示例问题

```text
总结这些资料的主要内容
prompting 技术有哪些？
zero-shot 和 k-shot prompting 有什么区别？
比较这几个文件中的重点内容
```

## 实验说明

CourseMate Agent 符合 BYOA 实验中 single-purpose agent 的要求。它使用了多个工具/skills，包括本地文件读取、关键词检索和外部 API 调用，并通过上传文件实现外部上下文集成。
