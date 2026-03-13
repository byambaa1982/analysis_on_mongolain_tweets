#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import re
import pandas as pd
from pathlib import Path
from collections import Counter

# Common noise words to suppress (Mongolian + English)
STOPWORDS = {
    # English
    "the", "a", "an", "is", "in", "of", "to", "and", "or", "for", "on", "at",
    "be", "was", "are", "this", "that", "with", "from", "by", "it", "as",
    "not", "but", "have", "has", "he", "she", "they", "we", "i", "you",
    "me", "my", "your", "his", "her", "our", "their", "https", "co", "http",
    # Mongolian functional words (romanised in unicode)
    "нь", "бол", "болон", "гэж", "гэсэн", "энэ", "тэр", "байна", "байгаа",
    "гэх", "харин", "мөн", "юм", "дээр", "руу", "ийм", "болох", "байх",
    "дотор", "гэдэг", "хийж", "хэлж", "хэлсэн", "байсан", "гэхэд",
}


def tokenise(text: str) -> list:
    text = re.sub(r"http\S+", "", text)            # strip URLs
    text = re.sub(r"@\S+", "", text)               # strip @mentions
    text = re.sub(r"#(\S+)", r"\1", text)          # keep hashtag text
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return [
        t for t in text.lower().split()
        if len(t) > 2 and t not in STOPWORDS and not t.isdigit()
    ]


def main():
    parser = argparse.ArgumentParser(description="Word cloud HTML from tweet CSV")
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

    tokens: list = []
    for text in df["post_text"].dropna():
        tokens.extend(tokenise(str(text)))

    counts = Counter(tokens).most_common(150)
    word_data = json.dumps([[w, c] for w, c in counts], ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="mn">
<head>
<meta charset="UTF-8">
<title>Word Cloud · {keyword}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f1117; font-family: 'Segoe UI', sans-serif; padding: 28px; color: #d0d8e8; }}
  h1 {{ color: #fff; font-size: 18px; margin-bottom: 4px; letter-spacing: 0.5px; }}
  .subtitle {{ color: #556677; font-size: 12px; margin-bottom: 24px; }}
  #cloud {{
    width: 960px; height: 520px;
    background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px;
  }}
  .footer {{ color: #445566; font-size: 11px; text-align: right; margin-top: 14px; }}
</style>
</head>
<body>
  <h1>☁️ Word Cloud · {keyword}</h1>
  <div class="subtitle">Most frequent words across all tweets — URLs, mentions and stopwords removed</div>
  <canvas id="cloud"></canvas>
  <div class="footer">Byamba Enkhbat · data: X API</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/wordcloud2.js/1.2.2/wordcloud2.min.js"></script>
<script>
const palette = ['#1d9bf0','#f91880','#00ba7c','#ffad1f','#7856ff','#ff6b6b','#4ecdc4','#a8edea'];
WordCloud(document.getElementById('cloud'), {{
  list: {word_data},
  gridSize: 10,
  weightFactor: s => Math.max(10, Math.sqrt(s) * 7),
  fontFamily: "'Segoe UI', sans-serif",
  color: () => palette[Math.floor(Math.random() * palette.length)],
  rotateRatio: 0.25,
  minSize: 8,
  backgroundColor: '#1a1d27',
  shrinkToFit: true,
  drawOutOfBound: false,
}});
</script>
</body>
</html>"""

    out = csv_path.with_name(f"{keyword}_wordcloud.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
