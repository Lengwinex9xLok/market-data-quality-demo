# Market Data Quality Demo

A small quote-data checker from my trading research work. The larger project
includes broker-data collection, data-quality checks, and tests of trading
hypotheses. This repository shares an offline example using synthetic quotes.

## What the demo checks

`demo.py` checks event identifiers, timestamps, and bid/ask prices. It flags
duplicate records, timestamps that go backwards within a symbol's stream,
missing or non-finite prices, and bids above asks.

The audit leaves the input records unchanged. Each issue includes its row number
so it can be traced back to the input. Timestamps must include a timezone;
the checker converts them to UTC rather than guessing the timezone.

The example has six fictional quotes. Four deliberately contain errors, leaving
two rows without detected issues. Running it prints a JSON report with these
counts and the affected rows.

## Run

Requires Python 3.10 or newer. Everything uses the standard library.

```bash
python demo.py
python -m unittest discover -s tests -v
```

The five tests cover the injected errors, equivalent timestamps in different
timezones, invalid prices, input preservation, and repeated timestamp regressions.

## How I decide whether to continue a study

In the private project, I have investigated trading hypotheses and built tools
to check whether the data and evaluation can support them. Some ideas stopped at
feasibility checks; others reached evaluation and failed their decision criteria.
Those outcomes stay in the research record.

For a new study, I first check whether the required observations are available
and whether the sample can detect an effect large enough to matter after costs.
Signal observations, entry prices, and evaluation prices are separated to avoid
look-ahead bias and relationships created by sharing the same price.

I also check which costs can actually be measured. Quote-based estimates still
leave actual fill quality unverified. Closely spaced observations are grouped
into episodes, and uncertainty is assessed across trading days.

If essential data is missing, important costs remain unknown, or the required
sample is unrealistic, I stop and record the reason before inspecting candidate
returns. If those checks pass, evaluation proceeds under frozen rules.
A failed evaluation is recorded without changing the rules to fit the result.

This repository contains the data-checking example only. The collector,
broker configuration, real data, specific signals, and full study results remain
private. Passing these checks does not establish feed freshness, full market
coverage, or a profitable strategy.
