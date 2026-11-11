# Mini AI Agent

A small agent in pure Python that shows the core loop behind Agentic AI:

```
goal -> THINK (pick a tool) -> ACT (run it) -> OBSERVE (read the result) -> remember
```

> This is a **rule-based** agent. It does not use an LLM or an API key, so it runs offline and is easy to understand. It is a foundation for learning how agents are built.

## What it can do
| Tool | Example |
|---|---|
| Calculator (safe, no `eval`) | `calculate 12 * (3 + 4)` |
| Unit converter | `convert 5 km to miles` |
| Notes (saved in a JSON file) | `note: finish my project` / `show my notes` |
| Clock | `what is the time` |

It can also do **multi-step goals**:
```
You: convert 100 c to f then calculate 2 + 2
Agent: 100 c = 212.0 f
Agent: 2 + 2 = 4
```
Type `tools` to see all tools and `memory` to see what the agent has done.

## Skills practiced
OOP (`Tool` and `Agent` classes), tool registry design, the agent loop, regex, safe expression parsing with `ast`, memory, JSON storage, error handling, `unittest`.

## Requirements
Python 3.8 or newer. No extra packages.

## Run it
```bash
python agent.py
```

## Run the tests
```bash
python -m unittest -v
```

## Project structure
```
mini-ai-agent/
├── agent.py        # Tool, Agent, and the main chat loop
├── test_agent.py   # unit tests
├── README.md
└── .gitignore
```

## Next steps (roadmap)
- [ ] Replace the rule-based `think()` with an LLM that picks the tool
- [ ] Add a web search tool
- [ ] Add long-term memory
- [ ] Add a simple web interface

## Author
Afan Nasr, BS Computer Science student
