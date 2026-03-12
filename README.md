# 🐦 Analysis on X

> Keyword-driven tweet collection and engagement analysis for X (Twitter), built for Mongolian-language political content — but works for any keyword.

![Top 10 report screenshot](Screenshot%202026-03-12%20160448.png)

---

## What it does

1. **Pull** — fetches up to N recent tweets matching a keyword via the X API v2 and saves them to a CSV.
2. **Top 10** — renders a dark-themed HTML card view of the 10 most-liked tweets, plus a ranked `.txt` list of authors.
3. **Summary** — measures engagement concentration: what share of total likes and retweets is captured by the Top 10 / 20 / 30 tweets, and exports a polished HTML table report.

---

## Project structure

```
analysis_on_x/
├── pull_tweets.py        # CLI: pull tweets by keyword → <keyword>.csv
├── pull_tweets.ipynb     # Interactive notebook version of the puller
├── top10.py              # CLI: generate Top 10 HTML cards + users.txt from any CSV
├── summary.py            # CLI: engagement-concentration report → <keyword>_summary.html
├── dankh_top10.py        # One-off hardcoded script (predecessor of top10.py)
│
├── данх.csv              # Sample dataset — keyword "данх"
├── dankh.csv             # Same dataset with ASCII filename
├── данх.html             # Top 10 HTML output for данх
├── данх_summary.html     # Summary HTML output for данх
├── данх_top_users.txt    # Top-10 user ranking for данх
└── dankh_top_users.txt   # Same with ASCII filename
```

---

## Requirements

| Dependency | Purpose |
|---|---|
| `tweepy` | X API v2 client |
| `pandas` | data wrangling and CSV I/O |
| `google-cloud-secret-manager` | reads the Bearer Token from GCP Secret Manager |

```bash
pip install tweepy pandas google-cloud-secret-manager
```

---

## Setup

The Bearer Token is stored securely in **GCP Secret Manager** under the secret ID `MONGOL_BEARER_TOKEN` in the `datalogichub` project. Make sure your environment has valid Application Default Credentials:

```bash
gcloud auth application-default login
```

No token is ever written to disk or committed to source control.

---

## Usage

### 1 — Pull tweets

```bash
# Fetch 500 tweets for a keyword and save to <keyword>.csv
python pull_tweets.py "данх" -n 500

# Fetch the default 50
python pull_tweets.py "Оюун-Эрдэнэ"
```

Output: `Оюун-Эрдэнэ.csv` with columns `username`, `post_text`, `posted_date`, `retweets`, `favorites`.

---

### 2 — Generate Top 10 HTML

```bash
python top10.py данх.csv
```

Produces:
- `данх.html` — dark-themed card view of the 10 most-liked tweets (medals 🥇🥈🥉)
- `данх_top_users.txt` — ranked author list

---

### 3 — Engagement summary

```bash
python summary.py данх.csv
```

Prints a concentration table to the terminal and saves `данх_summary.html`:

```
  Top    Tweet%    ❤️%     🔁%   Unique
  ---------------------------------------------
  Top 10    2.0%   34.5%   35.8%        9
  Top 20    4.0%   54.1%   57.4%       15
  Top 30    6.0%   64.9%   65.5%       20
```

The HTML report shows the same data with animated progress bars in X's brand colors (blue / pink / green) on a dark background.

---

## Sample data — "данх"

Dataset pulled **2026-03-12**, keyword `данх` (Mongolian political slang):

| Metric | Value |
|---|---|
| Total tweets | 521 |
| Total ❤️ favorites | 6,210 |
| Total 🔁 retweets | 2,282 |
| Unique authors | 259 |
| Top 10 tweets capture | **34.5 %** of all likes |

---

## Output preview

The HTML outputs use a dark `#0f1117` background that matches X's dark mode, with:
- **Blue** (`#1d9bf0`) for tweet share bars and usernames
- **Pink** (`#f91880`) for favorites
- **Green** (`#00ba7c`) for retweets

---

## Author

**Byamba Enkhbat** · data sourced from the X API via `@MongolPost`
