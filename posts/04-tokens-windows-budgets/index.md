# 04 · Tokens, windows, and budgets

> **TL;DR.** A token is the smallest unit a language model bills, attends to, and forgets. Three numbers govern every design decision in this series: the **context window** (how many tokens the model will accept), the **token budget** (how many you choose to spend), and the **latency–cost–quality triangle** (which two you optimise for at the expense of the third). This post defines all three precisely and walks through the arithmetic that lets you size an agent on the back of an envelope before a single line of code is written.
>
> **Reading time:** ~13 minutes.
>
> **After reading this you will be able to:**
> - Estimate the token cost and latency of any prompt without running it.
> - Decide between a smaller model on a longer prompt and a larger model on a shorter one.
> - Set a defensible token budget for each layer of your agent.

![Token, window, and budget at a glance](./diagrams/00-hero-token-window-budget.svg)
*The token is the unit, the window is the ceiling, and the budget is the smaller share you actually spend.*

---

## 1. What a token is, exactly

A token is the unit your provider's tokeniser produces when it splits the input string. Modern frontier models almost all use a **byte-pair encoding** (BPE) variant: a deterministic, reversible algorithm that learns a vocabulary of 50 000 to 200 000 sub-word units from a large training corpus. Common words become a single token; rare words and unfamiliar names get split into multiple. Whitespace is part of the token. Code, JSON, URLs, and non-English scripts tokenise much worse than running prose.

The famous rule of thumb is that **one token is roughly three quarters of an English word**, equivalently, 100 tokens is about 75 words, or roughly half a paragraph. The rule is good enough for budgeting and dangerously off for billing. The same string can produce noticeably different token counts across providers:

| String | GPT-4o (cl100k) | Claude 3.5 | Gemini 1.5 |
|---|---|---|---|
| `"context engineering"` | 2 | 3 | 2 |
| `"def parse_iso8601(s: str) -> datetime:"` | 12 | 14 | 13 |
| One page of English prose (≈300 words) | ~400 | ~410 | ~395 |
| One page of Python code | ~520 | ~570 | ~530 |
| One page of densely-nested JSON | ~700 | ~780 | ~720 |

Three operational consequences fall out of this:

1. **Code and structured data are 30–80 % more expensive per page than prose.** A 50-page PDF of well-formatted English may fit in a 32 k window; the same 50 pages dumped as JSON often will not.
2. **Non-English text is more expensive still.** Many tokenisers split CJK characters, Arabic, and Indic scripts at one token per character or worse. A bilingual support agent that bills the same per turn for English and Hindi customers is silently subsidising the latter.
3. **Counting words is not counting cost.** Always run the actual tokeniser (`tiktoken`, Anthropic's `count_tokens`, Vertex's `count_tokens`) before quoting numbers to anyone with a budget.

---

## 2. The context window

The **context window** is the maximum number of tokens, input *plus* output, that the model will accept in a single call. It is a hard architectural limit: pass a single token over and the API returns an error.

A short, freshly-curated table of where the frontier sits:

| Model family | Window (tokens) | Approx. pages of prose | Notes |
|---|---|---|---|
| GPT-4o / 4.1 | 128 k | ~300 | Most ChatGPT-class deployments |
| Claude 3.5 / 3.7 / 4 | 200 k | ~500 | Default for Claude API and Claude Code |
| Claude 3 Opus *(extended)* | 1 M | ~2 500 | Limited rollout, premium pricing |
| Gemini 1.5 Pro | 1 M | ~2 500 | First broadly-available 1 M model |
| Gemini 1.5 / 2.5 *(extended)* | 2 M | ~5 000 | Enterprise tier |
| Llama 3.1 / 3.3 70B | 128 k | ~300 | Open-weight baseline |
| GPT-4o-mini, Haiku | 128–200 k | ~300–500 | Cheap-tier defaults |

Two warnings before anyone gets excited.

First, **the window is a ceiling, not a target.** Quality degrades long before the ceiling, for the reasons covered in [Post 03](../03-how-llms-read-context/index.md): positional encodings extrapolate, attention dilutes, the middle gets lost. A safe operational range is the lower 25–50 % of the advertised window for a frontier model and the lower 10–20 % for an open-weight one.

Second, **input plus output share the window.** A 200 k Claude call configured to return a 16 k response leaves you 184 k for the prompt, not 200 k. Forget this and your long-context agent will silently start truncating its own answers.

---

## 3. The three budgets

Every LLM call is constrained by three independent budgets. Engineering for one without thinking about the other two is the most common failure mode in early production deployments.

**The token budget** is the one engineers think of first. It is the number of *input* tokens you choose to spend per call. It is bounded above by the context window and, more often, by your patience for cost. A reasonable default for an interactive assistant is 8–16 k input tokens; for a background agent that runs for an hour, 50–100 k is normal; for batch document analysis, 200 k is the working range.

