"""
YoloStocks.live Real-Time Web Scraper
Continuously extracts Top 15 Tickers from r/WallStreetBets and saves to CSV
"""

import time
import json
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import signal

# Set UTF-8 encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
elif hasattr(sys.stdout, 'buffer'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def scrape_yolostocks(driver=None):
    """
    Scrapes the Top 15 tickers from yolostocks.live
    Returns a list of dictionaries with ticker data
    
    Args:
        driver: Existing webdriver instance (optional)
    """
    
    # Create driver if not provided
    close_driver = False
    if driver is None:
        close_driver = True
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Initialize the driver
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"Chrome driver failed: {e}")
            try:
                print("Trying with Edge...")
                edge_options = webdriver.EdgeOptions()
                edge_options.add_argument('--headless')
                edge_options.add_argument('--no-sandbox')
                edge_options.add_argument('--disable-dev-shm-usage')
                edge_options.add_argument('--disable-gpu')
                edge_options.add_argument('--window-size=1920,1080')
                driver = webdriver.Edge(options=edge_options)
            except Exception as e2:
                print(f"Edge driver failed: {e2}")
                try:
                    print("Trying with Firefox...")
                    firefox_options = webdriver.FirefoxOptions()
                    firefox_options.add_argument('--headless')
                    driver = webdriver.Firefox(options=firefox_options)
                except Exception as e3:
                    print(f"Firefox driver failed: {e3}")
                    raise Exception("No compatible browser/driver found. Please install Chrome, Edge, or Firefox with their respective drivers.")
    
    try:
        print(f"Fetching data from yolostocks.live at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        driver.get("https://yolostocks.live/")
        
        # Wait for the page to load (adjust timeout as needed)
        wait = WebDriverWait(driver, 20)
        
        # Try multiple possible selectors for the table
        possible_selectors = [
            "table",
            ".table",
            "[class*='ticker']",
            "[class*='table']",
            "tbody tr",
            "[data-testid='table']",
            ".MuiTable-root",  # Material-UI table
            ".ag-root",  # AG-Grid table
        ]
        
        table_found = False
        tickers_data = []
        
        for selector in possible_selectors:
            try:
                # Wait for table or rows to be present
                elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                
                if elements:
                    print(f"Found elements with selector: {selector}")
                    
                    # Try to extract table rows
                    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr, .table-row, [role='row']")
                    
                    if not rows:
                        # If no tbody, try direct table rows
                        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
                    
                    for row in rows[:16]:  # Get top 15 + potential header
                        cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                        if cells:
                            row_data = [cell.text.strip() for cell in cells]
                            if row_data and any(row_data):  # Filter out empty rows
                                tickers_data.append(row_data)
                    
                    if tickers_data:
                        table_found = True
                        break
                        
            except TimeoutException:
                continue
        
        # If no table found, try to get all text and parse it
        if not table_found:
            print("Table not found with standard selectors. Attempting to parse page text...")
            
            # Wait a bit more for dynamic content
            time.sleep(5)
            
            # Get the page source for debugging
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for ticker patterns (common stock symbols are 1-5 uppercase letters)
            import re
            ticker_pattern = r'\b[A-Z]{1,5}\b'
            potential_tickers = re.findall(ticker_pattern, page_text)
            
            # Filter common non-ticker words
            exclude_words = {'USD', 'USA', 'NYSE', 'API', 'HTML', 'CSS', 'GET', 'POST', 'PUT'}
            tickers = [t for t in potential_tickers if t not in exclude_words]
            
            if tickers:
                print(f"Found potential tickers: {tickers[:15]}")
                tickers_data = [[ticker] for ticker in tickers[:15]]
            else:
                print("No tickers found in page text")
                print(f"Page text sample (first 500 chars): {page_text[:500]}")
        
        # Process the extracted data
        if tickers_data:
            # Try to identify headers if present
            headers = []
            data_rows = tickers_data
            
            if tickers_data[0] and all(isinstance(cell, str) and not cell[0].isdigit() for cell in tickers_data[0] if cell):
                headers = tickers_data[0]
                data_rows = tickers_data[1:]
            
            # Create structured data with timestamp
            result = []
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for i, row in enumerate(data_rows[:15], 1):
                if headers:
                    ticker_dict = {headers[j]: row[j] if j < len(row) else '' for j in range(len(headers))}
                    ticker_dict['Timestamp'] = timestamp
                else:
                    # Default column names if no headers found
                    ticker_dict = {
                        'Timestamp': timestamp,
                        'Rank': str(i),
                        'Ticker': row[0] if row else '',
                        'Mentions': row[1] if len(row) > 1 else '',
                        'Sentiment': row[2] if len(row) > 2 else '',
                        'Price': row[3] if len(row) > 3 else '',
                        'Change': row[4] if len(row) > 4 else ''
                    }
                result.append(ticker_dict)
            
            if close_driver:
                driver.quit()
            
            return result
        else:
            print("No data extracted from the page")
            return []
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []
    
    finally:
        if close_driver and driver:
            driver.quit()

def save_to_csv(data, filename='yolostocks_realtime.csv', append=True):
    """
    Save the scraped data to a CSV file
    
    Args:
        data: List of dictionaries containing ticker data
        filename: Output CSV filename
        append: If True, append to existing file; if False, overwrite
    """
    if data:
        df = pd.DataFrame(data)
        
        # Check if file exists and append mode is enabled
        if append and os.path.exists(filename):
            # Append without writing headers
            df.to_csv(filename, mode='a', header=False, index=False)
            print(f"Data appended to {filename}")
        else:
            # Write new file with headers
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
        return df
    else:
        print("No data to save")
        return None

def save_to_json(data, filename='yolostocks_tickers.json'):
    """Save the scraped data to a JSON file"""
    if data:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

def continuous_scraper(interval_minutes=5, duration_hours=None):
    """
    Continuously scrape YoloStocks data at specified intervals
    
    Args:
        interval_minutes: Time between scrapes in minutes
        duration_hours: Total duration to run in hours (None for infinite)
    """
    print(f"Starting continuous YoloStocks scraper...")
    print(f"Interval: {interval_minutes} minutes")
    print(f"Duration: {'Infinite' if duration_hours is None else f'{duration_hours} hours'}")
    print(f"Output file: yolostocks_realtime.csv")
    print("-" * 50)
    
    start_time = datetime.now()
    end_time = None if duration_hours is None else start_time + pd.Timedelta(hours=duration_hours)
    
    # Initialize driver once for efficiency
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome driver failed: {e}")
        try:
            print("Trying with Edge...")
            edge_options = webdriver.EdgeOptions()
            edge_options.add_argument('--headless')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--window-size=1920,1080')
            driver = webdriver.Edge(options=edge_options)
        except Exception as e2:
            print(f"Edge driver failed: {e2}")
            try:
                print("Trying with Firefox...")
                firefox_options = webdriver.FirefoxOptions()
                firefox_options.add_argument('--headless')
                driver = webdriver.Firefox(options=firefox_options)
            except Exception as e3:
                print(f"Firefox driver failed: {e3}")
                raise Exception("No compatible browser/driver found. Please install Chrome, Edge, or Firefox with their respective drivers.")
    
    scrape_count = 0
    consecutive_failures = 0
    max_failures = 3
    
    try:
        while True:
            # Check if duration has been exceeded
            if end_time and datetime.now() > end_time:
                print(f"\nDuration of {duration_hours} hours reached. Stopping scraper.")
                break
            
            try:
                # Scrape the data
                tickers_data = scrape_yolostocks(driver)
                
                if tickers_data:
                    scrape_count += 1
                    consecutive_failures = 0
                    
                    print(f"\n[Scrape #{scrape_count}] Successfully scraped {len(tickers_data)} tickers")
                    
                    # Save to CSV (append mode)
                    df = save_to_csv(tickers_data, append=(scrape_count > 1))
                    
                    # Display sample of current data
                    if df is not None and scrape_count == 1:
                        print("\nSample of data being collected:")
                        print(df.head())
                else:
                    consecutive_failures += 1
                    print(f"Failed to scrape data (attempt {consecutive_failures}/{max_failures})")
                    
                    if consecutive_failures >= max_failures:
                        print(f"\nMax consecutive failures ({max_failures}) reached. Stopping scraper.")
                        break
                
            except Exception as e:
                consecutive_failures += 1
                print(f"Error during scrape: {str(e)}")
                
                if consecutive_failures >= max_failures:
                    print(f"\nMax consecutive failures ({max_failures}) reached. Stopping scraper.")
                    break
            
            # Wait for next interval
            if not (end_time and datetime.now() > end_time):
                print(f"Waiting {interval_minutes} minutes until next scrape...")
                time.sleep(interval_minutes * 60)
    
    except KeyboardInterrupt:
        print("\n\nScraper interrupted by user.")
    
    finally:
        if driver:
            driver.quit()
        
        print(f"\nScraping session completed:")
        print(f"Total scrapes: {scrape_count}")
        print(f"Duration: {datetime.now() - start_time}")
        print(f"Data saved to: yolostocks_realtime.csv")


def main():
    """Main function to run the scraper with options"""
    print("YoloStocks Real-Time Scraper")
    print("=" * 50)
    
    # Parse command line arguments or use interactive mode
    import argparse
    parser = argparse.ArgumentParser(description='YoloStocks Real-Time Scraper')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run in continuous mode')
    parser.add_argument('--interval', type=int, default=5,
                       help='Interval between scrapes in minutes (default: 5)')
    parser.add_argument('--duration', type=float, default=None,
                       help='Duration to run in hours (default: infinite)')
    parser.add_argument('--single', action='store_true',
                       help='Run single scrape only')
    
    args = parser.parse_args()
    
    if args.single or not args.continuous:
        # Single scrape mode
        print("Running single scrape...")
        tickers_data = scrape_yolostocks()
        
        if tickers_data:
            print(f"\nSuccessfully scraped {len(tickers_data)} tickers:")
            print("-" * 50)
            
            # Display the data
            for i, ticker in enumerate(tickers_data[:5], 1):
                # Convert to string and handle Unicode characters
                ticker_str = str(ticker).encode('utf-8', errors='replace').decode('utf-8')
                print(f"{i}. {ticker_str}")
            if len(tickers_data) > 5:
                print(f"... and {len(tickers_data) - 5} more")
            
            # Save to CSV
            print("\nSaving data to CSV...")
            df = save_to_csv(tickers_data, append=False)
            
            if df is not None:
                print("\nData saved successfully!")
        else:
            print("Failed to scrape data from yolostocks.live")
    else:
        # Continuous mode
        continuous_scraper(interval_minutes=args.interval, 
                         duration_hours=args.duration)

if __name__ == "__main__":
    main()