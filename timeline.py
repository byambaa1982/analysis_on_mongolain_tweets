#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import pandas as pd
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Engagement timeline chart from tweet CSV")
    parser.add_argument("csv_file", type=str, help="Input CSV (e.g. данх.csv)")
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).parent / args.csv_file

    if not csv_path.exists():
        print(f"Error: file not found → {csv_path}")
        return

    keyword = csv_path.stem
    df = pd.read_csv(csv_path)
    df["posted_date"] = pd.to_datetime(df["posted_date"], utc=True).dt.tz_convert("Asia/Ulaanbaatar")
    df["favorites"]   = pd.to_numeric(df["favorites"], errors="coerce").fillna(0)
    df["retweets"]    = pd.to_numeric(df["retweets"],  errors="coerce").fillna(0)
    df = df.set_index("posted_date").sort_index()

    hourly = df.resample("h").agg(
        tweets   =("post_text",  "count"),
        favorites=("favorites",  "sum"),
        retweets =("retweets",   "sum"),
    ).reset_index()

    labels      = json.dumps(hourly["posted_date"].dt.strftime("%m/%d %H:00").tolist())
    tweets_data = json.dumps(hourly["tweets"].tolist())
    favs_data   = json.dumps(hourly["favorites"].astype(int).tolist())
    rts_data    = json.dumps(hourly["retweets"].astype(int).tolist())

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<title>Timeline · {keyword}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f1117; font-family: 'Segoe UI', sans-serif; padding: 28px; color: #d0d8e8; }}
  h1 {{ color: #fff; font-size: 18px; margin-bottom: 4px; letter-spacing: 0.5px; }}
  .subtitle {{ color: #556677; font-size: 12px; margin-bottom: 24px; }}
  .chart-wrap {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px; padding: 24px; }}
  .footer {{ color: #445566; font-size: 11px; text-align: right; margin-top: 14px; }}
</style>
</head>
<body>
  <h1>📈 Engagement Timeline · {keyword}</h1>
  <div class="subtitle">Tweet volume, likes and retweets grouped by hour (Ulaanbaatar time, UTC+8)</div>
  <div class="chart-wrap">
    <canvas id="chart"></canvas>
  </div>
  <div class="footer">Byamba Enkhbat · data: X API</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const labels = {labels};
const ctx = document.getElementById('chart').getContext('2d');
new Chart(ctx, {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{
        label: 'Tweets',
        data: {tweets_data},
        borderColor: '#1d9bf0',
        backgroundColor: '#1d9bf018',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        yAxisID: 'y',
      }},
      {{
        label: '❤️ Favorites',
        data: {favs_data},
        borderColor: '#f91880',
        backgroundColor: '#f9188018',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        yAxisID: 'y1',
      }},
      {{
        label: '🔁 Retweets',
        data: {rts_data},
        borderColor: '#00ba7c',
        backgroundColor: '#00ba7c18',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        yAxisID: 'y1',
      }},
    ],
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{
      legend: {{
        labels: {{ color: '#d0d8e8', padding: 20 }},
      }},
      tooltip: {{
        backgroundColor: '#1a1d27',
        borderColor: '#2a2d3a',
        borderWidth: 1,
        titleColor: '#ffffff',
        bodyColor: '#d0d8e8',
      }},
    }},
    scales: {{
      x: {{
        ticks: {{ color: '#556677', maxTicksLimit: 12, maxRotation: 30 }},
        grid:  {{ color: '#1e2130' }},
      }},
      y: {{
        position: 'left',
        ticks: {{ color: '#1d9bf0' }},
        grid:  {{ color: '#1e2130' }},
        title: {{ display: true, text: 'Tweets', color: '#1d9bf0' }},
      }},
      y1: {{
        position: 'right',
        ticks: {{ color: '#f91880' }},
        grid:  {{ drawOnChartArea: false }},
        title: {{ display: true, text: 'Engagement', color: '#f91880' }},
      }},
    }},
  }},
}});
</script>
</body>
</html>"""

    out = csv_path.with_name(f"{keyword}_timeline.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
