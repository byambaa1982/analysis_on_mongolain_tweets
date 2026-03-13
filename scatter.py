#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import pandas as pd
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Likes vs retweets scatter plot from tweet CSV")
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
    df["retweets"]  = pd.to_numeric(df["retweets"],  errors="coerce").fillna(0)

    points = []
    for _, row in df.iterrows():
        preview = str(row["post_text"])[:80].replace("\\", "").replace('"', "'")
        points.append({
            "x":    int(row["favorites"]),
            "y":    int(row["retweets"]),
            "user": str(row["username"]),
            "text": preview,
        })

    scatter_data = json.dumps(points, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<title>Scatter · {keyword}</title>
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
  <h1>🔵 Likes vs Retweets · {keyword}</h1>
  <div class="subtitle">Each dot = one tweet. Hover for author &amp; preview. Outliers reveal viral or bot-like patterns.</div>
  <div class="chart-wrap">
    <canvas id="chart"></canvas>
  </div>
  <div class="footer">Byamba Enkhbat · data: X API</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const raw = {scatter_data};
const ctx = document.getElementById('chart').getContext('2d');

new Chart(ctx, {{
  type: 'scatter',
  data: {{
    datasets: [{{
      label: 'Tweets',
      data: raw.map(p => ({{ x: p.x, y: p.y }})),
      backgroundColor: '#1d9bf044',
      borderColor: '#1d9bf0',
      borderWidth: 1,
      pointRadius: 5,
      pointHoverRadius: 9,
      pointHoverBackgroundColor: '#f91880',
      pointHoverBorderColor: '#fff',
    }}],
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: '#1a1d27',
        borderColor: '#2a2d3a',
        borderWidth: 1,
        titleColor: '#1d9bf0',
        bodyColor: '#d0d8e8',
        callbacks: {{
          title: (items) => '@' + raw[items[0].dataIndex].user,
          label: (item) => [
            `❤️ ${{item.raw.x}} likes   🔁 ${{item.raw.y}} retweets`,
            raw[item.dataIndex].text + '…',
          ],
        }},
      }},
    }},
    scales: {{
      x: {{
        ticks: {{ color: '#556677' }},
        grid:  {{ color: '#1e2130' }},
        title: {{ display: true, text: '❤️ Favorites', color: '#f91880' }},
      }},
      y: {{
        ticks: {{ color: '#556677' }},
        grid:  {{ color: '#1e2130' }},
        title: {{ display: true, text: '🔁 Retweets', color: '#00ba7c' }},
      }},
    }},
  }},
}});
</script>
</body>
</html>"""

    out = csv_path.with_name(f"{keyword}_scatter.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
