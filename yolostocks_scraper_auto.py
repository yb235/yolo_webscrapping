"""
YoloStocks.live Web Scraper with Automatic Driver Management
Extracts Top 15 Tickers from r/WallStreetBets (Past 24h)
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.service import Service as EdgeService
import pandas as pd
import re

def setup_driver():
    """Setup WebDriver with automatic driver management"""
    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Try Chrome first
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Using Chrome browser")
    except Exception as e:
        print(f"Chrome setup failed: {e}")
        print("Trying Edge browser...")
        
        # Try Edge as fallback
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument('--headless')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--window-size=1920,1080')
        
        try:
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
            print("Using Edge browser")
        except Exception as e:
            print(f"Edge setup also failed: {e}")
            raise Exception("Could not setup any browser driver")
    
    return driver

def scrape_yolostocks():
    """
    Scrapes the Top 15 tickers from yolostocks.live
    Returns a list of dictionaries with ticker data
    """
    
    driver = setup_driver()
    
    try:
        print(f"\nFetching data from yolostocks.live at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        driver.get("https://yolostocks.live/")
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)  # Initial wait for dynamic content
        
        wait = WebDriverWait(driver, 15)
        
        # Get page source for debugging
        page_source = driver.page_source
        
        # Try to find the table containing WSB data
        print("Looking for ticker data...")
        
        # Strategy 1: Look for table elements
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} table elements")
        
        tickers_data = []
        
        if tables:
            for i, table in enumerate(tables):
                print(f"Processing table {i+1}...")
                
                # Try to get rows
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows[:16]:  # Header + top 15
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        cells = row.find_elements(By.TAG_NAME, "th")
                    
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        if any(row_data):  # Skip empty rows
                            tickers_data.append(row_data)
                
                if tickers_data:
                    print(f"Extracted {len(tickers_data)} rows from table {i+1}")
                    break
        
        # Strategy 2: Look for specific class names or IDs
        if not tickers_data:
            print("No table found. Looking for ticker elements by class...")
            
            # Common class patterns for ticker tables
            class_patterns = [
                "ticker-table",
                "wsb-table",
                "stocks-table",
                "data-table",
                "MuiTable",
                "ag-theme",
                "rt-table"
            ]
            
            for pattern in class_patterns:
                elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{pattern}')]")
                if elements:
                    print(f"Found elements with class containing '{pattern}'")
                    break
        
        # Strategy 3: Look for ticker symbols directly
        if not tickers_data:
            print("Looking for ticker symbols in the page...")
            
            # Get all text content
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for patterns that match stock tickers with associated data
            lines = body_text.split('\n')
            
            # Filter lines that look like they contain tickers
            ticker_lines = []
            for line in lines:
                # Look for lines with uppercase letters (potential tickers)
                if re.search(r'\b[A-Z]{1,5}\b', line):
                    # Exclude common non-ticker words
                    exclude = ['HTML', 'CSS', 'API', 'JSON', 'GET', 'POST', 'HTTP', 'HTTPS']
                    if not any(word in line for word in exclude):
                        ticker_lines.append(line)
            
            # Process ticker lines
            for line in ticker_lines[:15]:
                # Extract ticker symbol
                ticker_match = re.search(r'\b([A-Z]{1,5})\b', line)
                if ticker_match:
                    ticker = ticker_match.group(1)
                    
                    # Try to extract numbers (mentions, price, etc.)
                    numbers = re.findall(r'\d+\.?\d*', line)
                    
                    row_data = [ticker] + numbers[:5]  # Ticker + up to 5 numeric values
                    tickers_data.append(row_data)
            
            if tickers_data:
                print(f"Extracted {len(tickers_data)} potential ticker entries")
        
        # Strategy 4: Wait longer and retry
        if not tickers_data:
            print("Waiting additional time for dynamic content...")
            time.sleep(5)
            
            # Try to click any "load more" or "show data" buttons
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['load', 'show', 'view', 'refresh']):
                        print(f"Clicking button: {button.text}")
                        button.click()
                        time.sleep(3)
                        break
            except:
                pass
            
            # Retry table search
            tables = driver.find_elements(By.TAG_NAME, "table")
            if tables:
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows[:16]:
                        cells = row.find_elements(By.XPATH, ".//td | .//th")
                        if cells:
                            row_data = [cell.text.strip() for cell in cells]
                            if any(row_data):
                                tickers_data.append(row_data)
                    if tickers_data:
                        break
        
        # Process and structure the data
        if tickers_data:
            print(f"\nProcessing {len(tickers_data)} rows of data...")
            
            # Determine if first row is headers
            headers = []
            data_rows = tickers_data
            
            first_row = tickers_data[0] if tickers_data else []
            if first_row and all(not re.search(r'\d', str(cell)) for cell in first_row[:2]):
                headers = first_row
                data_rows = tickers_data[1:]
                print(f"Headers detected: {headers}")
            
            # Create structured result
            result = []
            for i, row in enumerate(data_rows[:15], 1):
                if headers and len(headers) >= len(row):
                    ticker_dict = {}
                    for j, header in enumerate(headers):
                        if j < len(row):
                            ticker_dict[header] = row[j]
                else:
                    # Default structure based on typical WSB data
                    ticker_dict = {
                        'Rank': str(i),
                        'Ticker': row[0] if row else '',
                        'Mentions': row[1] if len(row) > 1 else '',
                        'Sentiment': row[2] if len(row) > 2 else '',
                        'Price': row[3] if len(row) > 3 else '',
                        'Change %': row[4] if len(row) > 4 else '',
                        'Volume': row[5] if len(row) > 5 else ''
                    }
                
                # Only add if we have at least a ticker
                if ticker_dict.get('Ticker') or (row and row[0]):
                    result.append(ticker_dict)
            
            return result
        else:
            print("\nNo ticker data could be extracted")
            print("The website might be using advanced anti-scraping measures or require authentication")
            
            # Save page source for debugging
            with open('yolostocks_page_source.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("Page source saved to 'yolostocks_page_source.html' for debugging")
            
            return []
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
    
    finally:
        driver.quit()
        print("Browser closed")

def save_data(data):
    """Save data to CSV and JSON files"""
    if not data:
        print("No data to save")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    csv_file = 'yolostocks_top15_tickers.csv'
    df.to_csv(csv_file, index=False)
    print(f"✓ Data saved to {csv_file}")
    
    # Save to JSON
    json_file = 'yolostocks_top15_tickers.json'
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Data saved to {json_file}")
    
    return df

def main():
    """Main function"""
    print("=" * 60)
    print("YoloStocks.live Web Scraper")
    print("Top 15 Tickers from r/WallStreetBets (Past 24h)")
    print("=" * 60)
    
    # Scrape the data
    tickers_data = scrape_yolostocks()
    
    if tickers_data:
        print(f"\n✓ Successfully scraped {len(tickers_data)} tickers")
        print("\n" + "=" * 60)
        print("EXTRACTED DATA:")
        print("=" * 60)
        
        # Display the data
        for i, ticker in enumerate(tickers_data, 1):
            print(f"\n{i}. {ticker}")
        
        # Save the data
        print("\n" + "=" * 60)
        print("SAVING DATA...")
        print("=" * 60)
        
        df = save_data(tickers_data)
        
        if df is not None:
            print("\n" + "=" * 60)
            print("DATA SUMMARY:")
            print("=" * 60)
            print(df.to_string())
    else:
        print("\n✗ Failed to scrape data")
        print("Possible reasons:")
        print("1. The website structure has changed")
        print("2. JavaScript rendering issues")
        print("3. Anti-scraping measures")
        print("4. Network or authentication issues")
        print("\nCheck 'yolostocks_page_source.html' for the actual page content")

if __name__ == "__main__":
    main()