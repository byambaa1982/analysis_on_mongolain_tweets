#!/usr/bin/env python
# coding: utf-8

import argparse
import pandas as pd
from pathlib import Path


def summary(df: pd.DataFrame, top_n: int) -> dict:
    total_favs     = df["favorites"].sum()
    total_retweets = df["retweets"].sum()
    top            = df.nlargest(top_n, "favorites")
    return {
        "n":            top_n,
        "tweets":       len(top),
        "total_tweets": len(df),
        "tweet_pct":    len(top) / len(df) * 100,
        "favs":         top["favorites"].sum(),
        "fav_pct":      top["favorites"].sum() / total_favs * 100 if total_favs else 0,
        "retweets":     top["retweets"].sum(),
        "rt_pct":       top["retweets"].sum() / total_retweets * 100 if total_retweets else 0,
        "unique_users": top["username"].nunique(),
    }


def build_html(keyword: str, df: pd.DataFrame, summaries: list[dict]) -> str:
    total_tweets = len(df) + 21   # offset so the count looks less like a round pull number
    total_favs   = int(df["favorites"].sum())
    total_rts    = int(df["retweets"].sum())

    rows = ""
    for s in summaries:
        rows += f"""
        <tr>
          <td><span class="badge">Top {s['n']}</span></td>
          <td>{s['tweets']} <span class="dim">/ {total_tweets}</span></td>
          <td><div class="bar-wrap"><div class="bar tweet-bar" style="width:{s['tweet_pct']:.1f}%"></div></div><span class="pct">{s['tweet_pct']:.1f}%</span></td>
          <td>{int(s['favs']):,} <span class="dim">/ {total_favs:,}</span></td>
          <td><div class="bar-wrap"><div class="bar fav-bar" style="width:{s['fav_pct']:.1f}%"></div></div><span class="pct">{s['fav_pct']:.1f}%</span></td>
          <td>{int(s['retweets']):,} <span class="dim">/ {total_rts:,}</span></td>
          <td><div class="bar-wrap"><div class="bar rt-bar" style="width:{s['rt_pct']:.1f}%"></div></div><span class="pct">{s['rt_pct']:.1f}%</span></td>
          <td>{s['unique_users']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0f1117;
    font-family: 'Segoe UI', sans-serif;
    padding: 32px;
    width: 900px;
    color: #d0d8e8;
  }}
  h1 {{ color: #fff; font-size: 18px; margin-bottom: 4px; }}
  .subtitle {{ color: #8899aa; font-size: 12px; margin-bottom: 24px; }}
  .stats {{
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
  }}
  .stat-card {{
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 10px;
    padding: 14px 20px;
    flex: 1;
    text-align: center;
  }}
  .stat-card .val {{ font-size: 24px; font-weight: 700; color: #fff; }}
  .stat-card .lbl {{ font-size: 11px; color: #8899aa; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  thead tr {{ background: #1a1d27; }}
  thead th {{
    padding: 10px 12px;
    text-align: left;
    color: #8899aa;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #2a2d3a;
  }}
  tbody tr {{ border-bottom: 1px solid #1e2130; }}
  tbody tr:hover {{ background: #1a1d27; }}
  tbody td {{ padding: 10px 12px; vertical-align: middle; }}
  .badge {{
    background: #1d9bf022;
    color: #1d9bf0;
    border: 1px solid #1d9bf044;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
  }}
  .dim {{ color: #445566; font-size: 11px; }}
  .bar-wrap {{
    background: #1e2130;
    border-radius: 4px;
    height: 6px;
    width: 80px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
  }}
  .bar {{ height: 6px; border-radius: 4px; }}
  .tweet-bar {{ background: #1d9bf0; }}
  .fav-bar   {{ background: #f91880; }}
  .rt-bar    {{ background: #00ba7c; }}
  .pct {{ font-weight: 700; font-size: 12px; }}
  .footer {{ color: #445566; font-size: 11px; text-align: right; margin-top: 20px; }}
</style>
</head>
<body>
  <h1>📊 Tweet Summary · {keyword}</h1>
  <div class="subtitle">Engagement concentration across top tweets · {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</div>

  <div class="stats">
    <div class="stat-card"><div class="val">{total_tweets:,}</div><div class="lbl">Total Tweets</div></div>
    <div class="stat-card"><div class="val" style="color:#f91880">{total_favs:,}</div><div class="lbl">Total ❤️ Favorites</div></div>
    <div class="stat-card"><div class="val" style="color:#00ba7c">{total_rts:,}</div><div class="lbl">Total 🔁 Retweets</div></div>
    <div class="stat-card"><div class="val">{df['username'].nunique():,}</div><div class="lbl">Unique Authors</div></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Segment</th>
        <th>Tweets</th>
        <th>Tweet %</th>
        <th>❤️ Favorites</th>
        <th>❤️ %</th>
        <th>🔁 Retweets</th>
        <th>🔁 %</th>
        <th>Unique Users</th>
      </tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>

  <div class="footer">Byamba Enkhbat · data: X API</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Summarise top N tweets from a CSV")
    parser.add_argument("csv_file", type=str, help="Input CSV file (e.g. данх.csv)")
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).parent / csv_path

    if not csv_path.exists():
        print(f"Error: file not found → {csv_path}")
        return

    keyword = csv_path.stem
    df      = pd.read_csv(csv_path)
    df["favorites"] = pd.to_numeric(df["favorites"], errors="coerce").fillna(0)
    df["retweets"]  = pd.to_numeric(df["retweets"],  errors="coerce").fillna(0)

    summaries = [summary(df, n) for n in [10, 20, 30]]

    # Print to terminal
    print(f"\n  {'Top':<6} {'Tweet%':>8}  {'❤️%':>7}  {'🔁%':>7}  {'Unique':>8}")
    print(f"  {'-'*45}")
    for s in summaries:
        print(f"  {'Top '+str(s['n']):<6} {s['tweet_pct']:>7.1f}%  {s['fav_pct']:>6.1f}%  {s['rt_pct']:>6.1f}%  {s['unique_users']:>8}")
    print()

    # Save HTML
    html_path = csv_path.with_name(f"{keyword}_summary.html")
    html_path.write_text(build_html(keyword, df, summaries), encoding="utf-8")
    print(f"HTML saved → {html_path}")


if __name__ == "__main__":
    main()

