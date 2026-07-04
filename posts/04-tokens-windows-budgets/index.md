# 04 · Tokens, windows, and budgets

> **TL;DR.** A token is the smallest unit a language model bills, attends to, and forgets. Three numbers govern every design decision in this series: the **context window** (how many tokens the model will accept), the **token budget** (how many you choose to spend), and the **latency–cost–quality triangle** (which two you optimise for at the expense of the third). This post defines all three precisely and walks through the arithmetic that lets you size an agent on the back of an envelope before a single line of code is written.
>
> **After reading this you will be able to:**
> - Estimate the token cost and latency of any prompt without running it.
> - Decide between a smaller model on a longer prompt and a larger model on a shorter one.
> - Set a defensible token budget for each layer of your agent.

![Token, window, and budget at a glance](./diagrams/00-hero-token-window-budget.svg)
*The token is the unit, the window is the ceiling, and the budget is the smaller share you actually spend.*

---

## 1. What a token is, exactly

A token is the unit your provider's tokeniser produces when it splits the input string. Modern frontier models almost all use a **byte-pair encoding** (BPE) variant: a deterministic, reversible algorithm that learns a vocabulary of sub-word units from a large training corpus (Sennrich et al., 2016). Production tokenisers land in the range of roughly 50,000 to 200,000 units, for example OpenAI's `cl100k` vocabulary is about 100,000 tokens (OpenAI, "Tokenizer"). Common words become a single token; rare words and unfamiliar names get split into multiple. Whitespace is part of the token. Code, JSON, URLs, and non-English scripts tokenise much worse than running prose.

The famous rule of thumb is that **one token is roughly three quarters of an English word**, equivalently, 100 tokens is about 75 words, or roughly half a paragraph (OpenAI, "Tokenizer"). The rule is good enough for budgeting and dangerously off for billing. The same string can produce noticeably different token counts across providers. The counts below are illustrative and provider-dependent; the point is the spread, not the exact digits (run the actual tokeniser to get real numbers):

| String | Frontier GPT (cl100k) | Claude | Gemini |
|---|---|---|---|
| `"context engineering"` | 2 | 3 | 2 |
| `"def parse_iso8601(s: str) -> datetime:"` | 12 | 14 | 13 |
| One page of English prose (≈300 words) | ~400 | ~410 | ~395 |
| One page of Python code | ~520 | ~570 | ~530 |
| One page of densely-nested JSON | ~700 | ~780 | ~720 |

Three operational consequences fall out of this:

1. **Code and structured data are, as a rule of thumb, tens of per cent more expensive per page than prose** (illustratively, on the order of 30–80 %). A 50-page PDF of well-formatted English may fit in a 32 k window; the same 50 pages dumped as JSON often will not.
2. **Non-English text is more expensive still.** Many tokenisers split CJK characters, Arabic, and Indic scripts at one token per character or worse. A bilingual support agent that bills the same per turn for English and Hindi customers is silently subsidising the latter.
3. **Counting words is not counting cost.** Always run the actual tokeniser (`tiktoken` for OpenAI, Anthropic's token-counting endpoint, Vertex's `count_tokens` for Gemini) before quoting numbers to anyone with a budget (OpenAI, "Tokenizer"; Anthropic, "Token counting").

---

## 2. The context window

The **context window** is the maximum number of tokens, input *plus* output, that the model will accept in a single call. It is a hard architectural limit: pass a single token over and the API returns an error.

A short table of where the frontier sits as of early 2026. Window sizes are the vendors' published figures (Anthropic, "Token counting"; Google, "Long context"); they change often, so confirm against the provider's docs:

| Model family | Window (tokens) | Approx. pages of prose | Notes |
|---|---|---|---|
| A frontier GPT model | 128 k+ | ~300+ | Most ChatGPT-class deployments |
| Claude Haiku 4.5 | 200 k | ~500 | Cheap/fast tier default |
| Claude Sonnet 4.5 | 1 M | ~2 500 | Mid-tier running example; 1 M tier |
| Claude Opus 4.x | 1 M | ~2 500 | Frontier tier; premium pricing |
| Gemini 2.5 | up to ~2 M | ~5 000 | Largest broadly-available window |

Model names and prices in this post are current as of early 2026; providers change both often, so check the provider's pricing page before you commit a number to a budget.

Two warnings before anyone gets excited.

First, **the window is a ceiling, not a target.** Quality degrades long before the ceiling, for the reasons covered in [Post 03](../03-how-llms-read-context/index.md): positional encodings extrapolate, attention dilutes, the middle gets lost. A safe operational range is the lower 25–50 % of the advertised window for a frontier model and the lower 10–20 % for an open-weight one.

