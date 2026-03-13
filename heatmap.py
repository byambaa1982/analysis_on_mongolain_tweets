#!/usr/bin/env python
# coding: utf-8

import argparse
import pandas as pd
from pathlib import Path

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main():
    parser = argparse.ArgumentParser(description="Tweet volume heatmap (hour × day) from CSV")
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

    df["hour"] = df["posted_date"].dt.hour
    df["dow"]  = df["posted_date"].dt.dayofweek  # 0=Mon, 6=Sun

    pivot = df.groupby(["hour", "dow"]).size().unstack(fill_value=0)
    for d in range(7):
        if d not in pivot.columns:
            pivot[d] = 0
    pivot = pivot[sorted(pivot.columns)]

    max_val = pivot.values.max() or 1

    # Build table rows
    rows_html = ""
    for h in range(24):
        row = f'<tr><td class="hour-label">{h:02d}:00</td>'
        for d in range(7):
            val = int(pivot.loc[h, d]) if h in pivot.index else 0
            alpha = 0.06 + (val / max_val) * 0.94
            display = str(val) if val else ""
            row += (
                f'<td class="cell" style="background:rgba(29,155,240,{alpha:.2f})" '
                f'title="{val} tweets">{display}</td>'
            )
        row += "</tr>"
        rows_html += row

    header = "<tr><th></th>" + "".join(f"<th>{d}</th>" for d in DAYS) + "</tr>"

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<title>Heatmap · {keyword}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f1117; font-family: 'Segoe UI', sans-serif; padding: 28px; color: #d0d8e8; }}
  h1 {{ color: #fff; font-size: 18px; margin-bottom: 4px; letter-spacing: 0.5px; }}
  .subtitle {{ color: #556677; font-size: 12px; margin-bottom: 24px; }}
  .wrap {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px; padding: 24px; display: inline-block; }}
  table {{ border-collapse: collapse; }}
  th {{
    color: #1d9bf0; font-size: 12px; font-weight: 600;
    padding: 4px 10px; text-align: center;
  }}
  td.hour-label {{
    color: #556677; font-size: 11px;
    padding: 3px 12px 3px 0; text-align: right; white-space: nowrap;
  }}
  td.cell {{
    width: 48px; height: 26px; text-align: center;
    font-size: 10px; color: #ffffffcc;
    border: 1px solid #0f1117; border-radius: 3px;
    cursor: default; transition: opacity 0.15s;
  }}
  td.cell:hover {{ outline: 1px solid #1d9bf0; }}
  .legend {{ display: flex; align-items: center; gap: 8px; margin-top: 16px; font-size: 11px; color: #556677; }}
  .legend-bar {{
    width: 160px; height: 10px; border-radius: 4px;
    background: linear-gradient(to right, rgba(29,155,240,0.06), rgba(29,155,240,1));
  }}
  .footer {{ color: #445566; font-size: 11px; text-align: right; margin-top: 14px; }}
</style>
</head>
<body>
  <h1>🗓️ Tweet Volume Heatmap · {keyword}</h1>
  <div class="subtitle">Tweet count by hour (Ulaanbaatar time, UTC+8) × day of week — darker = more tweets</div>
  <div class="wrap">
    <table>
      {header}
      {rows_html}
    </table>
    <div class="legend">
      <span>Low</span>
      <div class="legend-bar"></div>
      <span>High ({int(max_val)} tweets)</span>
    </div>
  </div>
  <div class="footer">Byamba Enkhbat · data: X API</div>
</body>
</html>"""

    out = csv_path.with_name(f"{keyword}_heatmap.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
