#!/usr/bin/env python3
import os
import datetime
import time
import praw

# ---------- config ----------
LIMIT     = int(os.getenv("LIMIT", 6))
SUBREDDIT = os.getenv("SUBREDDIT", "your_subreddit_name")
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    user_agent=os.getenv("USER_AGENT"),
)
# ----------------------------

sub = reddit.subreddit(SUBREDDIT)
print(f"🤖  Monitoring r/{SUBREDDIT} – daily limit {LIMIT} posts/user")

today  = datetime.date.today()
counts = {}          # username -> posts today

def reset_if_midnight():
    global today, counts
    now = datetime.date.today()
    if now != today:
        counts = {}
        today  = now
        print("🕛 Midnight UTC – counters reset")

for submission in sub.stream.submissions(skip_existing=True):
    reset_if_midnight()

    author = submission.author.name if submission.author else "[deleted]"
    if author == "[deleted]":
        continue

    counts[author] = counts.get(author, 0) + 1

    if counts[author] > LIMIT:
        submission.mod.remove()
        comment = submission.reply(
            f"Hi u/{author}, you have reached the daily post limit ({LIMIT}) for r/{SUBREDDIT}. "
            "This post was removed. You can post again after midnight UTC."
        )
        comment.mod.distinguish(how="yes")
        comment.mod.lock()
        print(f"❌ Removed post {submission.id} by u/{author} (#{counts[author]})")
      
