
import logging
from pathlib import Path
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "books.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


def fetch_page(session, url):
    """Download one webpage and return its HTML."""
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text

    except requests.RequestException as error:
        logger.error("Failed to fetch %s: %s", url, error)
        return None


def extract_books(html, page_url):
    """Extract book titles and prices from one page."""
    soup = BeautifulSoup(html, "html.parser")
    books = soup.select("article.product_pod")

    records = []

    for book in books:
        title_element = book.select_one("h3 a")
        price_element = book.select_one(".price_color")

        if title_element is None or price_element is None:
            logger.warning("A book record is missing its title or price.")
            continue

        title = title_element.get("title", "").strip()
        price_text = price_element.get_text(strip=True)
        price_text = price_text.replace("Â£", "£").replace("£", "").strip()

        records.append({
            "title": title,
            "price": price_text
        })

    next_element = soup.select_one("li.next a")
    next_url = (
        urljoin(page_url, next_element["href"])
        if next_element else None
    )

    return records, next_url


def scrape_books():
    """Scrape all catalogue pages."""
    records = []
    url = BASE_URL

    with requests.Session() as session:
        while url:
            logger.info("Scraping %s", url)

            html = fetch_page(session, url)

            if html is None:
                raise RuntimeError(
                    f"Scraping stopped because this page failed: {url}"
                )

            page_records, next_url = extract_books(html, url)

            if not page_records:
                raise RuntimeError(
                    f"No book records extracted from: {url}"
                )

            records.extend(page_records)
            url = next_url

    return pd.DataFrame(records)


def clean_data(df):
    """Normalize, validate, and review the extracted records."""
    df = df.copy()

    raw_count = len(df)

    df["title"] = df["title"].str.strip()
    df["price"] = (
        df["price"]
        .str.replace("£", "", regex=False)
        .str.strip()
    )

    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Report data quality before dropping invalid records.
    logger.info("Raw records: %d", raw_count)
    logger.info("Missing titles: %d", df["title"].isna().sum())
    logger.info("Invalid or missing prices: %d", df["price"].isna().sum())

    repeated_titles = df[
        df.duplicated(subset=["title"], keep=False)
    ]

    if not repeated_titles.empty:
        logger.warning(
            "Found %d rows with repeated titles. Review these records.",
            len(repeated_titles)
        )
        print("\nRecords requiring review:")
        print(repeated_titles.sort_values("title"))

    # Remove exact duplicate rows only.
    df = df.drop_duplicates(subset=["title", "price"])

    df = df.dropna(subset=["title", "price"])
    df = df[df["title"] != ""]
    df = df[df["price"] >= 0]

    logger.info("Final valid records: %d", len(df))

    return df



def save_data(df):
    """Create the output folder and save CSV and Excel files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # # Save CSV
    # df.to_csv(
    #     OUTPUT_DIR / "books.csv",
    #     index=False,
    #     encoding="utf-8-sig"
    # )

    # Save Excel
    df.to_excel(
        OUTPUT_DIR / "books.xlsx",
        index=False
    )

    # logger.info("CSV saved to %s", OUTPUT_DIR / "books.csv")
    logger.info("Excel saved to %s", OUTPUT_DIR / "books.xlsx")



def main():
    raw_df = scrape_books()
    clean_df = clean_data(raw_df)
    save_data(clean_df)

    print("\nFinal preview:")
    print(clean_df.head())


if __name__ == "__main__":
    main()
