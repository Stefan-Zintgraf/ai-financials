"""Web price search: cache and deep-dive scraping for asset prices."""
import json
import os
import asyncio
import requests
import re

import config


def load_web_price_cache():
    """Load web price source cache from disk."""
    try:
        if os.path.exists(config.WEB_PRICE_CACHE_FILE):
            with open(config.WEB_PRICE_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_web_price_cache(cache):
    """Save web price source cache to disk."""
    try:
        cache_dir = os.path.dirname(config.WEB_PRICE_CACHE_FILE)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        with open(config.WEB_PRICE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"    Cache save failed: {e}")


async def deep_dive_price_search(asset, ticker):
    """
    Searches for asset price on financial sites.
    Uses ISIN, WKN, or ticker as search term.
    """
    isin = asset.get("ISIN")
    wkn = asset.get("WKN")

    search_id = None
    if wkn and str(wkn) != "nan" and len(str(wkn)) >= 5:
        search_id = str(wkn)
        print(f"    DeepDive Search using WKN: {search_id}")
    elif isin and str(isin) != "nan":
        search_id = str(isin)
        print(f"    DeepDive Search using ISIN: {search_id}")
    else:
        return {"error": "No ISIN or WKN"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    }

    quick_urls = [
        (f"https://www.onvista.de/suche/{search_id}", "Onvista"),
        (f"https://www.ariva.de/{search_id}", "Ariva"),
        (f"https://www.comdirect.de/inf/search/all.html?SEARCH_VALUE={search_id}", "Comdirect"),
    ]

    for url, source in quick_urls:
        try:
            resp = await asyncio.to_thread(
                requests.get, url, headers=headers, timeout=8, allow_redirects=True
            )
            if resp.status_code == 200:
                html = resp.text
                brief = re.search(r"Brief.*?(\d+,\d{2,4})", html, re.IGNORECASE | re.DOTALL)
                if brief:
                    price = float(brief.group(1).replace(",", "."))
                    print(f"    {source} (Brief): {price}")
                    return {"price": price, "source": f"{source} (Brief)", "url": resp.url}
                geld = re.search(r"Geld.*?(\d+,\d{2,4})", html, re.IGNORECASE | re.DOTALL)
                if geld:
                    price = float(geld.group(1).replace(",", "."))
                    print(f"    {source} (Geld): {price}")
                    return {"price": price, "source": f"{source} (Geld)", "url": resp.url}
        except Exception:
            pass

    isin = search_id
    search_urls = []
    try:
        query = f"{isin} Kurs aktuell onvista finanzen"
        url = f"https://www.google.com/search?q={query}&num=5"
        resp = await asyncio.to_thread(requests.get, url, headers=headers, timeout=5)
        raw_links = re.findall(
            r"/url\?q=(https://www\.(?:onvista|finanzen)\.de/[^&]+)", resp.text
        )
        if not raw_links:
            raw_links = re.findall(
                r'href="(https://www\.(?:onvista|finanzen)\.de/[^"]+)"', resp.text
            )
        for l in raw_links:
            if "google" in l:
                continue
            search_urls.append(l)
    except Exception as e:
        print(f"      Search failed: {e}")

    potential_urls = [
        f"https://www.onvista.de/suche/{isin}",
        f"https://www.finanzen.net/suchergebnis?_search={isin}",
    ]
    if "DE000P" in isin or "BNP" in asset.get("Asset", ""):
        bnp_url = f"https://derivate.bnpparibas.com/product-details/{isin}/"
        if bnp_url not in search_urls:
            potential_urls.append(bnp_url)

    urls_to_check = search_urls + [u for u in potential_urls if u not in search_urls]

    for link in urls_to_check[:5]:
        print(f"    Inspecting: {link}")
        try:
            page_resp = await asyncio.to_thread(
                requests.get, link, headers=headers, timeout=5
            )
            if page_resp.status_code != 200:
                continue
            html = page_resp.text

            if "onvista.de" in link:
                match = re.search(r"Brief.*?(\d+,\d{2})", html, re.IGNORECASE | re.DOTALL)
                if match:
                    return {
                        "price": float(match.group(1).replace(",", ".")),
                        "source": "Onvista (Brief)",
                        "url": link,
                    }
                match = re.search(r"Geld.*?(\d+,\d{2})", html, re.IGNORECASE | re.DOTALL)
                if match:
                    return {
                        "price": float(match.group(1).replace(",", ".")),
                        "source": "Onvista (Geld)",
                        "url": link,
                    }
                match = re.search(r'itemprop="price"[^>]*content="([\d\.]+)"', html)
                if match:
                    return {"price": float(match.group(1)), "source": "Onvista (Meta)", "url": link}
                match = re.search(
                    r'value="([\d\.]+)"[^>]*class="[^"]*price[^"]*"', html
                )
                if match:
                    return {"price": float(match.group(1)), "source": "Onvista (Data)", "url": link}

            elif "finanzen.net" in link:
                match = re.search(r'itemprop="price"[^>]*content="([\d\.]+)"', html)
                if match:
                    return {"price": float(match.group(1)), "source": "Finanzen.net", "url": link}
                match = re.search(r'col-price"[^>]*>([\d,]+)', html)
                if match:
                    return {
                        "price": float(match.group(1).replace(",", ".")),
                        "source": "Finanzen.net (Table)",
                        "url": link,
                    }

            if "bnpparibas" in link:
                match = re.search(r'itemprop="price"[^>]*content="([\d\.]+)"', html)
                if match:
                    return {"price": float(match.group(1)), "source": "BNP (Meta)", "url": link}
                match = re.search(
                    r'"(?:ask|offer|price|kaufen)"\s*[:=]\s*"?([\d\.]+)"?',
                    html,
                    re.IGNORECASE,
                )
                if match:
                    return {"price": float(match.group(1)), "source": "BNP (JSON)", "url": link}
                match = re.search(
                    r"Kaufen.*?(\d+,\d{2})", html, re.DOTALL | re.IGNORECASE
                )
                if match:
                    return {
                        "price": float(match.group(1).replace(",", ".")),
                        "source": "BNP (Text Kaufen)",
                        "url": link,
                    }
                match = re.search(
                    r"Brief.*?(\d+,\d{2})", html, re.DOTALL | re.IGNORECASE
                )
                if match:
                    return {
                        "price": float(match.group(1).replace(",", ".")),
                        "source": "BNP (Text Brief)",
                        "url": link,
                    }
        except Exception:
            pass

    print("    Google Search Fallback for price...")
    asset_name = asset.get("Asset", "")
    search_queries = [
        f"{isin} Kurs EUR",
        f"{isin} aktueller Preis",
        f'"{asset_name}" Kurs aktuell',
    ]

    for search_query in search_queries:
        try:
            url = f"https://www.google.com/search?q={search_query}"
            resp = await asyncio.to_thread(requests.get, url, headers=headers, timeout=5)
            html = resp.text
            match = re.search(r'data-last-price="([\d\.]+)"', html)
            if match:
                price = float(match.group(1))
                print(f"    Google Finance: {price}")
                return {"price": price, "source": "Google Finance", "url": url}
            match = re.search(r">(\d+[,\.]\d{2})\s*(?:€|EUR)<", html)
            if match:
                price = float(match.group(1).replace(",", "."))
                print(f"    Google Search (EUR): {price}")
                return {"price": price, "source": "Google Search", "url": url}
            match = re.search(
                r"(?:Kurs|Preis|Price|Aktuell)[:\s]+(\d+[,\.]\d{2})",
                html,
                re.IGNORECASE,
            )
            if match:
                price = float(match.group(1).replace(",", "."))
                print(f"    Google Search (Kurs): {price}")
                return {"price": price, "source": "Google Search", "url": url}
            match = re.search(r"(\d{1,4}[,\.]\d{2})\s*(?:€|EUR|Euro)", html)
            if match:
                price = float(match.group(1).replace(",", "."))
                if 0.01 <= price <= 10000:
                    print(f"    Google Search (Generic): {price}")
                    return {"price": price, "source": "Google Search", "url": url}
        except Exception:
            pass

    fallback_sites = [
        f"https://www.wallstreet-online.de/suche?q={isin}",
        f"https://www.ariva.de/quote/simple.m?secu={isin}",
        f"https://www.boerse.de/suche/?search={isin}",
        f"https://www.comdirect.de/inf/search/all.html?SEARCH_VALUE={isin}",
        f"https://www.finanzen100.de/suche/?q={isin}",
    ]

    for site_url in fallback_sites:
        try:
            print(f"    Fallback: {site_url.split('/')[2]}")
            resp = await asyncio.to_thread(requests.get, site_url, headers=headers, timeout=5)
            html = resp.text
            for pattern in [
                r'itemprop="price"[^>]*content="([\d\.]+)"',
                r'class="[^"]*price[^"]*"[^>]*>([\d,\.]+)',
                r">(\d+[,\.]\d{2})\s*(?:€|EUR)<",
                r"Kurs[:\s]+(\d+[,\.]\d{2})",
            ]:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(",", ".")
                    price = float(price_str)
                    if 0.01 <= price <= 10000:
                        source = site_url.split("/")[2].replace("www.", "")
                        print(f"    {source}: {price}")
                        return {"price": price, "source": source, "url": site_url}
        except Exception:
            pass

    return {"error": "No info"}
