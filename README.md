# CourseMate Agent

## Overview

CourseMate Agent is a single-purpose study assistant that helps users understand local course materials.

It reads local PPT/PDF/TXT files, searches for relevant keywords, and answers questions based on the extracted material.

## Main Functions

- Read local course materials from PPTX, PDF, and TXT files
- Search keywords in extracted course text
- Return relevant content for question answering
- Generate a short summary of the material

## Tools / Skills

1. `read_local_file`: reads local PPTX, PDF, or TXT course files
2. `search_in_text`: searches extracted text for keywords and returns relevant content
3. `summarize_text`: creates a concise preview summary from the local material

## Context Integration

This project uses function-based context integration. The agent calls local tools to read course files and retrieve relevant text, then uses that external context to answer user questions.

## Core Prompt

The core prompt is stored in:

```text
prompts/system_prompt.txt
```

## Project Structure

```text
byoa-coursemate-agent/
├── main.py
├── tools.py
├── requirements.txt
├── README.md
├── prompts/
│   └── system_prompt.txt
├── data/
│   └── Week 13-15.pptx
└── screenshots/
```

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the agent:

```bash
python main.py
```

Example questions:

```text
Experiment 2
prompting
summarize the main content
```

## Assignment Description

CourseMate Agent is designed for the BYOA experiment as a tool-using single-purpose agent. It integrates external course materials as context through local file reading and keyword retrieval.
