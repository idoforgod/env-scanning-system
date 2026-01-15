#!/usr/bin/env python3
"""
Google News URL Collector v4 (Source of Truth compliant)
Only collects URLs, no content fetching.
"""

import json
import random
import time
from datetime import datetime

import feedparser
import requests


class GoogleNewsURLCollector:
    """Collects URLs from Google News RSS feeds"""

    STEEPS_KEYWORDS = {
        "Technological": [
            "artificial intelligence 2026",
            "AI breakthrough",
            "quantum computing",
            "quantum technology",
            "robotics advancement",
            "semiconductor technology",
        ],
        "Environmental": [
            "climate policy",
            "carbon neutrality",
            "renewable energy",
            "climate change action",
            "net zero emissions",
            "sustainability innovation",
        ],
        "Economic": [
            "cryptocurrency regulation",
            "digital currency",
            "global economy 2026",
            "trade policy",
            "economic reform",
            "startup funding",
        ],
        "Social": [
            "future of work",
            "automation jobs",
            "population crisis",
            "mental health policy",
            "aging society",
            "Gen Z trends",
        ],
        "Political": [
            "geopolitical tension",
            "election 2026",
            "policy reform",
            "international sanctions",
            "diplomatic relations",
            "government regulation",
        ],
        "Spiritual": [
            "mindfulness wellness",
            "ethical AI",
            "meditation industry",
            "wellness technology",
            "spiritual technology",
            "conscious capitalism",
        ],
    }

    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, delay: float = 2.0, max_per_keyword: int = 3):
        self.delay = delay
        self.max_per_keyword = max_per_keyword
        self.collected_urls = []

    def get_rss_url(self, keyword: str, country: str = "US") -> str:
        """Generate Google News RSS URL for keyword"""
        lang_map = {"US": "en-US", "KR": "ko-KR", "GB": "en-GB", "JP": "ja-JP"}
        lang = lang_map.get(country, "en-US")

        # URL encode keyword
        import urllib.parse

        encoded = urllib.parse.quote(keyword)

        return (
            f"https://news.google.com/rss/search?q={encoded}&hl={lang}&gl={country}&ceid={country}:{lang.split('-')[0]}"
        )

    def fetch_urls_for_keyword(self, keyword: str, category: str) -> list[dict]:
        """Fetch URLs from Google News for a single keyword"""
        rss_url = self.get_rss_url(keyword)
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}

        try:
            # Use feedparser with custom headers
            response = requests.get(rss_url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)

            urls = []
            for entry in feed.entries[: self.max_per_keyword]:
                url_data = {
                    "url": entry.link if hasattr(entry, "link") else entry.id,
                    "title": entry.title,
                    "keyword": keyword,
                    "category": category,
                    "discovered_at": datetime.now().isoformat(),
                }
                urls.append(url_data)
                print(f"  ✓ [{category}] {entry.title[:60]}...")

            return urls

        except Exception as e:
            print(f"  ✗ Error fetching {keyword}: {e}")
            return []

    def collect_all_urls(self) -> list[dict]:
        """Collect URLs for all STEEPS categories"""
        all_urls = []

        print("\n🔍 Google News URL Collection Started")
        print(f"   Target: {len(self.STEEPS_KEYWORDS)} categories")
        print(f"   Max per keyword: {self.max_per_keyword}")
        print(f"   Delay: {self.delay}s\n")

        for category, keywords in self.STEEPS_KEYWORDS.items():
            print(f"📰 {category}")

            for keyword in keywords:
                urls = self.fetch_urls_for_keyword(keyword, category)
                all_urls.extend(urls)

                # Rate limiting
                time.sleep(self.delay)

            print()

        # Deduplicate by URL
        seen_urls = set()
        unique_urls = []
        for url_data in all_urls:
            if url_data["url"] not in seen_urls:
                seen_urls.add(url_data["url"])
                unique_urls.append(url_data)

        print(f"✓ Total URLs collected: {len(all_urls)}")
        print(f"✓ Unique URLs: {len(unique_urls)}")

        return unique_urls

    def save_results(self, urls: list[dict], output_path: str):
        """Save collected URLs to JSON file"""
        output = {
            "source": "google-news",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "total_urls": len(urls),
            "by_category": {},
            "urls": urls,
        }

        # Count by category
        for url_data in urls:
            cat = url_data["category"]
            output["by_category"][cat] = output["by_category"].get(cat, 0) + 1

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Saved to: {output_path}")
        print(f"   Categories: {output['by_category']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Google News URL Collector v4")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")
    parser.add_argument("--max-per-keyword", type=int, default=3, help="Max URLs per keyword")
    parser.add_argument("--output", type=str, required=True, help="Output JSON file path")

    args = parser.parse_args()

    collector = GoogleNewsURLCollector(delay=args.delay, max_per_keyword=args.max_per_keyword)

    urls = collector.collect_all_urls()

    if len(urls) >= 15:
        collector.save_results(urls, args.output)
        print(f"\n✅ SUCCESS: Collected {len(urls)} URLs (minimum 15 required)")
        return 0
    else:
        print(f"\n❌ FAILED: Only collected {len(urls)} URLs (minimum 15 required)")
        return 1


if __name__ == "__main__":
    exit(main())
