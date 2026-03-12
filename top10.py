#!/usr/bin/env python
# coding: utf-8

import argparse
import pandas as pd
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate Top 10 HTML + users txt from a tweets CSV")
    parser.add_argument("csv_file", type=str, help="Input CSV file (e.g. данх.csv or Оюун-Эрдэнэ.csv)")
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).parent / csv_path

    if not csv_path.exists():
        print(f"Error: file not found → {csv_path}")
        return

    keyword   = csv_path.stem
    html_file = csv_path.with_suffix(".html")
    txt_file  = csv_path.parent / f"{keyword}_top_users.txt"

    df    = pd.read_csv(csv_path)
    top10 = df.nlargest(10, "favorites")[["username", "post_text", "favorites"]].reset_index(drop=True)

    # ── Save users txt ───────────────────────────────────────────────────────
    lines = [f"Top users · {keyword} · {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", "=" * 50]
    for i, row in top10.iterrows():
        lines.append(f"{i+1:>2}. @{row['username']:<20} ❤️  {int(row['favorites'])}")
    txt_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Users saved → {txt_file}")

    # ── Build HTML cards ─────────────────────────────────────────────────────
    cards = ""
    for i, row in top10.iterrows():
        rank  = i + 1
        text  = row["post_text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        cards += f"""
    <div class="card">
      <div class="rank">{medal}</div>
      <div class="content">
        <div class="username">@{row['username']}</div>
        <div class="text">{text}</div>
      </div>
      <div class="fav">❤️ {int(row['favorites'])}</div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0f1117;
    font-family: 'Segoe UI', sans-serif;
    padding: 20px 28px;
    width: 1000px;
  }}
  h1 {{
    color: #fff;
    font-size: 17px;
    margin-bottom: 3px;
    letter-spacing: 0.5px;
  }}
  .subtitle {{
    color: #ffffff;
    font-size: 12px;
    margin-bottom: 12px;
  }}
  .card {{
    display: flex;
    align-items: flex-start;
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 8px;
    padding: 9px 14px;
    margin-bottom: 6px;
    gap: 12px;
  }}
  .rank {{
    font-size: 18px;
    min-width: 32px;
    text-align: center;
    padding-top: 1px;
  }}
  .content {{ flex: 1; }}
  .username {{
    color: #1d9bf0;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 3px;
  }}
  .text {{
    color: #d0d8e8;
    font-size: 12px;
    line-height: 1.4;
    white-space: pre-wrap;
    word-break: break-word;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .fav {{
    font-size: 13px;
    color: #f91880;
    font-weight: 700;
    min-width: 52px;
    text-align: right;
    padding-top: 1px;
    white-space: nowrap;
  }}
  .footer {{
    color: #445566;
    font-size: 11px;
    text-align: right;
    margin-top: 10px;
  }}
</style>
</head>
<body>
  <h1>🔥 Top 10</h1>
  <div class="subtitle">"{keyword}" гэсэн түлхүүрээр хайхад хамгийн олон хандалт авсан 10 жиргээ. Гэхдээ миний database рүү татагдахаас 8 цагаас өмнө жиргэсэн жиргээнүүд ороогүй болно.</div>
  {cards}
  <div class="footer">Created By Byamba Enkhbat</div>
</body>
</html>"""

    html_file.write_text(html, encoding="utf-8")
    print(f"HTML saved  → {html_file}")


if __name__ == "__main__":
    main()
