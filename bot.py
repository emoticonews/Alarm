import os, re, json, requests, feedparser

TOKEN = os.environ["TG_TOKEN"]
CHAT = os.environ["TG_CHAT_ID"]
NID = os.environ["NAVER_ID"]
NSEC = os.environ["NAVER_SECRET"]
RSS = [u for u in os.environ.get("RSS_URLS", "").split(",") if u.strip()]
QUERIES = ["카카오톡 채널 추가 이모티콘", "무료 이모티콘 채널 추가"]

def ok(t):
    return "이모티콘" in t and ("채널" in t or "무료" in t)

def clean(s):
    return re.sub(r"<[^>]+>", "", s)

try:
    seen = set(json.load(open("seen.json")))
except Exception:
    seen = set()

found = []
headers = {"X-Naver-Client-Id": NID, "X-Naver-Client-Secret": NSEC}
for kind in ("news", "blog"):
    for q in QUERIES:
        try:
            r = requests.get(
                f"https://openapi.naver.com/v1/search/{kind}.json",
                params={"query": q, "display": 20, "sort": "date"},
                headers=headers, timeout=15)
            for i in r.json().get("items", []):
                found.append((clean(i["title"]), i["link"]))
        except Exception as e:
            print("naver error", e)

for u in RSS:
    try:
        for e in feedparser.parse(u.strip()).entries:
            found.append((clean(e.title), e.link))
    except Exception as e:
        print("rss error", e)

new = []
for t, l in found:
    if l not in seen and ok(t):
        new.append((t, l))
        seen.add(l)

for t, l in new[:10]:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": f"🎁 {t}\n{l}"}, timeout=15)

json.dump(list(seen)[-2000:], open("seen.json", "w"), ensure_ascii=False)
