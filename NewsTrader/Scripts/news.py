"""News aggregation: Google News RSS, Tiingo, Boersen-Zeitung."""
import re
import asyncio
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from data_providers import tiingo_get_news, ALPACA_AVAILABLE


async def get_google_news(query, country_code="US"):
    """Fetch recent news via Google News RSS based on country and filter for today."""
    today = datetime.now().date()
    cc_map = {
        "DE": {"hl": "de", "gl": "DE", "ceid": "DE:de"},
        "US": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
        "GB": {"hl": "en-GB", "gl": "GB", "ceid": "GB:en"},
        "CA": {"hl": "en-CA", "gl": "CA", "ceid": "CA:en"},
        "FR": {"hl": "fr", "gl": "FR", "ceid": "FR:fr"},
        "CH": {"hl": "de-CH", "gl": "CH", "ceid": "CH:de"},
    }
    params = cc_map.get(country_code.upper(), cc_map["US"])
    hl, gl, ceid = params["hl"], params["gl"], params["ceid"]

    try:
        url = f"https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        news_items = []
        for item in root.findall(".//item"):
            pub_date_str = item.find("pubDate").text
            try:
                dt = parsedate_to_datetime(pub_date_str)
                if dt.date() != today:
                    continue
            except Exception:
                continue
            news_items.append({
                "source": f"Google News ({gl})",
                "title": item.find("title").text,
                "date": dt.strftime("%d.%m.%Y %H:%M"),
                "url": item.find("link").text,
            })
            if len(news_items) >= 20:
                break
        print(f"    Found {len(news_items)} today from Google News ({gl})")
        return news_items
    except Exception as e:
        print(f"    Google News Fetch failed ({gl}): {e}")
        return []


async def aggregate_news(asset, ticker):
    """Aggregate news internationally with clear source logging."""
    all_news = []
    asset_name = asset.get("Asset", ticker) or ""
    isin = str(asset.get("ISIN", "")).strip()

    country_code = "US"
    if len(isin) >= 2 and isin[:2].isalpha():
        country_code = isin[:2].upper()

    full_name = asset_name
    derivative_keywords = [
        "Call", "Put", "Turbo", "Zertifikat", "OS", "Warrant", "Mini",
        "Classic", "Long", "Short", "Faktor", "Discount", "Underlying",
    ]
    is_derivative = any(dk.lower() in full_name.lower() for dk in derivative_keywords)

    if is_derivative:
        words = full_name.split()
        banks = [
            "HSBC", "BNP", "DZ", "Bank", "Goldman", "Sachs", "SocGen",
            "Vontobel", "Citi", "Citigroup", "Morgan", "Stanley", "UBS",
            "J.P.", "JP", "UniCredit",
        ]
        types = derivative_keywords + ["Open", "End", "auf", "Basiswert", "Line"]
        filtered_words = []
        for w in words:
            clean_w = w.strip(",() ")
            if clean_w.isdigit() and len(clean_w) == 4:
                continue
            if clean_w.upper() in [b.upper() for b in banks]:
                continue
            if clean_w.upper() in [t.upper() for t in types]:
                continue
            if len(clean_w.replace(".", "")) < 2 and not any(c in clean_w for c in "123456789"):
                continue
            filtered_words.append(clean_w)
        if filtered_words:
            full_name = " ".join(filtered_words)
            print(f"    Derivative detected! Underlying: '{full_name}'")

    print(f"    Seek: Web Search (Google News {country_code}) for '{full_name}'...")
    query_suffix = "+stock" if country_code != "US" else ""
    if country_code == "DE":
        query_suffix = "+Aktie"
    search_query = f'"{full_name}"{query_suffix}' if len(full_name.split()) > 1 else f"{full_name}{query_suffix}"
    raw_news = await get_google_news(search_query, country_code)

    financial_keywords = [
        "stock", "market", "mining", "quarter", "revenue", "profit",
        "Aktie", "Börse", "Quartal", "Ergebnis", "News", "Dividend",
        "Price", "Kurs",
    ]
    for item in raw_news:
        if len(full_name.split()) < 2:
            if any(kw.lower() in item["title"].lower() for kw in financial_keywords):
                all_news.append(item)
        else:
            all_news.append(item)

    if raw_news:
        print(f"    Found {len(all_news)} items from Web Search")

    today_iso = datetime.now().strftime("%Y-%m-%d")
    if len(all_news) < 5:
        print(f"    Seek: Tiingo News for '{full_name}'...")
        try:
            t_news = tiingo_get_news(tickers=None, limit=50)
            found_t = 0
            if t_news and isinstance(t_news, list):
                for item in t_news:
                    if not item.get("publishedDate", "").startswith(today_iso):
                        continue
                    title = item.get("title", "")
                    if full_name.lower() in title.lower():
                        if not any(n["title"] == title for n in all_news):
                            all_news.append({
                                "source": "Tiingo",
                                "title": title,
                                "date": item.get("publishedDate"),
                                "url": item.get("url"),
                            })
                            found_t += 1
            if found_t:
                print(f"    Found {found_t} items from Tiingo")
        except Exception:
            pass

    if ALPACA_AVAILABLE and len(all_news) < 5:
        print(f"    Seek: Alpaca News for '{full_name}'...")
        pass

    if country_code == "DE" and len(all_news) < 10:
        print(f"    Seek: Boersen-Zeitung for '{full_name}'...")
        try:
            bz_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "de,en;q=0.5",
            }
            search_term = full_name.replace(" ", "+")
            bz_url = f"https://www.boersen-zeitung.de/suche?q={search_term}"
            bz_resp = await asyncio.to_thread(
                requests.get, bz_url, headers=bz_headers, timeout=10
            )
            if bz_resp.status_code == 200:
                html = bz_resp.text
                found_bz = 0
                articles = re.findall(
                    r'<a[^>]*href="(/[^"]*)"[^>]*>([^<]{20,100})</a>', html
                )
                for href, title in articles:
                    if any(skip in href.lower() for skip in ["login", "abo", "newsletter", "impressum", "datenschutz"]):
                        continue
                    if any(skip in title.lower() for skip in ["anmelden", "registrieren", "cookie"]):
                        continue
                    title_clean = title.strip()
                    if len(title_clean) > 15 and not any(n["title"] == title_clean for n in all_news):
                        all_news.append({
                            "source": "Boersen-Zeitung",
                            "title": title_clean,
                            "date": datetime.now().strftime("%d.%m.%Y"),
                            "url": f"https://www.boersen-zeitung.de{href}" if href.startswith("/") else href,
                        })
                        found_bz += 1
                        if found_bz >= 5:
                            break
                if found_bz:
                    print(f"    Found {found_bz} items from Boersen-Zeitung")
        except Exception as e:
            print(f"    Boersen-Zeitung failed: {e}")

    return {
        "news_items": all_news[:10],
        "count": len(all_news[:10]),
        "search_query": full_name,
    }
