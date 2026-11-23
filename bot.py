import os, re, json, requests, feedparser

TOKEN = os.environ["TG_TOKEN"]
CHAT = os.environ["TG_CHAT_ID"]
RSS = [u.strip() for u in os.environ.get("RSS_URLS", "").split(",") if u.strip()]

def ok(t):
    return "이모티콘" in t and ("채널" in t or "무료" in t)

def clean(s):
    return re.sub(r"<[^>]+>", "", s)

try:
    seen = set(json.load(open("seen.json")))
except Exception:
    seen = set()

found = []
for u in RSS:
    try:
        feed = feedparser.parse(u, agent="Mozilla/5.0")
        for e in feed.entries:
            found.append((clean(e.get("title", "")), e.get("link", "")))
    except Exception as e:
        print("rss error", u, e)

new = []
for t, l in found:
    if l and l not in seen and ok(t):
        new.append((t, l))
        seen.add(l)

for t, l in new[:10]:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": f"🎁 {t}\n{l}"}, timeout=15)

print(f"feeds={len(RSS)} items={len(found)} new={len(new)}")
json.dump(list(seen)[-2000:], open("seen.json", "w"), ensure_ascii=False)
