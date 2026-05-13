# Context Engineering — a free, public series

A practical, framework-agnostic series on **engineering the entire input** that an LLM sees on every call: system prompt, tools, memory, retrieved chunks, conversation history, and the user instruction.

This repository contains the source for all 24 posts, every diagram (as editable SVG), every code snippet (runnable), and a reference architecture poster you can pin to a wall.

> **Author:** Dr. Shrirat Panat (Vizuara)
> **License:** prose CC-BY 4.0 · code MIT
> **Status:** in progress — Part I shipping first

---

## How to read this series

You can read the posts in order, top to bottom, or jump to any individual post — each one stands alone and links forward and backward.

If you only have one hour, read these three:

1. [Post 01 — Why context engineering](posts/01-why-context-engineering/index.md)
2. [Post 02 — The six layers of context](posts/02-six-layers-of-context/index.md)
3. [Post 06 — The four primitives: Write, Select, Compress, Isolate](posts/06-write-select-compress-isolate/index.md)

If you only have ten minutes, read the [one-page cheatsheet](CHEATSHEET.md).

---

## The series

### Part I — Foundations

| #  | Title | Slug |
|----|-------|------|
| 01 | Why context engineering — and why now | [01-why-context-engineering](posts/01-why-context-engineering/index.md) |
| 02 | The six layers of context | [02-six-layers-of-context](posts/02-six-layers-of-context/index.md) |
| 03 | How LLMs actually read a prompt — attention, position, and "lost in the middle" | [03-how-llms-read-context](posts/03-how-llms-read-context/index.md) |
| 04 | Tokens, windows, and the three budgets that govern every call | [04-tokens-windows-budgets](posts/04-tokens-windows-budgets/index.md) |
| 05 | Failure modes — poisoning, distraction, confusion, clash, drift | [05-context-failure-modes](posts/05-context-failure-modes/index.md) |

### Part II — The four primitives (WSCI)

| #  | Title | Slug |
|----|-------|------|
| 06 | Write, Select, Compress, Isolate — a working vocabulary | [06-write-select-compress-isolate](posts/06-write-select-compress-isolate/index.md) |
| 07 | Write — scratchpads, plan files, and externalising state | [07-write-strategies](posts/07-write-strategies/index.md) |
| 08 | Select — choosing what enters the window on every turn | [08-select-strategies](posts/08-select-strategies/index.md) |
| 09 | Select in depth — RAG done well | [09-rag-in-depth](posts/09-rag-in-depth/index.md) |
| 10 | Compress — summarisation, pruning, and prompt-level compression | [10-compress-strategies](posts/10-compress-strategies/index.md) |
| 11 | Isolate — sub-agents, sandboxes, and parallel work | [11-isolate-strategies](posts/11-isolate-strategies/index.md) |

### Part III — The layers in depth

| #  | Title | Slug |
|----|-------|------|
| 12 | The system prompt as software — `CLAUDE.md`, `AGENTS.md`, and skills | [12-system-prompt-as-software](posts/12-system-prompt-as-software/index.md) |
| 13 | Tools, function calling, and the Model Context Protocol | [13-tools-and-mcp](posts/13-tools-and-mcp/index.md) |
| 14 | Memory systems — short-term, long-term, episodic, semantic, procedural | [14-memory-systems](posts/14-memory-systems/index.md) |
| 15 | Retrieval beyond vanilla RAG — agentic, graph, and hybrid patterns | [15-advanced-retrieval](posts/15-advanced-retrieval/index.md) |

### Part IV — Production concerns

| #  | Title | Slug |
|----|-------|------|
| 16 | Cost and latency — caching, batching, and the math of long contexts | [16-cost-and-latency](posts/16-cost-and-latency/index.md) |
| 17 | Observability — tracing, evals, and the feedback loop | [17-observability-and-evals](posts/17-observability-and-evals/index.md) |
| 18 | Security — prompt injection, exfiltration, and untrusted content | [18-security-and-injection](posts/18-security-and-injection/index.md) |
| 19 | Multi-agent systems — when to split, when not to | [19-multi-agent-systems](posts/19-multi-agent-systems/index.md) |

### Part V — Workflow & what to build

| #  | Title | Slug |
|----|-------|------|
| 20 | A day in the life — the context engineer's workflow | [20-the-workflow](posts/20-the-workflow/index.md) |
| 21 | Building a coding agent from scratch | [21-build-coding-agent](posts/21-build-coding-agent/index.md) |
| 22 | Building a research agent from scratch | [22-build-research-agent](posts/22-build-research-agent/index.md) |
| 23 | Building a customer-support agent from scratch | [23-build-support-agent](posts/23-build-support-agent/index.md) |
| 24 | Where context engineering goes next | [24-the-future](posts/24-the-future/index.md) |

---

## Reference assets

- [GLOSSARY.md](GLOSSARY.md) — every term, one line each.
- [CHEATSHEET.md](CHEATSHEET.md) — printable single page: layers, WSCI, failure modes, debug checklist.
- [REFERENCES.md](REFERENCES.md) — master bibliography for every citation in the series.
- [assets/poster/reference-architecture.svg](assets/poster/reference-architecture.svg) — A2 poster of every concept on one canvas.

---

## How the diagrams are made

Every diagram in this series is hand-edited SVG, drawn against a single design-token system that supports light and dark mode and is colour-blind safe. See [assets/diagrams/style/README.md](assets/diagrams/style/README.md) and the canonical hero diagrams under [assets/diagrams/exports/](assets/diagrams/exports/).

You are welcome to copy, remix, or translate them under CC-BY 4.0 — please keep the attribution line.

---

## Contributing

Typos, broken links, and clarity fixes are very welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). For larger changes (new posts, new diagrams) please open an issue first.

---

## Why free?

These ideas are how careful people are building real systems on top of LLMs in 2025–2026. They should not sit behind a paywall. If this series helps you, the best thank-you is to share it with one other person who is trying to build something with these tools.
