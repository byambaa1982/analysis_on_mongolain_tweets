#!/usr/bin/env python
# coding: utf-8

import argparse
import tweepy
import pandas as pd
from pathlib import Path
from google.cloud import secretmanager

GCP_PROJECT_ID = "datalogichub"


def get_secret(secret_id: str, project_id: str = GCP_PROJECT_ID) -> str:
    sm_client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = sm_client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def pull_tweets(keyword: str, n: int, client: tweepy.Client) -> pd.DataFrame:
    rows = []

    paginator = tweepy.Paginator(
        client.search_recent_tweets,
        query=f"{keyword} -is:retweet",
        tweet_fields=["created_at", "public_metrics", "author_id"],
        user_fields=["username"],
        expansions=["author_id"],
        max_results=100,  # max per page
    )

    for response in paginator:
        if not response.data:
            break
        users = {u.id: u.username for u in (response.includes.get("users") or [])}
        for tweet in response.data:
            metrics = tweet.public_metrics or {}
            rows.append({
                "username":    users.get(tweet.author_id, "unknown"),
                "post_text":   tweet.text,
                "posted_date": tweet.created_at,
                "retweets":    metrics.get("retweet_count", 0),
                "favorites":   metrics.get("like_count", 0),
            })
            if len(rows) >= n:
                break
        if len(rows) >= n:
            break

    df = pd.DataFrame(rows, columns=["username", "post_text", "posted_date", "retweets", "favorites"])
    df["posted_date"] = pd.to_datetime(df["posted_date"])
    return df.sort_values("favorites", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull tweets by keyword from X API")
    parser.add_argument("keyword",  type=str,            help="Search keyword or hashtag")
    parser.add_argument("-n",       type=int, default=50, help="Number of tweets to fetch (default: 50)")
    args = parser.parse_args()

    bearer_token = get_secret("MONGOL_BEARER_TOKEN")
    tweepy_v2 = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

    df = pull_tweets(args.keyword, args.n, tweepy_v2)

    out_file = Path(__file__).parent / f"{args.keyword}.csv"
    df.to_csv(out_file, index=False)
    print(f"Fetched {len(df)} tweets → {out_file}")




