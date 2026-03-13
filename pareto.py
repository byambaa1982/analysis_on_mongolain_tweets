#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import pandas as pd
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Pareto chart — likes per tweet + cumulative % from CSV")
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
    df["favorites"] = pd.to_numeric(df["favorites"], errors="coerce").fillna(0)
    df = df.sort_values("favorites", ascending=False).reset_index(drop=True)

    total_favs = df["favorites"].sum()
    df["cumulative_pct"] = (df["favorites"].cumsum() / total_favs * 100).round(2)

    n = min(len(df), 100)
    top = df.head(n)

    labels    = json.dumps([f"#{i+1}" for i in range(n)])
    bar_data  = json.dumps(top["favorites"].astype(int).tolist())
    line_data = json.dumps(top["cumulative_pct"].tolist())

    # Annotation: where does cumulative cross 50% and 80%?
    marks = {}
    for threshold in [50, 80]:
        idx = (top["cumulative_pct"] >= threshold).idxmax()
        if top.loc[idx, "cumulative_pct"] >= threshold:
            marks[threshold] = int(idx)

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<title>Pareto · {keyword}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f1117; font-family: 'Segoe UI', sans-serif; padding: 28px; color: #d0d8e8; }}
  h1 {{ color: #fff; font-size: 18px; margin-bottom: 4px; letter-spacing: 0.5px; }}
  .subtitle {{ color: #556677; font-size: 12px; margin-bottom: 24px; }}
  .chart-wrap {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px; padding: 24px; }}
  .insight {{ margin-top: 16px; display: flex; gap: 16px; flex-wrap: wrap; }}
  .badge {{
    background: #1e2130; border: 1px solid #2a2d3a; border-radius: 6px;
    padding: 8px 16px; font-size: 12px; color: #d0d8e8;
  }}
  .badge span {{ color: #f91880; font-weight: 700; font-size: 14px; }}
  .footer {{ color: #445566; font-size: 11px; text-align: right; margin-top: 14px; }}
</style>
</head>
<body>
  <h1>📊 Pareto Chart · {keyword}</h1>
  <div class="subtitle">Individual tweet likes (bars) vs. cumulative share of total engagement (line) — top {n} tweets by likes</div>
  <div class="chart-wrap">
    <canvas id="chart"></canvas>
  </div>
  <div class="insight" id="insights"></div>
  <div class="footer">Byamba Enkhbat · data: X API</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const marks = {json.dumps(marks)};
const labels = {labels};
const ctx = document.getElementById('chart').getContext('2d');

new Chart(ctx, {{
  data: {{
    labels,
    datasets: [
      {{
        type: 'bar',
        label: '❤️ Likes',
        data: {bar_data},
        backgroundColor: '#f9188044',
        borderColor: '#f91880',
        borderWidth: 1,
        yAxisID: 'y',
      }},
      {{
        type: 'line',
        label: 'Cumulative %',
        data: {line_data},
        borderColor: '#1d9bf0',
        backgroundColor: 'transparent',
        pointRadius: 0,
        borderWidth: 2.5,
        tension: 0.05,
        yAxisID: 'y1',
      }},
    ],
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ labels: {{ color: '#d0d8e8', padding: 20 }} }},
      tooltip: {{
        backgroundColor: '#1a1d27',
        borderColor: '#2a2d3a',
        borderWidth: 1,
        titleColor: '#fff',
        bodyColor: '#d0d8e8',
      }},
    }},
    scales: {{
      x: {{
        ticks: {{ color: '#556677', maxTicksLimit: 20 }},
        grid:  {{ color: '#1e2130' }},
      }},
      y: {{
        position: 'left',
        ticks: {{ color: '#f91880' }},
        grid:  {{ color: '#1e2130' }},
        title: {{ display: true, text: '❤️ Likes', color: '#f91880' }},
      }},
      y1: {{
        position: 'right',
        min: 0,
        max: 100,
        ticks: {{ color: '#1d9bf0', callback: v => v + '%' }},
        grid:  {{ drawOnChartArea: false }},
        title: {{ display: true, text: 'Cumulative %', color: '#1d9bf0' }},
      }},
    }},
  }},
}});

// Insight badges
const box = document.getElementById('insights');
for (const [pct, idx] of Object.entries(marks)) {{
  const d = document.createElement('div');
  d.className = 'badge';
  d.innerHTML = `<span>${{idx + 1}}</span> tweets capture <span>${{pct}}%</span> of all likes`;
  box.appendChild(d);
}}
</script>
</body>
</html>"""

    out = csv_path.with_name(f"{keyword}_pareto.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
