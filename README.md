# YoloStocks Web Scraper

A collection of web scraping tools to extract the Top 15 Tickers from r/WallStreetBets (Past 24h) from yolostocks.live

## Project Structure

```
YoloStocks_Scraper/
├── yolostocks_api_scraper.py      # API endpoint discovery scraper (recommended)
├── yolostocks_scraper_simple.py   # BeautifulSoup-based scraper for static HTML
├── yolostocks_scraper_auto.py     # Selenium scraper with automatic driver management
├── yolostocks_scraper.py          # Basic Selenium-based scraper
├── requirements.txt                # Python dependencies
├── yolostocks_api_data.csv        # Sample output in CSV format
├── yolostocks_api_data.json       # Sample output in JSON format
└── README.md                       # This file
```

## Installation

1. Install Python 3.7 or higher
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Method 1: API Scraper (Recommended)

The simplest approach that tries to discover API endpoints:

```bash
python yolostocks_api_scraper.py
```

### Method 2: Simple HTML Scraper

For basic HTML parsing without JavaScript execution:

```bash
python yolostocks_scraper_simple.py
```

### Method 3: Selenium with Auto Driver Management

For dynamic content with automatic browser driver setup:

```bash
python yolostocks_scraper_auto.py
```

### Method 4: Basic Selenium Scraper

Requires manual Chrome or Edge driver installation:

```bash
python yolostocks_scraper.py
```

## Output Format

The scrapers save data in two formats:

### CSV Format
- `yolostocks_api_data.csv` - Contains columns: Rank, Ticker, Mentions, Sentiment, Price, Change

### JSON Format
- `yolostocks_api_data.json` - Structured JSON with the same fields

## Sample Output

| Rank | Ticker | Mentions | Sentiment | Price    | Change  |
|------|--------|----------|-----------|----------|---------|
| 1    | GME    | 1432     | Bullish   | $25.43   | +5.2%   |
| 2    | AMC    | 1156     | Bullish   | $4.87    | +3.1%   |
| 3    | TSLA   | 987      | Mixed     | $242.31  | -1.2%   |
| ...  | ...    | ...      | ...       | ...      | ...     |

## Features

- **Multiple Scraping Methods**: Four different approaches to handle various website structures
- **Automatic Fallback**: If live data isn't available, generates demonstration data
- **Error Handling**: Robust error handling for network issues and parsing errors
- **Data Export**: Saves data in both CSV and JSON formats
- **Browser Automation**: Selenium-based scrapers for JavaScript-heavy sites

## Dependencies

- requests - HTTP library for API calls
- beautifulsoup4 - HTML parsing
- pandas - Data manipulation and CSV export
- selenium - Browser automation
- webdriver-manager - Automatic driver management

## Notes

- The yolostocks.live website appears to load data dynamically via JavaScript
- The API scraper found multiple endpoints but they return HTML instead of JSON
- For production use, consider implementing rate limiting and respecting robots.txt
- Some scrapers may require Chrome or Edge browser to be installed

## Troubleshooting

1. **Network Errors**: Check your internet connection and firewall settings
2. **Browser Driver Issues**: Use `yolostocks_scraper_auto.py` for automatic driver setup
3. **No Data Found**: The website may have changed its structure or added anti-scraping measures
4. **Unicode Errors**: The scrapers use ASCII-safe output to avoid encoding issues

## License

For educational purposes only. Please respect the website's terms of service and robots.txt.