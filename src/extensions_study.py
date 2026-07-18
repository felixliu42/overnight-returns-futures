"""
EXTENSIONS (exploratory — not pre-registered): closure-duration and venue tests.

Motivating hypothesis (proposed, then falsified): "human optimism inflates the
open", implying (P1) gap returns grow with closure duration, (P3) post-closure
intraday reversal. Discriminator vs. a risk story: (P4) gap variance ~ closed time.

Findings (see README Extensions section):
- P1 rejected/inverted: the premium sits in weekday overnights; weekends
  (~65h closed) and long closures carry ~zero.
- P3 rejected with opposite sign: Monday intraday is the strongest weekday.
- P4 rejected: gap variance grows far slower than sqrt(closed hours)
  (French & Roll 1986: volatility accrues in trading time).
- Venue comparison (same period): overnight share of returns — cash ETFs
  60-62%, futures 57-58%. Direction as predicted, magnitude small.
- Crypto control: BTC/ETH never close, yet show the same US-clock pattern,
  stronger (77%+ of returns in US off-hours; ETH's US-daytime leg negative).
  Closure-based explanations are ruled out; the premium follows the clock.

All inputs are committed legs files in data/ — reruns from a clone alone.
"""
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

def boot(x, seed=42, n=8000):
    rng = np.random.default_rng(seed)
    m = np.array([rng.choice(x, len(x)).mean() for _ in range(n)])
    return (m <= 0).mean()

def load(name):
    return pd.read_csv(DATA / name, parse_dates=["day"])

def closure_duration():
    print("=" * 100)
    print("CLOSURE-DURATION TESTS (NQ / ES, all gap lengths)")
    print("=" * 100)
    for sym in ("NQ", "ES"):
        df = load(f"{sym}_legs_all_gaps.csv")
        print(f"\n{sym}: gap return by closure duration")
        print(f"{'group':<24}{'N':>6}{'mean bp':>9}{'P<=0':>7}{'bp/hour':>9}{'std/sqrt(h)':>12}")
        for name, m in (("normal overnight (1d)", df["gap_cal_days"] == 1),
                        ("weekend (3d)", df["gap_cal_days"] == 3),
                        ("long closure (4d+)", df["gap_cal_days"] >= 4)):
            g = df[m]
            x = g["overnight"].to_numpy()
            hrs = g["closed_hours"].mean()
            print(f"{name:<24}{len(g):>6}{x.mean()*1e4:>9.2f}{boot(x)*100:>6.1f}%"
                  f"{x.mean()*1e4/hrs:>9.3f}{x.std(ddof=1)*1e4/np.sqrt(hrs):>12.2f}")
        after_long = df[df["gap_cal_days"] >= 3]["intraday"].to_numpy()
        after_norm = df[df["gap_cal_days"] == 1]["intraday"].to_numpy()
        print(f"  reversal test: intraday after weekend/holiday {after_long.mean()*1e4:+.2f} bp "
              f"vs after normal overnight {after_norm.mean()*1e4:+.2f} bp "
              f"(optimism predicted the first to be LOWER; it is higher)")

def venue_comparison():
    print()
    print("=" * 100)
    print("VENUE COMPARISON — overnight share of total returns")
    print("=" * 100)
    hdr = f"{'venue / instrument':<26}{'N':>6}{'O/N bp':>10}{'P<=0':>9}{'intra bp':>10}{'P<=0':>9}{'O/N share':>11}"
    def row(name, df):
        on, idr = df["overnight"].to_numpy(), df["intraday"].to_numpy()
        tot = on.mean() + idr.mean()
        share = on.mean() / tot * 100 if tot else np.nan
        print(f"{name:<26}{len(df):>6}{on.mean()*1e4:>10.2f}{boot(on)*100:>8.1f}%"
              f"{idr.mean()*1e4:>10.2f}{boot(idr)*100:>8.1f}%{share:>10.1f}%")
    print("\nPanel A — common window Jun 2015 - Jun 2026 (16:00 -> 9:30 ET; ETFs use actual open):")
    print(hdr)
    row("cash ETF  SPY", load("SPY_legs.csv"))
    row("cash ETF  QQQ", load("QQQ_legs.csv"))
    row("futures   ES", load("ES_legs.csv"))
    row("futures   NQ", load("NQ_legs.csv"))
    print("\nPanel B — crypto window 2017-08 - 2026-06 (16:00 -> 9:00 ET boundaries; weekdays, 1-day gaps):")
    print(hdr)
    for sym in ("BTC", "ETH"):
        d = load(f"{sym}_legs.csv")
        row(f"crypto    {sym} (24/7)", d[(d["day"].dt.dayofweek < 5) & (d["gap_days"] == 1)])
    print("\nPanel C — crypto weekend (never closes: is Fri 16:00 -> Mon 9:00 special?):")
    for sym in ("BTC", "ETH"):
        d = load(f"{sym}_legs.csv")
        wk = d[(d["day"].dt.dayofweek < 5) & (d["gap_days"] == 1)]["overnight"].to_numpy()
        p16 = d.set_index("day")["p16"]
        mon = d[d["day"].dt.dayofweek == 0].copy()
        fri = mon["day"] - pd.Timedelta(days=3)
        have = fri.isin(p16.index).to_numpy()
        wkend = mon.loc[have, "p09"].to_numpy() / p16.loc[fri[have]].to_numpy() - 1
        print(f"  {sym}: weekday off-hours {wk.mean()*1e4/17.0:+.3f} bp/h vs weekend {wkend.mean()*1e4/65.0:+.3f} bp/h "
              f"(futures weekend rate for reference: ~+0.02 bp/h)")

if __name__ == "__main__":
    closure_duration()
    venue_comparison()
