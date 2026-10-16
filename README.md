
# Automated Book Data Scraper

## Overview
A Python web scraping project that extracts book titles
and prices from the Books to Scrape practice website.

## Features
- Extracts data across multiple pages
- Parses HTML using BeautifulSoup
- Cleans and validates extracted prices
- Identifies repeated titles for manual review
- Removes exact duplicate records
- Exports cleaned data to CSV
- Logs scraping progress and errors

## Tech Stack
- Python
- Requests
- BeautifulSoup
- Pandas

## Installation

Create and activate a virtual environment, then run:

```bash
python -m pip install -r requirements.txt
```

## Run the Project

```bash
python scraper.py
```

## Output
The cleaned dataset is saved to:

`output/books.csv`

## Data Quality
The script checks missing values, invalid prices,
and repeated titles.

## Limitations
- Depends on the source website's HTML structure.
- Network failures can interrupt scraping.
- Repeated titles require review because different
  prices may represent different listings.

## Data Source
https://books.toscrape.com/

This is a learning project using a practice website.
