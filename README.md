<div align="center">

# Context Engineering

**A free, framework-agnostic series on engineering the entire input an LLM sees on every call.**

System prompt · tools · memory · retrieval · history · user instruction.

[![License: CC BY 4.0](https://img.shields.io/badge/Prose-CC--BY--4.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE)
[![Posts](https://img.shields.io/badge/posts-24-orange.svg)](#-the-series)
[![Status](https://img.shields.io/badge/status-in%20progress-yellow.svg)](PLAN.md)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Read the cheatsheet](CHEATSHEET.md) · [Glossary](GLOSSARY.md) · [References](REFERENCES.md) · [Plan](PLAN.md) · [Contribute](CONTRIBUTING.md)

</div>

---

## Why this exists

Most LLM applications fail not because the model is weak but because the **context** assembled around the user's question is wrong: the system prompt is too vague, the wrong chunks were retrieved, history has buried the rules, or the tools are described badly. *Context engineering* is the discipline of doing that assembly well — across all six layers — so that the model has the right information, in the right place, at the right cost.

This repository is the source for **24 posts**, every **diagram** (as editable SVG with a shared design-token system), every **code companion** (runnable), plus a one-page **cheatsheet** and a printable **reference-architecture poster**.

> No marketing voice. Neutral, textbook tone. Examples first, formalism second. Framework-agnostic.

---

## Quick start

**If you have one hour, read these three:**

1. [01 · Why context engineering](posts/01-why-context-engineering/index.md)
2. [02 · The six layers of context](posts/02-six-layers-of-context/index.md)
3. [06 · Write, select, compress, isolate](posts/06-write-select-compress-isolate/index.md)

**If you have ten minutes, read the [one-page cheatsheet](CHEATSHEET.md).**

**If you have ten seconds:**

> Every LLM call is a stack of six layers. Four operations — **W**rite, **S**elect, **C**ompress, **I**solate — let you engineer each layer. Five recurring **failure modes** explain almost every production bug. The rest of the series is depth on each.

---

## 📚 The series

### Part I — Foundations

| #  | Title | Folder |
|----|-------|--------|
| 01 | [Why context engineering — and why now](posts/01-why-context-engineering/index.md) | `01-why-context-engineering` |
| 02 | [The six layers of context](posts/02-six-layers-of-context/index.md) | `02-six-layers-of-context` |
| 03 | [How LLMs actually read context](posts/03-how-llms-read-context/index.md) | `03-how-llms-read-context` |
| 04 | [Tokens, windows, and budgets](posts/04-tokens-windows-budgets/index.md) | `04-tokens-windows-budgets` |
| 05 | [Five context failure modes](posts/05-context-failure-modes/index.md) | `05-context-failure-modes` |

### Part II — The four primitives (WSCI)

| #  | Title | Folder |
|----|-------|--------|
| 06 | [Write, select, compress, isolate](posts/06-write-select-compress-isolate/index.md) | `06-write-select-compress-isolate` |
| 07 | [Write strategies](posts/07-write-strategies/index.md) | `07-write-strategies` |
| 08 | [Select strategies](posts/08-select-strategies/index.md) | `08-select-strategies` |
| 09 | [RAG in depth](posts/09-rag-in-depth/index.md) | `09-rag-in-depth` |
| 10 | [Compress strategies](posts/10-compress-strategies/index.md) | `10-compress-strategies` |
| 11 | [Isolate strategies](posts/11-isolate-strategies/index.md) | `11-isolate-strategies` |

### Part III — The layers in depth

| #  | Title | Folder |
|----|-------|--------|
| 12 | [The system prompt as software](posts/12-system-prompt-as-software/index.md) | `12-system-prompt-as-software` |
| 13 | [Tools and MCP](posts/13-tools-and-mcp/index.md) | `13-tools-and-mcp` |
| 14 | [Memory systems](posts/14-memory-systems/index.md) | `14-memory-systems` |
| 15 | [Advanced retrieval](posts/15-advanced-retrieval/index.md) | `15-advanced-retrieval` |

### Part IV — Production concerns

| #  | Title | Folder |
|----|-------|--------|
| 16 | [Evaluation](posts/16-evaluation/index.md) | `16-evaluation` |
| 17 | [Observability, tracing, and cost](posts/17-observability/index.md) | `17-observability` |
| 18 | [Security and prompt injection](posts/18-security/index.md) | `18-security` |
| 19 | [Long context vs. RAG — a decision framework](posts/19-long-context-vs-rag/index.md) | `19-long-context-vs-rag` |

### Part V — Workflow & builds

| #  | Title | Folder |
|----|-------|--------|
| 20 | [The modern agentic workflow](posts/20-modern-agentic-workflow/index.md) | `20-modern-agentic-workflow` |
| 21 | [Remote agentic workflow](posts/21-remote-agentic-workflow/index.md) | `21-remote-agentic-workflow` |
| 22 | [Build #1 — RAG chatbot from scratch](posts/22-build-rag-chatbot/index.md) | `22-build-rag-chatbot` |
| 23 | [Build #2 — MCP server from scratch](posts/23-build-mcp-server/index.md) | `23-build-mcp-server` |
| 24 | [Capstone — Email reply agent](posts/24-capstone-email-reply-agent/index.md) | `24-capstone-email-reply-agent` |

---

## 🧰 Reference assets

| Asset | What it is |
|-------|-----------|
| [`CHEATSHEET.md`](CHEATSHEET.md) | Single printable page: six layers, WSCI, five failure modes, debug checklist. |
| [`GLOSSARY.md`](GLOSSARY.md) | Every term used in any post, alphabetised, one-line definitions. |
| [`REFERENCES.md`](REFERENCES.md) | Master bibliography for every citation in the series. |
| [`PLAN.md`](PLAN.md) | The master plan — thesis, sections, diagrams, and code per post. |
| [`assets/poster/`](assets/poster/) | A2 reference-architecture poster: every concept on one canvas. |

---

## 🗂 Repository layout

```
context-engineering/
├── README.md              ← you are here
├── PLAN.md                ← master plan (single source of truth)
├── GLOSSARY.md            ← one-line term definitions
├── CHEATSHEET.md          ← printable single page
├── REFERENCES.md          ← master bibliography
├── CONTRIBUTING.md        ← style guide and PR rules
├── LICENSE                ← CC-BY 4.0 (prose) + MIT (code)
│
├── posts/                 ← one folder per post
│   └── NN-kebab-slug/
│       ├── index.md       ← the post
│       ├── diagrams/      ← post-specific SVGs
│       └── snippets/      ← inline code shown in the post
│
├── code/                  ← runnable companions for builds
│   ├── 22-rag-chatbot/
│   ├── 23-mcp-server-full/
│   └── 24-email-reply-agent/
│
├── assets/
│   ├── diagrams/
│   │   └── exports/       ← rendered hero SVGs used by posts
│   ├── images/
│   ├── animations/
│   └── poster/            ← reference-architecture poster
```

**Naming rule.** `posts/NN-kebab-slug/`. `NN` is a stable two-digit number; the slug never changes after publishing (URL stability).

---

## 💻 Code companions

Runnable companions live under [`code/`](code/) and are MIT-licensed. They use plain Python and the official provider SDKs first; a framework appears only when it materially changes the shape of the code.

| Build | Code | Post |
|-------|------|------|
| RAG chatbot | [`code/22-rag-chatbot/`](code/22-rag-chatbot/) | [Post 22](posts/22-build-rag-chatbot/index.md) |
| MCP server (full) | [`code/23-mcp-server-full/`](code/23-mcp-server-full/) | [Post 23](posts/23-build-mcp-server/index.md) |
| Email reply agent | [`code/24-email-reply-agent/`](code/24-email-reply-agent/) | [Post 24](posts/24-capstone-email-reply-agent/index.md) |

Each code folder ships its own `README.md`, `pyproject.toml`, `.env.example`, and `tests/`.

---

## 🤝 Contributing

Typos, broken links, and clarity fixes are very welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for style conventions.

For larger changes — a new post, a new hero diagram, a new code companion — please **open an issue first** so we can align on scope before you spend time on a PR.

Found a factual error or an outdated benchmark? File an issue with a citation; that is the most valuable kind of contribution this series can receive.

---

## 📜 License

This repository is **dual-licensed**:

- **Prose, diagrams, illustrations, and hero images** — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Share and adapt freely with attribution.
- **Code** under [`code/`](code/) and [`tools/`](tools/) — [MIT](LICENSE).

See [LICENSE](LICENSE) for full terms and the required attribution line.

---

<div align="center">

⭐ **If you find this useful, star the repo so others can find it.** ⭐

</div>
