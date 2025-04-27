import requests, pandas as pd, time
from lxml import html
from urllib.parse import urljoin
from tqdm import tqdm

BASE   = "https://knowyourmeme.com"
LIST   = f"{BASE}/categories/meme"
HDRS   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."}
SEL    = ("body > main > article > article > section"
          " > div.contents-container > div.contents"
          " > section > div:nth-child(1) > a:nth-child(odd)")

def detail_urls(list_html: str):
    tree  = html.fromstring(list_html)
    return [urljoin(BASE, a.get("href")) for a in tree.cssselect(SEL)]

def parse_detail(url: str):
    t = html.fromstring(requests.get(url, headers=HDRS, timeout=20).text)
    return {
        "title": t.xpath('normalize-space(//h1)'),
        "about": t.xpath('normalize-space(//*[@id="entry_section_about"]/p[1])'),
        "added": (t.xpath('string(//section[@id="entry_about"]//span[@class="time"]/@datetime)') or "")[:10],
        "url":   url,
    }

def crawl(pages=1, pause=1.5):
    rows = []
    for p in range(1, pages+1):
        url  = LIST if p == 1 else f"{LIST}/page/{p}"
        res  = requests.get(url, headers=HDRS, timeout=20)
        for durl in tqdm(detail_urls(res.text), desc=f"Page {p}"):
            try:
                rows.append(parse_detail(durl))
            except Exception as e:
                print("skip:", durl, e)
            time.sleep(pause)
        time.sleep(pause)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = crawl(pages=1)          # 필요하면 pages 값을 늘리세요
    df.to_csv("kym_meme.csv", index=False, encoding="utf-8-sig")
    print("saved", len(df), "rows")
