"""Utilities for fetching foreign exchange rates from VietcomBank."""
from datetime import datetime
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


class ExchangeRateScraper:
    """Fetch exchange rates from VietcomBank via API with web scraping fallback."""

    API_URL = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"
    WEB_URL = "https://vietcombank.com.vn/vi-VN/KHCN/Cong-cu-Tien-ich/Ty-gia"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        )

    def get_exchange_rate_api(self) -> Optional[Dict]:
        """Fetch exchange rates from the official API."""
        try:
            response = self.session.get(self.API_URL, timeout=10)
            response.raise_for_status()

            from xml.etree import ElementTree as ET

            root = ET.fromstring(response.content)

            rates = {
                "timestamp": datetime.now().isoformat(),
                "source": "API",
                "currencies": {},
            }

            for exrate in root.findall(".//Exrate"):
                currency_code = exrate.get("CurrencyCode")
                if not currency_code:
                    continue
                currency_name = exrate.get("CurrencyName", "")
                buy_rate = exrate.get("Buy", "0")
                transfer_rate = exrate.get("Transfer", "0")
                sell_rate = exrate.get("Sell", "0")

                rates["currencies"][currency_code] = {
                    "name": currency_name,
                    "buy": self._clean_rate(buy_rate),
                    "transfer": self._clean_rate(transfer_rate),
                    "sell": self._clean_rate(sell_rate),
                }

            print(f"Fetched exchange rates via API: {len(rates['currencies'])} currencies")
            return rates

        except Exception as exc:  # pragma: no cover - external dependency
            print(f"API error: {exc}")
            return None

    def get_exchange_rate_scraping(self) -> Optional[Dict]:
        """Fetch exchange rates via web scraping with Selenium (requires browser driver)."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            import time

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            
            driver.get(self.WEB_URL)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()

            rates = {
                "timestamp": datetime.now().isoformat(),
                "source": "WebScraping",
                "currencies": {},
            }

            # Try primary selector
            tbody = soup.select_one(".table-responsive tbody")
            if not tbody:
                tbody = soup.find("tbody")
            if not tbody:
                tables = soup.find_all("table")
                if tables:
                    tbody = tables[0].find("tbody")

            if tbody:
                for tr in tbody.find_all("tr"):
                    td = tr.find_all("td")
                    if len(td) >= 5:
                        currency_code = td[0].get_text(strip=True)
                        buy_cash = td[2].get_text(strip=True)
                        buy_transfer = td[3].get_text(strip=True)
                        sell = td[4].get_text(strip=True)

                        rates["currencies"][currency_code] = {
                            "buy": self._clean_rate(buy_cash),
                            "transfer": self._clean_rate(buy_transfer),
                            "sell": self._clean_rate(sell),
                        }

                print(
                    f"Fetched exchange rates via web scraping: "
                    f"{len(rates['currencies'])} currencies"
                )
                return rates

            print("Could not find the exchange rate table on the web page")
            return None

        except Exception as exc:  # pragma: no cover - external dependency
            print(f"Web scraping error: {exc}")
            return None

    def get_exchange_rate(self) -> Optional[Dict]:
        """Attempt API first, then fall back to web scraping."""
        print("Retrieving exchange rates from VietcomBank...")

        rates = self.get_exchange_rate_api()

        if not rates:
            print("API unavailable, switching to web scraping...")
            rates = self.get_exchange_rate_scraping()

        return rates

    def _clean_rate(self, rate_str: str) -> float:
        """Normalize a rate string into a float."""
        try:
            cleaned = rate_str.replace(",", "").replace(" ", "").strip()
            if cleaned and cleaned != "-":
                return float(cleaned)
            return 0.0
        except Exception:
            return 0.0

    def get_usd_rate(self) -> Optional[Dict]:
        """Return the USD/VND rate if available."""
        rates = self.get_exchange_rate()
        if rates and "USD" in rates.get("currencies", {}):
            return rates["currencies"]["USD"]
        # Fallback rate if scraping fails
        print("Warning: Unable to fetch USD rate, using default 24000 VND")
        return {"buy": 24000.0, "transfer": 24000.0, "sell": 24000.0}


if __name__ == "__main__":
    # Manual test for the exchange rate scraper
    scraper = ExchangeRateScraper()
    usd_rate = scraper.get_usd_rate()
    if usd_rate:
        print("\nUSD/VND rate:")
        print(f"  Buy: {usd_rate['buy']:,.0f} VND")
        print(f"  Transfer: {usd_rate['transfer']:,.0f} VND")
        print(f"  Sell: {usd_rate['sell']:,.0f} VND")