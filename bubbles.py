#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import pandas as pd
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Author bubble chart from tweet CSV")
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

    authors = (
        df.groupby("username")
        .agg(
            total_favs  =("favorites",  "sum"),
            total_rts   =("retweets",   "sum"),
            tweet_count =("post_text",  "count"),
        )
        .sort_values("total_favs", ascending=False)
        .reset_index()
    )

    max_favs = authors["total_favs"].max() or 1
    MAX_R, MIN_R = 44, 4

    points = []
    for _, row in authors.iterrows():
        r = MIN_R + (row["total_favs"] / max_favs) ** 0.5 * (MAX_R - MIN_R)
        points.append({
            "x":      int(row["tweet_count"]),
            "y":      int(row["total_favs"]),
            "r":      round(r, 1),
            "user":   str(row["username"]),
            "rts":    int(row["total_rts"]),
            "tweets": int(row["tweet_count"]),
        })

    bubble_data = json.dumps(points, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<title>Author Bubbles · {keyword}</title>
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
  <h1>🫧 Author Bubble Chart · {keyword}</h1>
  <div class="subtitle">Each bubble = one author. X = tweet count · Y = total likes · size = total likes. Hover to see stats.</div>
  <div class="chart-wrap">
    <canvas id="chart"></canvas>
  </div>
  <div class="footer">Byamba Enkhbat · data: X API</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const raw = {bubble_data};
const ctx = document.getElementById('chart').getContext('2d');

new Chart(ctx, {{
  type: 'bubble',
  data: {{
    datasets: [{{
      label: 'Authors',
      data: raw.map(p => ({{ x: p.x, y: p.y, r: p.r }})),
      backgroundColor: (ctx) => {{
        const y = ctx.raw ? ctx.raw.y : 0;
        const max = raw[0].y;
        const t = Math.sqrt(y / max);
        // Gradient from teal → purple → pink based on engagement
        if (t > 0.7) return '#f9188066';
        if (t > 0.4) return '#7856ff66';
        return '#1d9bf066';
      }},
      borderColor: (ctx) => {{
        const y = ctx.raw ? ctx.raw.y : 0;
        const max = raw[0].y;
        const t = Math.sqrt(y / max);
        if (t > 0.7) return '#f91880';
        if (t > 0.4) return '#7856ff';
        return '#1d9bf0';
      }},
      borderWidth: 1.5,
      hoverBorderWidth: 2.5,
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
        titleColor: '#7856ff',
        bodyColor: '#d0d8e8',
        callbacks: {{
          title: (items) => '@' + raw[items[0].dataIndex].user,
          label: (item) => [
            `❤️ ${{raw[item.dataIndex].y.toLocaleString()}} total likes`,
            `🔁 ${{raw[item.dataIndex].rts.toLocaleString()}} total retweets`,
            `✍️ ${{raw[item.dataIndex].tweets}} tweet${{raw[item.dataIndex].tweets !== 1 ? 's' : ''}}`,
          ],
        }},
      }},
    }},
    scales: {{
      x: {{
        ticks: {{ color: '#556677' }},
        grid:  {{ color: '#1e2130' }},
        title: {{ display: true, text: '✍️ Tweet Count', color: '#d0d8e8' }},
      }},
      y: {{
        ticks: {{ color: '#556677' }},
        grid:  {{ color: '#1e2130' }},
        title: {{ display: true, text: '❤️ Total Likes', color: '#f91880' }},
      }},
    }},
  }},
}});
</script>
</body>
</html>"""

    out = csv_path.with_name(f"{keyword}_bubbles.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
