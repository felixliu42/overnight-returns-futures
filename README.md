# The Overnight Return Premium in Equity Index Futures (2015-2026)

A replication study of the documented "overnight return premium" (Cliff, Cooper & Gulen 2008; Lou, Polk & Skouras, *Journal of Financial Economics* 2019) on NQ and ES futures using data from June 2015 - June 2026, as well as an evaluation of whether purchasing futures contracts overnight and selling them at market open is more profitable compared to simply holding the contracts through the full day.

Fully reproducible from this repo alone: the derived daily session-leg data is committed (`data/*_legs.csv`, ~250KB each), so every statistic and figure reruns with nothing but `git clone` and `python src/overnight_intraday_study.py`.

## Research question

Split each trading day at the cash-market open and close. The original study on the overnight return premium finds that in US equity indices, nearly all long-run returns historically accrued overnight while intraday returns averaged near zero. This partition is defined concretely by the clock, making it an ideal subject for replication.

Futures expand upon the aforementioned overnight return premium studies because both legs are traded for almost their entire duration, meaning that traders can react to news overnight. An overnight premium that persists in futures would support the clientele-based mechanism of Lou, Polk & Skouras while arguing against simple "locked-in risk" explanations.

Additionally, the Cliff, Cooper & Gulen study found that intraday returns were actually slightly negative, suggesting that holding equities overnight and selling them at the market open could be a profitable strategy. This study also aims to determine whether such a strategy would be profitable in the case that an overnight/intraday return gap does exist on NQ and ES futures.

## Experiment design

Overnight = 16:00 to 9:30 ET, intraday = 9:30 to 16:00. The data period is split into two halves at the start of 2021 in order to account for and test the overnight return premium in different market regimes. Trades are calculated with fills at the first 1-minute close at/after each boundary . Costs for tradability: one round-trip/day (all-in commission + 1 tick slippage per side).

## Results

![Cumulative curves](figures/fig_overnight_curves.png)

| | NQ overnight | NQ intraday | ES overnight | ES intraday |
| --- | --- | --- | --- | --- |
| Mean bp/day | +4.34 | +3.18 | +2.98 | +2.21 |
| Annualized | +11.6% | +8.3% | +7.8% | +5.7% |
| 90% bootstrap CI (bp) | [+1.9, +6.8] | [+0.2, +6.1] | [+0.7, +5.2] | [−0.1, +4.4] |
| P(mean ≤ 0) | 0.3% | 3.9% | 2.1% | 5.6% |
| Volatility (ann.) | 13.8% | 17.0% | 11.7% | 13.1% |
| Monthly Sharpe | 0.87 | 0.52 | 0.65 | 0.46 |
| Growth of $1 (11y) | $2.89 | $2.00 | $2.06 | $1.65 |

The overnight return premium does exist in index futures, but not as strongly as in their equity counterparts. The Cliff, Cooper & Gulen study's stronger claim that intraday returns are about zero does not hold in this modern futures sample.

![Yearly breakdown](figures/fig_overnight_yearly.png)

The above graph shows that the overnight premium is stable across the two halves of the experiment (+4.40 bp/day pre-2021, +4.28 after on NQ) and weathered the 2022 bear market better than the intraday leg (−5.0 vs −9.8 bp/day).

## Tradability

| Overnight-only, net of daily costs | NQ | ES |
| --- | --- | --- |
| Avg cost per day | 0.81 bp | 1.78 bp |
| Net return | **+9.3%/yr** | +3.1%/yr |
| P(≤ 0) | 1.1% | **19.7%** |
| Monthly Sharpe | 0.71 | 0.26 |

The NQ overnight-only strategy does not beat buy-and-hold (+20.9%/yr, 0.96 Sharpe, no daily costs) in this sample, and on ES the overnight premium does not even survive trading costs. 

## Discussion

The result lands between the original study's strong claim and a null: a real, stable overnight premium exists in modern NQ futures, surviving bootstrap inference, costs, and a subperiod split between market regimes. Its persistence in a venue where overnight trading is fully possible weighs against pure inaccessibility-risk explanations. However, the premium is far smaller than the 1993-2008 equity era suggested, and is not by itself a reason to trade rather than hold. 

**Limitations:** unadjusted continuous contracts (quarterly roll gaps land in the overnight leg, small relative to leg volatility); a single asset class in a predominantly bull-market sample; no financing/margin modeling; boundary fills assume marketable orders at the first 1-minute close.

## Extensions (exploratory): the premium follows the clock, not the closure

The section below details my research on a follow-up hypothesis: "optimism accumulated while markets are closed inflates the open." This was formalized into falsifiable predictions and tested (`src/extensions_study.py`).  Every prediction failed, with the failures suggesting an interesting conclusion:

- Gap returns do not grow with closure time. The premium sits in ordinary weekday overnights (~17.5h closed, +5.5 bp); weekends (~65h) and long holiday closures carry approximately nothing. Per hour closed: 0.31 bp vs 0.02 bp.
- There is no post-closure reversal. If opens were optimism-inflated, Mondays should deflate; instead Monday has the *strongest* intraday returns of the week.
- Gap return variance grows far slower than closed time - volatility accrues in trading time, independently rediscovering a result already reported in French & Roll (1986).
- Venue comparison (same period): cash ETFs route 60-62% of returns through the overnight leg, futures 57-58% - the direction a market-structure story predicts, but small.
- Crypto control test: BTC and ETH never close, yet split by the New York Stock Exchange's operating hours they show an even stronger overnight/intraday gap than equities and futures - 77%+ of BTC's weekday return accrues during US off-hours, and ETH's US-daytime leg is negative. Crypto also earns its normal off-hours rate straight through weekends, while index futures - which also trade on Sunday evenings - earn nothing.

![Extensions](figures/fig_extensions.png)

Taken together: closure-based explanations (building up optimism, locked-in risk compensation) are ruled out. The overnight premium is a property of the weekday clock - volatility lives inside the US trading day, returns accrue outside it. This applies to all venues tested in this study, which is an argument against any explanation that leans on equity-market structure alone. Derived legs data for all six instruments (SPY, QQQ, ES, NQ, BTC, ETH) is committed in `data/`, so these tables can be reproduced from a clone. Caveats: crypto sample is 2017-2026 with large drift and volatility; crypto "market open" was logged at 9:00 ET due to only having hourly bars, but an NQ 9:00-boundary check shows the half-hour shift is immaterial; ETF prices are adjusted series (dividend effects of ~1%/yr may smear across legs).

## Reproducing

```bash
pip install pandas numpy
python src/overnight_intraday_study.py        # both symbols, full tables
python src/overnight_intraday_study.py NQ     # one symbol
```

To rebuild `data/*_legs.csv` from raw 1-minute bars, set `RAW_DATA_DIR` to a folder of `MNQ_YYYY/raw_data.csv` / `ES_YYYY/raw_data.csv` files (Databento GLBX.MDP3, ohlcv-1m).

---

*Companion project: an 11-year falsification study of ICT/"Smart Money" trading strategies, built with the same validation machinery (nested walk-forward, cost modeling, bootstrap inference) located at /ict-nq-falsification-study.*
