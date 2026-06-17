# CourseMate Agent

## Overview

CourseMate Agent is a single-purpose study assistant for local course materials.

It reads a local PPT/PDF/TXT file, retrieves relevant course context, and uses an external OpenAI API call to generate a grounded answer. It also includes a simple web page for asking questions.

## Main Functions

- Read local course materials from PPTX, PDF, and TXT files
- Search keywords in extracted course text
- Send retrieved context to an external API for answer generation
- Generate a short summary of the material
- Provide a simple browser interface

## Tools / Skills

1. `read_local_file`: reads local PPTX, PDF, or TXT course files
2. `search_in_text`: searches extracted text for keywords and returns relevant context
3. `answer_with_openai`: calls the external OpenAI API to generate a final answer

## Context Integration

This project uses function-based context integration. The agent first calls local tools to read and retrieve course content, then passes the retrieved context to the OpenAI API. This makes the answer depend on the local course material instead of only the model's general knowledge.

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

Create a `.env` file from `.env.example`:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## Run in Terminal

```bash
python main.py
```

## Run Web Page

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The web page uses Python's built-in HTTP server, so no web framework is required.

Example questions:

```text
prompting
summarize the main content
What are zero-shot and k-shot prompting?
```

## Assignment Description

CourseMate Agent is designed for the BYOA experiment as a tool-using single-purpose agent. It integrates local course material as external context and uses an external API for final answer generation.
