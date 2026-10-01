---
title: Function Calling With Closed-Set Questions
kind: cookbook
source: Function calling (TypeSafe cookbook)
source_url: https://docs.typesafe.ai/cookbooks/function_calling
tags: [cookbook, routing, agent-tooling]
topics: [topic-routing, topic-agent-integration, topic-calibration]
---
# Function Calling With Closed-Set Questions
> Turn a natural-language sentence into a call to an ordinary typed Python function (name + arguments), where every argument is an evaluated enum with a probability, via a `Dispatcher` built from a plain-words spec. Reach for it when function arguments come from fixed lists and you want per-argument confidence.

## What it is / How it works
**Metaphor in source:** a barista marks four options on a cup rather than writing your sentence down. Sentence in -> function name + arguments out, each with a confidence. Domain: a trading assistant with **10 ordinary functions** over **156,780 one-minute bars**.

Examples (command -> call, confidence):
- "plot rolling correlation between nvda and spy for the past month" -> `rolling_correlation(symbol='NVDA', benchmark='SPY', window='1mo')` 0.91
- "compare nvda amd and msft over the past three months" -> `compare_returns(symbols=['NVDA','AMD','MSFT'], window='3mo')` 0.94
- "show me apple daily with volume" -> `plot_price(symbol='AAPL', resolution='1d', include_volume=True)` 0.75
- "what tickers do you have" -> `list_symbols()` 1.00

**Closed sets.** An argument whose values come from a fixed list is a closed set; if it takes one value from the list it gets a [[choice]] question over exactly those values, so whatever reaches the function is a value the function accepts. You leave the functions alone; you add a **spec** in plain words. Example signature: `plot_price(symbol: Literal["SPY","NVDA","AMD","AAPL","MSFT","TSLA"], style: Literal["line","candles"]="line", resolution: Literal["1m","5m","15m","1h","1d"]="15m", window: Literal["1d","1w","1mo","3mo"]="1w", include_volume: bool=False, moving_average: Literal["9","20","50"]|None=None, log_scale: bool=False)`.

**`closed_sets(fn)`** reads a signature and sorts arguments into three shapes:
| Shape | Type hint | Meaning | Question type |
|---|---|---|---|
| choice | `Literal[...]` | one value from the list | Choice |
| set | `list[Literal[...]]` | any number of the values | one Noul per member |
| flag | `bool` | on/off | Noul |

Per function (fillable args): list_symbols 0; market_summary 1 (window); plot_price 7; intraday_pattern 3 (symbol, window, metric); compare_returns 3 (symbols=set, window, normalize=flag); rolling_correlation 4 (symbol, benchmark, window, resolution); summary_stats 2; volatility 3 (symbol, window, annualized=flag); top_movers 2 (window, direction); drawdown 3 (symbol, window, plot=flag). **28 fillable arguments total.**

**Left out:** non-closed arguments (free text, numbers, dates) get no question; the function's default stands. E.g. `top_movers`' `limit` (an `int`) is never asked and keeps default 3.

**The spec (`spec.json`)** holds: a question per argument, a line per option, a description per function, and one more question choosing between functions. An LLM can write it from the signatures. Option keys are the strings the function accepts, so no label->argument mapping afterwards. Per argument:
- `question` (the Choice question), `options` (key -> plain-words meaning),
- `stated` (optional): a second yes/no [[noul]] asking whether the command says anything about this argument at all. If "no", the argument is **omitted** and the function's own default applies. Example `style.stated`: "Does the user say how the chart should be drawn, such as a line, candles, or OHLC bars?"
- Set arguments: the question is asked once per member with `{}` replaced by member name, e.g. "Does the user want {} in the comparison?"
- Example options: `style`: line = "a simple line through the closing prices", candles = "a candlestick or OHLC chart..."; `moving_average` question "How many bars should the moving average cover - nine, twenty, or fifty?" with options 9 (fast), 20, 50 (slow).

**Writing questions.** Ask about the *idea*, not the words a user might pick, because the match is on meaning: "is amd tracking nvidia lately" reaches `rolling_correlation` though neither "tracking" nor "lately" is in `spec.json`. Do **not** name a question after its parameter ("Which resolution?" gives the command nothing to match against).

**`Dispatcher(SPEC, TOOLS, client)`** builds the questions once. **54 questions per command.** Each command is **one request** carrying the function-choice question (`__tool__`, a Choice: "What is the user asking the trading assistant to do?") and every function's argument questions; the dispatcher reads only the chosen function's answers. Question ids: `__tool__`, `plot_price.style` (choice), `plot_price.style?` (noul, the "stated" gate), `compare_returns.symbols.NVDA` (noul). See [[speculative-fan-out]] for the fan-out pattern, [[intent-routing]].

**Confidence = the least certain judgement behind the call**, not the product. Reason: one wrong argument spoils the result; a product answers "is every part right" and falls with the number of arguments even when no single judgement is shaky. `call.weakest()` returns the weakest argument; `call.tool.probability` is the function-choice probability; each argument has `.value`, `.probability`, `.distribution`, `.omitted`. Includes the "stated" gate judgements for omitted arguments (e.g. window omitted with p 0.96).

