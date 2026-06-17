# CourseMate Agent：本地课程资料学习助手

## 项目简介

CourseMate Agent 是一个面向课程学习场景的单一用途 Agent。用户需要在网页中上传自己电脑里的课程资料文件，然后输入问题。系统会先读取并检索上传文件中的内容，再把检索到的上下文发送给外部 AI API，生成基于资料的回答。

本项目默认不内置课程资料文件，也不会自动调用任何默认文件。每次使用时都需要由用户上传 PPTX、PDF 或 TXT 文件。网页支持一次上传多个文件，并会在回答下方显示本次调用文件的原文内容。对于 PPT/PDF，页面显示的是程序提取出的文本。

## 主要功能

- 上传一个或多个本机课程资料文件
- 支持读取 `.pptx`、`.pdf`、`.txt`
- 根据用户问题检索资料中的相关内容
- 显示 Agent 本次调用的文件原文
- 支持关闭外部 AI，只查看本地检索结果
- 支持通过 OpenAI-compatible API 调用多个 AI 平台
- 提供中文网页界面

## 工具 / Skills

1. `read_local_file`：读取用户上传的 PPTX、PDF 或 TXT 文件
2. `search_in_text`：在提取出的文本中进行关键词检索
3. `answer_with_external_api`：调用外部 OpenAI-compatible API 生成最终回答

## Context 集成方式

本项目采用基于函数调用的上下文集成方式。Agent 不直接依赖模型自身知识回答问题，而是先调用本地文件读取工具提取课程资料文本，再调用检索工具找到和问题相关的内容，最后把检索结果作为外部上下文传入 AI API。

当用户上传多个文件时，Agent 会依次读取每个文件，将文件名和提取出的原文合并成可检索上下文，并在网页中展示本次调用文件的原文，方便验证回答来源。

## 核心 Prompt

核心 prompt 存放在：

```text
prompts/system_prompt.txt
```

## 项目结构

```text
byoa-coursemate-agent/
├── agent.py
├── app.py
├── main.py
├── tools.py
├── requirements.txt
├── README.md
├── prompts/
│   └── system_prompt.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── screenshots/
```

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

如果本机 `python` 命令不可用，可以使用 Codex 环境中的 Python 路径运行。

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
3. 输入问题，例如“总结这些资料的主要内容”。
4. 在右侧填写 API Key、API Base URL 和模型名称。
5. 点击“开始回答”。
6. 查看 Agent 回答、检索到的课程上下文，以及本次调用文件原文。

如果只想测试本地读取和检索功能，可以取消勾选“调用外部 AI”。

## API 设置示例

本项目使用 OpenAI-compatible `/chat/completions` 接口。常见填写方式如下：

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