**The cost budget** is what each token costs you in dollars. Modern frontier pricing for *input* tokens spans roughly two orders of magnitude:

| Tier | Example model | $ / 1 M input | $ / 1 M output | Cached input |
|---|---|---|---|---|
| Frontier | GPT-4.1, Claude Opus 4 | $3.00–$15.00 | $15.00–$75.00 | ~10 % of input |
| Mid | Claude Sonnet 3.5, GPT-4o | $1.50–$3.00 | $7.50–$15.00 | ~10 % of input |
| Cheap | GPT-4o-mini, Haiku 3.5, Gemini Flash | $0.15–$0.50 | $0.60–$2.00 | ~10 % of input |

Pricing changes monthly; treat the table as orders of magnitude. The decisive ratio is not the absolute number but the ten-to-one gap between the cheap tier and the frontier tier, and the further ten-to-one gap that prefix caching opens up *within* a tier.

**The latency budget** is how long the user (or upstream service) will wait. It decomposes into two terms that compose differently than people expect:

$$
T_{\text{total}} = T_{\text{prefill}} + N_{\text{out}} \cdot T_{\text{decode}}
$$

*Prefill* is the time to ingest the prompt, roughly linear in input length. *Decode* is the per-token generation time, roughly constant per output token at a given model size. Order-of-magnitude figures in late 2025:

| Model class | Prefill | Decode | 8 k-in / 800-out wall time |
|---|---|---|---|
| Cheap (Haiku, Flash, mini) | ~1 ms / token | ~10 ms / token | ~10 s |
| Mid (Sonnet, GPT-4o) | ~2 ms / token | ~20 ms / token | ~30 s |
| Frontier (Opus, GPT-4.1) | ~3 ms / token | ~40 ms / token | ~60 s |

The numbers move every quarter, but the shape is durable. Two consequences: shrinking the *prompt* helps latency on long inputs; shrinking the *output* helps latency on short ones. Streaming hides decode time but not prefill time, which is why a long-context agent feels sluggish to first token even with streaming on.

---

## 4. The triangle

The three budgets pull against each other. You pick any two and the third goes wherever it must.

- **Cheap and fast** ⇒ accept lower quality. Use a Haiku/Flash/mini-tier model on a small prompt. Good for high-throughput auto-classification, intent detection, simple extraction.
- **Cheap and high-quality** ⇒ accept slow. Use a frontier model with prompt caching, batch endpoints, or off-peak processing. Good for nightly analytics jobs.
- **Fast and high-quality** ⇒ accept expensive. Use a frontier model on a focused prompt with reserved-capacity hosting and cache hits. Good for the user-facing critical path of a paid product.

![The cost-latency-quality triangle](./diagrams/01-budget-triangle.svg)

There is no fourth corner. The marketing material that promises all three is selling either the cheapest tier with the smallest prompt (calling it "fast and high-quality" relative to the previous generation of cheap models), or a benchmark configuration that nobody actually runs in production.

The practical mental model: choose the corner you are optimising for *per workflow*, not per company. A coding agent's "explain this stack trace" call lives in the fast-and-high-quality corner; its "summarise the last 200 turns" maintenance call lives in the cheap-and-high-quality corner. Different models, different prompts, same product.

---

## 5. Sizing an agent on an envelope

The arithmetic that follows is the back-of-envelope every team eventually does, written out once.

Suppose you are building a customer-support agent with the following per-turn shape:

| Layer | Tokens per call |
|---|---|
| System prompt + format + rules | 3 000 |
| Tool / MCP schemas (8 tools) | 1 600 |
| Memory (user profile + 5 prior tickets summarised) | 1 200 |
| RAG (top-5 chunks of 500 tokens each) | 2 500 |
| Conversation history (compressed) | 2 000 |
| User message | 200 |
| **Input total** | **10 500** |
| Output (typical reply) | 400 |

A single call on a mid-tier model at $2.50 / M input + $10 / M output:

$$
\text{Cost} = \frac{10\,500}{10^6} \times \$2.50 + \frac{400}{10^6} \times \$10.00 \approx \$0.0303
$$

Three cents. Now suppose 10 000 conversations a day, 4 turns per conversation, 5 of those calls per turn (sub-agents, tool replies):

$$
10\,000 \times 4 \times 5 \times \$0.0303 \approx \$6\,000\text{ / day}
$$

Six thousand dollars a day, $180 000 a month, before infrastructure. This is the calculation that turns "we will just call the API" into a real engineering project.

Now turn on prefix caching. The first 4 600 tokens (system prompt + tools) are byte-identical across all 200 000 calls in the day's trailing five-minute window. They cost ~10 % of full price:

