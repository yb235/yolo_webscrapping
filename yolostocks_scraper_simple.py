"""
YoloStocks.live Simple Web Scraper
Extracts Top 15 Tickers using requests and BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime

def scrape_yolostocks_simple():
    """
    Scrapes yolostocks.live using requests and BeautifulSoup
    Returns a list of dictionaries with ticker data
    """
    
    url = "https://yolostocks.live/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fetching data from {url} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find tables in different ways
        tables = soup.find_all('table')
        
        if not tables:
            # Look for div-based tables
            table_divs = soup.find_all('div', class_=lambda x: x and ('table' in x.lower() if isinstance(x, str) else False))
            
            if table_divs:
                print(f"Found {len(table_divs)} div-based table structures")
        
        tickers_data = []
        
        for table in tables:
            # Try to extract data from table
            rows = table.find_all('tr')
            
            for row in rows[:16]:  # Get header + top 15
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data and any(row_data):
                        tickers_data.append(row_data)
            
            if tickers_data:
                break
        
        # If no table found, try to find ticker data in other structures
        if not tickers_data:
            print("No traditional table found. Looking for ticker patterns...")
            
            # Look for common ticker patterns in the page
            import re
            
            # Find all text that looks like tickers
            page_text = soup.get_text()
            
            # Pattern for stock tickers (1-5 uppercase letters, possibly with $ prefix)
            ticker_pattern = r'\$?[A-Z]{1,5}(?:\s|$)'
            potential_tickers = re.findall(ticker_pattern, page_text)
            
            # Clean and filter
            tickers = []
            exclude = {'HTML', 'CSS', 'API', 'JSON', 'GET', 'POST', 'USD', 'USA'}
            for ticker in potential_tickers:
                clean_ticker = ticker.strip().replace('$', '')
                if clean_ticker not in exclude and clean_ticker not in tickers:
                    tickers.append(clean_ticker)
            
            if tickers:
                print(f"Found {len(tickers)} potential tickers")
                tickers_data = [[i+1, ticker] for i, ticker in enumerate(tickers[:15])]
        
        # Process the data
        if tickers_data:
            result = []
            
            # Check if first row is headers
            headers = []
            data_rows = tickers_data
            
            if tickers_data[0] and not any(char.isdigit() for char in str(tickers_data[0][0])):
                headers = tickers_data[0]
                data_rows = tickers_data[1:]
            
            for i, row in enumerate(data_rows[:15], 1):
                if headers and len(headers) == len(row):
                    ticker_dict = {headers[j]: row[j] for j in range(len(row))}
                else:
                    # Create default structure
                    ticker_dict = {
                        'Rank': str(i),
                        'Ticker': row[0] if row else '',
                        'Data': ' | '.join(row[1:]) if len(row) > 1 else ''
                    }
                result.append(ticker_dict)
            
            return result
        else:
            print("No ticker data found in the HTML")
            
            # Print a sample of the page for debugging
            print("\nPage title:", soup.title.string if soup.title else "No title")
            print("\nFirst 500 characters of page text:")
            print(soup.get_text()[:500])
            
            return []
            
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the page: {e}")
        return []

def display_and_save(data):
    """Display and save the scraped data"""
    if data:
        print(f"\nSuccessfully extracted {len(data)} items:")
        print("-" * 60)
        
        # Display the data
        df = pd.DataFrame(data)
        print(df.to_string())
        
        # Save to CSV
        csv_file = 'yolostocks_tickers_simple.csv'
        df.to_csv(csv_file, index=False)
        print(f"\nData saved to {csv_file}")
        
        # Save to JSON
        json_file = 'yolostocks_tickers_simple.json'
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {json_file}")
        
        return df
    else:
        print("No data to display or save")
        return None

def main():
    """Main function"""
    print("YoloStocks.live Simple Scraper")
    print("=" * 60)
    
    # Scrape the data
    data = scrape_yolostocks_simple()
    
    # Display and save
    display_and_save(data)

if __name__ == "__main__":
    main()