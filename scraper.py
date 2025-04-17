import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
BASE_URL    = "https://www.shl.com"

def scrape_catalog():
    # 1) Launch headless Chrome via webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    # 2) Load page & wait for rows to appear
    driver.get(CATALOG_URL)
    try:
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "tbody tr")) > 0
        )
    except Exception:
        driver.quit()
        raise RuntimeError("Dynamic assessments table did not load in time.")

    html = driver.page_source
    driver.quit()

    # 3) Parse the rendered HTML
    soup = BeautifulSoup(html, "html.parser")
    table = None
    for tbl in soup.find_all("table"):
        if tbl.select("tbody tr"):
            table = tbl
            break
    if not table:
        raise RuntimeError("Assessments table not found on page after rendering.")

    # 4) Extract rows
    items = []
    for row in table.select("tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        # Title & URL
        a = cells[0].find("a", href=True)
        name = a.get_text(strip=True) if a else cells[0].get_text(strip=True)
        url  = urljoin(BASE_URL, a["href"]) if a else ""

        # Duration & Test type
        duration  = cells[1].get_text(strip=True)
        test_type = cells[2].get_text(strip=True)

        # Remote / Adaptive flags
        flags_text = cells[3].get_text(separator="|")
        flags = [f.strip() for f in flags_text.split("|") if f.strip()]
        remote   = "Yes" if any("Remote" in f for f in flags) else "No"
        adaptive = "Yes" if any("Adaptive" in f or "IRT" in f for f in flags) else "No"

        items.append({
            "name":          name,
            "url":           url,
            "remoteTesting": remote,
            "adaptiveIRT":   adaptive,
            "duration":      duration,
            "testType":      test_type
        })

    # 5) Save to JSON
    with open("catalog.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

    print(f"Scraped {len(items)} assessments via Selenium.")

if __name__ == "__main__":
    scrape_catalog()
