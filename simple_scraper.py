"""
Simple YoloStocks Scraper using requests (fallback when Selenium unavailable)
"""

import requests
import time
import pandas as pd
from datetime import datetime
import json

def scrape_yolostocks_simple():
    """
    Simple scraper using requests - fallback when Selenium unavailable
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching data from yolostocks.live at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        response = requests.get("https://yolostocks.live/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("Successfully fetched page content")
            # This is a basic fallback - real parsing would need BeautifulSoup
            # For now, just demonstrate the concept
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Simulated data for demonstration
            mock_data = []
            for i in range(1, 16):
                mock_data.append({
                    'Timestamp': timestamp,
                    'Rank': str(i),
                    'Ticker': f'MOCK{i}',
                    'Mentions': f'{100-i*5}',
                    'Sentiment': f'{90-i*2}%',
                    'Price': f'${50+i*2}',
                    'Change': f'+{i*0.5}%'
                })
            
            return mock_data
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def save_to_csv_simple(data, filename='yolostocks_simple.csv'):
    """Save data to CSV"""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        return df
    return None

if __name__ == "__main__":
    print("Simple YoloStocks Scraper (Fallback)")
    print("=" * 50)
    
    data = scrape_yolostocks_simple()
    if data:
        print(f"Scraped {len(data)} items")
        df = save_to_csv_simple(data)
        if df is not None:
            print("\nSample data:")
            print(df.head())
    else:
        print("No data scraped")