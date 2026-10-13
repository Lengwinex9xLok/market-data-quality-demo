# Market Data Quality Demo

A small Python example of validating broker-sourced quote events before using
them in a downstream dataset. The runnable example uses fictional data only.

## Project overview

This demonstration draws on data engineering and hypothesis evaluation work in a
private trading research project. It combines a runnable quote-quality example
with a high-level overview of the research process. The code illustrates schema
validation, duplicate detection, and event-time ordering, helping keep
questionable records visible in the dataset.

## Research process overview

The research asks whether a candidate relationship survives data-quality,
execution, and statistical checks. A selective summary of the evaluation
approach is shown below.

| Stage | Research question |
|---|---|
| Hypothesis and baseline | What economic mechanism is proposed, and what would falsify it relative to a suitable baseline? |
| Data feasibility | Are coverage, timestamps, and the required observations adequate for the proposed question? |
| Causal measurement | Are signal observation, entry, and evaluation separated to avoid shared-price artifacts and look-ahead bias? |
| Execution costs | Which spread, fee, and execution components can be measured, and which remain unknown? |
| Statistical power | On the final eligible sample, what effect can the design detect before candidate outcomes are inspected? |
| Evaluation and decision | Where feasibility permits, use frozen rules, time-ordered evaluation, and inference that respects dependence; record nulls and stop or redesign when evidence is inadequate. |

Closely spaced observations can represent the same underlying event. Episode
aggregation and trading-day clustering help account for that dependence.
Predictive evidence and achievable execution require separate validation.

The runnable example implements the quote-quality checks only. The later research
stages above are a methodological overview; this package contains no executable
alpha model or strategy-performance result.

## Run locally

Requires Python 3.10 or newer. Uses the standard library; no additional packages
or credentials are needed.

```bash
python demo.py
python -m unittest discover -s tests -v
```

The example generates six fictional quote records. Two have no detected issues;
the other four illustrate a duplicate, a timestamp regression, a crossed quote,
and a missing price. The command prints a JSON audit report. Detected issues in
this deliberately malformed fixture are expected.

## Selected design choices

| Concern | Demonstrated check |
|---|---|
| Event identity | Duplicate `(symbol, event_id)` detection |
| Time representation | Timezone-aware timestamps normalized to UTC |
| Stream ordering | Per-symbol timestamp regression detection |
| Quote validity | Finite positive prices and bid/ask ordering |
| Data traceability | Input row number and issue codes in the report |
| Input preservation | The audit does not modify input records |

```text
Fictional broker quote events
            |
            v
Schema and ordering checks
            |
            v
Issue ledger + summary counts
```

## Scope

This is a deliberately small offline example. It checks the supplied records;
it does not establish feed freshness, complete market coverage, or execution
quality. Broker integration and trading functionality are outside this example.

All symbols, identifiers, timestamps, and prices in the demo are fictional. The
example contains no production configuration, account records, market-data
archive, or research results.