Second, **input plus output share the window.** A 200 k Claude call configured to return a 16 k response leaves you 184 k for the prompt, not 200 k. Forget this and your long-context agent will silently start truncating its own answers.

---

## 3. The three budgets

Every LLM call is constrained by three independent budgets. Engineering for one without thinking about the other two is the most common failure mode in early production deployments.

**The token budget** is the one engineers think of first. It is the number of *input* tokens you choose to spend per call. It is bounded above by the context window and, more often, by your patience for cost. As a rule of thumb, a reasonable default for an interactive assistant is 8–16 k input tokens; for a background agent that runs for an hour, 50–100 k is normal; for batch document analysis, 200 k is the working range.

**The cost budget** is what each token costs in dollars. Notice the **input–output asymmetry**: output tokens are priced several times higher than input tokens (roughly 5× across the tiers below), because generating a token runs the full model forward once per token, whereas ingesting the prompt is parallelised. A short prompt with a long answer can cost more than a long prompt with a short answer. Modern frontier pricing for *input* tokens spans roughly two orders of magnitude. The figures below are representative early-2026 published prices (Anthropic, "Prompt caching"); confirm against the provider's page:

| Tier | Example model | $ / 1 M input | $ / 1 M output | Cached-read input |
|---|---|---|---|---|
| Frontier | Claude Opus 4.x | ~$5 | ~$25 | ~10 % of input |
| Mid | Claude Sonnet 4.5, a frontier GPT model | ~$3 | ~$15 | ~10 % of input |
| Cheap | Claude Haiku 4.5, Gemini Flash | ~$1 | ~$5 | ~10 % of input |

The "~10 % of input" cached-read figure is the Anthropic prompt-caching discount: a cache read is billed at about 0.1× the base input price (Anthropic, "Prompt caching"). OpenAI's automatic caching discounts cached input by a smaller amount (around 50 %), so the numbers here are the Anthropic case. Pricing changes monthly; treat the table as orders of magnitude. The decisive ratio is not the absolute number but the roughly five-to-one gap between the cheap tier and the frontier tier, and the further ten-to-one gap that prefix caching opens up *within* a tier.

**The latency budget** is how long the user (or upstream service) will wait. It decomposes into two terms that compose differently than people expect:

$$
T_{\text{total}} = T_{\text{prefill}} + N_{\text{out}} \cdot T_{\text{decode}}
$$

*Prefill* is the time to ingest the prompt, roughly linear in input length; *decode* is the per-token generation time, roughly constant per output token at a given model size (Pope et al., 2022). The figures below are illustrative rules of thumb, not measured benchmarks: use them to reason about *shape*, and measure your own workload before quoting a latency to anyone:

| Model class | Prefill | Decode | 8 k-in / 800-out wall time |
|---|---|---|---|
| Cheap (Haiku, Flash) | ~1 ms / token | ~10 ms / token | ~10 s |
| Mid (Sonnet) | ~2 ms / token | ~20 ms / token | ~30 s |
| Frontier (Opus) | ~3 ms / token | ~40 ms / token | ~60 s |

The numbers move every quarter, but the shape is durable. Two consequences: shrinking the *prompt* helps latency on long inputs; shrinking the *output* helps latency on short ones. Streaming hides decode time but not prefill time, which is why a long-context agent feels sluggish to first token even with streaming on.

---

## 4. The triangle

The three budgets pull against each other. You pick any two and the third goes wherever it must.

- **Cheap and fast** ⇒ accept lower quality. Use a Haiku/Flash/mini-tier model on a small prompt. Good for high-throughput auto-classification, intent detection, simple extraction.
- **Cheap and high-quality** ⇒ accept slow. Use a frontier model with prompt caching, batch endpoints, or off-peak processing. Good for nightly analytics jobs.
- **Fast and high-quality** ⇒ accept expensive. Use a frontier model on a focused prompt with reserved-capacity hosting and cache hits. Good for the user-facing critical path of a paid product.

![The cost-latency-quality triangle](./diagrams/01-budget-triangle.svg)
*Pick any two corners; the third is whatever the first two leave you. There is no configuration that is cheap, fast, and high-quality at once.*

There is no fourth corner. The marketing material that promises all three is selling either the cheapest tier with the smallest prompt (calling it "fast and high-quality" relative to the previous generation of cheap models), or a benchmark configuration that nobody actually runs in production.

The practical mental model: choose the corner you are optimising for *per workflow*, not per company. A coding agent's "explain this stack trace" call lives in the fast-and-high-quality corner; its "summarise the last 200 turns" maintenance call lives in the cheap-and-high-quality corner. Different models, different prompts, same product.

---

## 5. Sizing an agent on an envelope

