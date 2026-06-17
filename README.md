# CourseMate Agent

## Overview

CourseMate Agent is a single-purpose study assistant for local course materials.

It reads a local PPT/PDF/TXT file, retrieves relevant course context, and calls an external OpenAI-compatible AI API to generate a grounded answer. It also provides a Chinese web interface where users can enter an API key, choose a model, and upload their own local course file.

## Main Functions

- Read local course materials from PPTX, PDF, and TXT files
- Upload a course file from the user's computer through the web page
- Search keywords in extracted course text
- Send retrieved context to an external AI API for answer generation
- Support OpenAI-compatible API providers through custom Base URL and model name
- Provide a Chinese browser interface

## Tools / Skills

1. `read_local_file`: reads local PPTX, PDF, or TXT course files
2. `search_in_text`: searches extracted text for keywords and returns relevant context
3. `answer_with_external_api`: calls an external OpenAI-compatible chat completions API

## Context Integration

This project uses function-based context integration. The agent first calls local tools to read and retrieve course content, then passes the retrieved context to an external AI API. This makes the answer depend on the local course material instead of only the model's general knowledge.

## Core Prompt

The core prompt is stored in:

```text
prompts/system_prompt.txt
```

## Project Structure

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
├── data/
│   └── Week 13-15.pptx
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── screenshots/
```

## Setup

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

If `python` is not available on this computer, use the bundled Codex Python path shown by the local environment.

## Run Web Page

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The web page uses Python's built-in HTTP server, so no web framework is required.

## API Settings

The web page supports OpenAI-compatible `/chat/completions` APIs. Enter the API key directly on the page.

Common examples:

```text
OpenAI
Base URL: https://api.openai.com/v1
Model: gpt-4.1-mini

DeepSeek
Base URL: https://api.deepseek.com/v1
Model: deepseek-chat

DashScope / Qwen
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
Model: qwen-plus

Moonshot / Kimi
Base URL: https://api.moonshot.cn/v1
Model: moonshot-v1-8k

Zhipu GLM
Base URL: https://open.bigmodel.cn/api/paas/v4
Model: glm-4-flash
```

You can also create a `.env` file from `.env.example`, but it is optional because the page allows entering the API key directly.

## Example Questions

```text
总结这份课件的主要内容
prompting 技术有哪些？
zero-shot 和 k-shot prompting 有什么区别？
```

## Assignment Description

CourseMate Agent is designed for the BYOA experiment as a tool-using single-purpose agent. It integrates local course material as external context and uses an external AI API for final answer generation.