$$
\text{Cost}_{\text{cached prefix}} = \frac{4\,600}{10^6} \times \$0.25 + \frac{5\,900}{10^6} \times \$2.50 + \frac{400}{10^6} \times \$10.00 \approx \$0.0193
$$

That single architectural choice, having a stable prefix and putting it at the front, drops the daily bill from $6 000 to about $3 900. A 35 % saving for an afternoon's work.

Finally, route the simpler 60 % of turns (FAQ-shaped questions) to a cheap-tier model at $0.30 / M / $1.20 / M. The blended cost drops to roughly $1 800 / day. The system is now four times cheaper than the naive baseline, with no measurable change in user-facing quality. **This is what context engineering pays for.**

---

## 6. Setting per-layer budgets

The arithmetic above only works if each layer of your context has a budget you actually enforce. A useful starting allocation, treating the *input* token budget as 100 %:

| Layer | Default share | Why |
|---|---|---|
| System prompt | 5–15 % | Must be small enough to keep the cached prefix *cacheable* |
| Tools / MCP | 5–15 % | RAG over tool schemas (Post 13) when this exceeds 15 % |
| Memory | 5–10 % | Compress aggressively; episodic memory should not grow unbounded |
| RAG | 20–40 % | The biggest variable lever; tune retrieval `k` to the budget, not the other way round |
| History | 10–30 % | Summarise on a schedule (Post 10), not at the limit |
| User turn | 1–5 % | Almost always the smallest, despite being the reason for the call |
| **Output reserve** | 10–20 % of *window* | Cap with `max_tokens`; never trust the model to be brief |

![Per-layer token budget allocation](./diagrams/02-per-layer-budget.svg)

These percentages are starting points, not laws. The discipline that matters is *having* explicit numbers per layer. Without them, the layer that grows fastest (almost always RAG or history) silently consumes everyone else's allocation.

---

## 7. Picking a model: a one-page decision

The five questions below cover almost every model-selection conversation in practice. Walk them in order; the first that gives you a strong answer wins.

1. **Does the task need state-of-the-art reasoning?** (Multi-step planning, code synthesis, hard math, novel domain.) → Frontier tier.
2. **Is the task a short, well-defined extraction or classification?** → Cheap tier; you will not measure the difference.
3. **Is the input long but the task simple?** (Summarise a 200-page report.) → Cheap tier with a long-context model: Gemini Flash, Haiku.
4. **Is the input short but the task hard?** (Architect a refactor.) → Frontier tier with a small prompt; you are paying for thinking, not reading.
5. **Is the task user-facing and time-critical?** → Mid tier with streaming, plus an explicit per-call latency budget that triggers fallback to a cheaper model on timeout.

Two patterns recur often enough to deserve their own names. **Cascade**: try the cheap model first, escalate to the frontier model only when an upstream eval (Post 16) flags the cheap answer. **Plan-and-execute**: a frontier model writes the plan once; cheap models execute the steps. Both shrink the average cost per task without sacrificing tail quality.

---

## Common pitfalls

- **Quoting word counts to engineers and token counts to product**, getting the conversion wrong, and discovering at month's end that the bill is 40 % higher than the forecast.
- **Sizing the prompt at the window ceiling.** A 200 k call costs the same whether the model uses the last 100 k or not. The lower half of the window is almost always wasted spend.
- **Forgetting the output reserve.** `max_tokens` is the one parameter teams routinely leave at the API default and then are surprised when long answers truncate mid-sentence.
- **Treating tool schemas as free.** Eight modest tools is 1–2 k of cached prefix on every call, forever. Worth keeping as long as they are used; worth auditing every quarter.
- **Optimising the wrong corner of the triangle.** Most user-facing chatbots over-spend on quality and under-spend on latency. Most internal batch jobs do the opposite.
- **No per-layer budget at all.** RAG and history will eat the system whole if nobody is watching.

---

## Further reading

- OpenAI, *"Tokenizer"* (interactive) and the `tiktoken` library: the canonical reference for the cl100k family.
- Anthropic Engineering, *"Counting tokens"* and *"Prompt caching with Claude"*: definitive numbers for the Claude family.
- Google, *"Gemini long-context tips"*: best practice for the 1 M / 2 M tier.
- Sennrich, R. *et al.*, *"Neural Machine Translation of Rare Words with Subword Units"* (2016): the original BPE paper.
- Patel, P. & Dean, J., *"Efficiently Scaling Transformer Inference"* (2023): prefill/decode mechanics that drive the latency model in §3.

Full citations in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 05 — Five context failure modes](../05-context-failure-modes/index.md)**: the symptoms that appear when a budget is wrong.
- **[Post 19 — Long context vs RAG](../19-long-context-vs-rag/index.md)**: the full version of the envelope arithmetic above, applied to the routing decision.
- **[Post 10 — Compress strategies](../10-compress-strategies/index.md)**: what to do when the history or RAG layer breaks its budget.