## When to use / when NOT to use
- Use: tools whose arguments are enums/booleans/sets of enums; you want a probability on each argument and on tool choice, and a way to say "not stated, use default".
- Not covered: free text, numbers, dates are never extracted (default stands). `limit` is the cited example. [inference] pair with an extraction primitive ([[topic-extraction]]) if those matter; the cookbook does not do this.
- Weak spots shown: low-confidence calls (0.53 "when during the day does nvda trade the most" -> `intraday_pattern(symbol='NVDA')`) deserve confirmation. The source does not prescribe a threshold.

## Worked example(s)
All 14 commands (confidence = weakest judgement; `tool` = function-choice probability):

| Command | Call | conf | tool |
|---|---|---|---|
| show nvda 1h | plot_price(symbol='NVDA', resolution='1h') | 0.78 | 1.00 |
| plot rolling correlation between nvda and spy for the past month | rolling_correlation(symbol='NVDA', benchmark='SPY', window='1mo') | 0.91 | 1.00 |
| when during the day does nvda trade the most | intraday_pattern(symbol='NVDA') | 0.53 | 1.00 |
| what moved today | top_movers(window='1d', direction='gainers') | 0.90 | 0.90 |
| what tickers do you have | list_symbols() | 1.00 | 1.00 |
| how did the market do this week | market_summary(window='1w') | 0.96 | 0.99 |
| candles for tesla with a 20 period moving average | plot_price(symbol='TSLA', style='candles', moving_average='20') | 0.69 | 0.97 |
| compare nvda amd and msft over the past three months | compare_returns(symbols=['NVDA','AMD','MSFT'], window='3mo') | 0.94 | 1.00 |
| how volatile is tsla | volatility(symbol='TSLA') | 0.96 | 1.00 |
| biggest losers today | top_movers(window='1d', direction='losers') | 0.98 | 0.98 |
| worst drawdown for nvda this quarter, and chart it please | drawdown(symbol='NVDA', window='3mo', plot=True) | 0.84 | 0.84 |
| spy stats for the last month | summary_stats(symbol='SPY', window='1mo') | 0.88 | 0.88 |
| show me apple daily with volume | plot_price(symbol='AAPL', resolution='1d', include_volume=True) | 0.75 | 0.85 |
| is amd tracking nvidia lately | rolling_correlation(symbol='AMD', benchmark='NVDA') | 0.82 | 0.82 |

Observations from the source:
- Both long commands came out as asked: the first filled four args from one sentence; `symbol` and `benchmark` draw from the same six tickers and each landed in the right slot because questions spell out roles ("the one being measured, named first" vs "the second one named, the yardstick"). The compare command put 3 tickers in the set and left the other 3 out.
- Call objects have `.run()`: plots for the 3 chart examples; text for `market_summary` ("the board over 1w": NVDA 254.12 9.62% 389,465,563; AMD 184.20 1.51% 182,740,497; AAPL 258.71 0.97% 223,818,998; SPY 664.86 0.40% 138,617,365; MSFT 451.35 0.26% 113,427,173; TSLA 320.22 -0.97% 266,317,023) and `top_movers` ("top 3 losers over 1d": AMD -0.57% -> 184.20, MSFT 0.67% -> 451.35, AAPL 1.40% -> 258.71; note positive-return tickers appear under "losers" because only 6 tickers exist and limit=3; source does not comment).

**Per-argument breakdown** for "is amd tracking nvidia lately" -> `rolling_correlation(symbol='AMD', benchmark='NVDA')`, confidence 0.82:
- symbol 'AMD' p 0.87 (AMD 0.87, NVDA 0.13, AAPL 0.00)
- benchmark 'NVDA' p 0.78 (NVDA 0.92, AMD 0.08, AAPL 0.00) -> **weakest argument**
- window: omitted, default stands, p 0.96; resolution: omitted, default stands, p 0.99.
- Window/resolution omitted because "lately" gives neither; defaults are one month and hourly bars. Without the `stated` gate the Choice would have had to name some window, and would have named one confidently.

## Numbers & limits
| Item | Value |
|---|---|
| Functions / fillable args | 10 / 28 |
| Questions per command | 54 (one request) |
| Model | `jev-1.12` |
| Data | 156,780 one-minute bars |
| Setup | `pip install ipython polars matplotlib numpy 'cooksafe>=0.2.0,<0.3.0'`; set `TYPESAFE_API_KEY`; `trader.py` (functions + cached client), `dispatch.py` (signature+spec -> call) |
| Playground link | holds one command plus the `__tool__` question and the picked function's questions (editable) |

## Gotchas
- Confidence is a **min**, not a product; do not multiply per-argument probabilities.
- Without `stated`, optional args get filled confidently with a guess. Use `stated` to make arguments optional.
- Name questions after meaning, not the parameter name.
- A command that matches nothing: not shown in the source. [inference] `__tool__` is a Choice over the 10 functions, so every command picks one; there is no explicit "none of these" option described.
- Free text/number/date arguments are ignored.

## Related
[[choice]] · [[noul]] · [[confidence]] · [[intent-routing]] · [[speculative-fan-out]] · [[confidence-gated-routing]] · [[jev-mcp-server]] · [[typesafe-agent-skill]] · [[cookbooks-overview]]