The arithmetic that follows is the back-of-envelope every team eventually does, written out once. To keep the sums easy to follow, it uses round illustrative rates of **\$2.50 / 1 M input** and **\$10 / 1 M output** (close to the mid tier above; plug in your provider's current numbers to get real figures).

Consider a customer-support agent with the following per-turn shape. Two acronyms appear here: **MCP** (Model Context Protocol, the open standard for exposing tools to a model; Post 15) and **RAG** (retrieval-augmented generation, pulling in the *top-k* most relevant chunks from a store; Post 11). Each contributes its own slice of the input budget:

| Layer | Tokens per call |
|---|---|
| System prompt + format + rules | 3,000 |
| Tool / MCP schemas (8 tools) | 1,600 |
| Memory (user profile + 5 prior tickets summarised) | 1,200 |
| RAG (top-5 chunks of 500 tokens each) | 2,500 |
| Conversation history (compressed) | 2,000 |
| User message | 200 |
| **Input total** | **10,500** |
| Output (typical reply) | 400 |

A single call on a mid-tier model at \$2.50 / M input + \$10 / M output:

$$
\text{Cost} = \frac{10\,500}{10^6} \times \$2.50 + \frac{400}{10^6} \times \$10.00 \approx \$0.0303
$$

Three cents. Now suppose 10,000 conversations a day, 4 turns per conversation, 5 of those calls per turn (sub-agents, tool replies):

$$
10\,000 \times 4 \times 5 \times \$0.0303 \approx \$6\,050\text{ / day}
$$

About six thousand dollars a day, roughly $180,000 a month, before infrastructure. This is the calculation that turns "just call the API" into a real engineering project.

Now turn on prefix caching. The first 4,600 tokens (system prompt + tools) are byte-identical on every call. A cached prefix has a short time-to-live (Anthropic's default is five minutes, refreshed each time it is hit), so under sustained traffic the prefix is continuously re-warmed and nearly every one of the day's ~200,000 calls reads it from cache rather than reprocessing it. A cache read costs ~10 % of the full input price (Anthropic, "Prompt caching"), so the cached portion is billed at \$0.25 / 1 M rather than \$2.50 / 1 M:

$$
\text{Cost}_{\text{cached prefix}} = \frac{4\,600}{10^6} \times \$0.25 + \frac{5\,900}{10^6} \times \$2.50 + \frac{400}{10^6} \times \$10.00 \approx \$0.0199
$$

That single architectural choice, having a stable prefix and putting it at the front, drops the daily bill from about \$6 050 to about \$3 980. A 34 % saving for an afternoon's work.

Finally, route the simpler 60 % of turns (FAQ-shaped questions) to a cheap-tier model at illustrative \$0.30 / M input, \$1.20 / M output. The blended cost drops to roughly \$2 000 / day. The system is now about three times cheaper than the naive baseline, with no measurable change in user-facing quality. **This is what context engineering pays for.**

The whole envelope is fifteen lines of code. The function below takes a per-layer token breakdown and prices and returns the cost of one call; the two calls under it reproduce the \$0.0303 and \$0.0199 figures above:

```python
def call_cost(layers, price_in, price_out, out_tokens,
              cached_prefix=0, cache_discount=0.10):
    """Cost of one LLM call in dollars.
    layers: {name: input_tokens}; price_* in $ per 1M tokens;
    cached_prefix: leading tokens billed at cache_discount x price_in."""
    total_in = sum(layers.values())
    billable_in = total_in - cached_prefix
    return (cached_prefix / 1e6 * price_in * cache_discount
            + billable_in / 1e6 * price_in
            + out_tokens / 1e6 * price_out)

layers = {"system": 3000, "tools": 1600, "memory": 1200,
          "rag": 2500, "history": 2000, "user": 200}
per_call = call_cost(layers, 2.50, 10.00, out_tokens=400)          # 0.0303
cached   = call_cost(layers, 2.50, 10.00, out_tokens=400,
                     cached_prefix=4600)                            # 0.0199
daily    = per_call * 10_000 * 4 * 5                                # 6050
```

### What prompt caching does and does not do

Prefix caching (Anthropic, "Prompt caching") stores the model's internal attention state, the **KV-cache** (the cached key and value tensors introduced in [Post 03](../03-how-llms-read-context/index.md)), for a **byte-identical prefix** so repeat calls skip re-processing it. Keeping that prefix stable is one of the highest-leverage moves in agent design (Yao, "Context Engineering for AI Agents: Lessons from Building Manus", 2025). Three properties decide whether it helps:

- **It caches only an exact prefix.** Change one token near the front, and the cache misses from that point on. Put the volatile parts (the user turn, freshly retrieved chunks) *last* and the stable parts (system prompt, tool schemas) *first*, or nothing caches.
- **It has a minimum length.** Prefixes below roughly 1k – 4k tokens (model-dependent) are not cacheable at all, so tiny prompts see no benefit.
- **It expires.** Anthropic's cache has two time-to-live tiers, a 5-minute default and a 1-hour option; each cache read refreshes the clock, so a prefix stays warm as long as traffic keeps hitting it. Writing to the cache costs *more* than a normal input token (1.25× input for the 5-minute tier, 2× for the 1-hour tier), which is why caching pays off only when the same prefix is reused many times.

Vendors differ. Anthropic caching is explicit (you mark the cache breakpoint) and reads bill at ~10 % of input. OpenAI caching is automatic and discounts cached input by a smaller amount (around 50 %). Gemini offers both implicit and explicit context caching. The architectural lesson is the same everywhere: **order your context stable-to-volatile so the expensive, unchanging bytes sit in front.**

---

## 6. Setting per-layer budgets

The arithmetic above only works if each layer of your context has a budget you actually enforce. A useful starting allocation, treating the *input* token budget as 100 %:

| Layer | Default share | Why |
|---|---|---|
| System prompt | 5–15 % | Must be small enough to keep the cached prefix *cacheable* |
| Tools / MCP | 5–15 % | RAG over tool schemas (Post 15) when this exceeds 15 % |
| Memory | 5–10 % | Compress aggressively; episodic memory should not grow unbounded |
| RAG | 20–40 % | The biggest variable lever; tune retrieval `k` to the budget, not the other way round |
| History | 10–30 % | Summarise on a schedule (Post 12), not at the limit |
| User turn | 1–5 % | Almost always the smallest, despite being the reason for the call |
| **Output reserve** | 10–20 % of *window* | Cap with `max_tokens`; never trust the model to be brief |

![Per-layer token budget allocation](./diagrams/02-per-layer-budget.svg)
*A default split of the input budget across the six layers; RAG and history are the levers that move most, and the output reserve is carved from the window, not the input budget.*

These percentages are starting points, not laws. The discipline that matters is *having* explicit numbers per layer. Without them, the layer that grows fastest (almost always RAG or history) silently consumes everyone else's allocation.

---

## 7. Picking a model: a one-page decision

The five questions below cover almost every model-selection conversation in practice. Walk them in order; the first that gives you a strong answer wins.

1. **Does the task need state-of-the-art reasoning?** (Multi-step planning, code synthesis, hard math, novel domain.) → Frontier tier.
2. **Is the task a short, well-defined extraction or classification?** → Cheap tier; you will not measure the difference.
3. **Is the input long but the task simple?** (Summarise a 200-page report.) → Cheap tier with a long-context model: Gemini Flash, Haiku.
4. **Is the input short but the task hard?** (Architect a refactor.) → Frontier tier with a small prompt; you are paying for thinking, not reading.
5. **Is the task user-facing and time-critical?** → Mid tier with streaming, plus an explicit per-call latency budget that triggers fallback to a cheaper model on timeout.

Two patterns recur often enough to deserve their own names. **Cascade**: try the cheap model first, escalate to the frontier model only when an upstream eval (Post 20) flags the cheap answer. **Plan-and-execute**: a frontier model writes the plan once; cheap models execute the steps. Both shrink the average cost per task without sacrificing tail quality.

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

- OpenAI, *"Tokenizer"* (interactive) and the `tiktoken` library: the canonical reference for the cl100k family, the ~0.75 words-per-token ratio, and the illustrative token counts in §1.
- Anthropic, *"Token counting"* and *"Prompt caching"* (documentation, 2024–25): source of the Claude window sizes in §2, the ~10 % cached-read discount, the cache-write multipliers, and the 5-minute / 1-hour TTL tiers in §5.
- Google, *"Long context"* (Gemini API documentation): the Gemini window sizes in §2 and best practice for the 1 M / 2 M tier.
- Yao, S. (Manus), *"Context Engineering for AI Agents: Lessons from Building Manus"* (2025): the KV-cache argument for a stable prefix that underlies the §5 caching example.
- Sennrich, R. *et al.*, *"Neural Machine Translation of Rare Words with Subword Units"* (2016): the original BPE paper behind §1.
- Pope, R. *et al.*, *"Efficiently Scaling Transformer Inference"* (2022): prefill/decode mechanics that drive the latency model in §3.

Full citations in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 03 — How LLMs read context](../03-how-llms-read-context/index.md)** (back): why quality degrades well below the window ceiling, and what the KV-cache is that prefix caching reuses.
- **[Post 06 — Five context failure modes](../06-context-failure-modes/index.md)**: the symptoms that appear when a budget is wrong.
- **[Post 25 — Long context vs RAG](../25-long-context-vs-rag/index.md)**: the full version of the envelope arithmetic above, applied to the routing decision.
- **[Post 12 — Compress strategies](../12-compress-strategies/index.md)**: what to do when the history or RAG layer breaks its budget.
