import os
from datetime import datetime, timedelta
import pandas as pd
from pytrends.request import TrendReq

if not os.path.exists('trend_data.csv'):
    print("File does not exist in the current directory.")


def fetch_trend_data(keyword, timeframe, geo=''):
    """
    Fetches trend data for a specific keyword and timeframe using Pytrends.

    Parameters:
    - keyword (str): The search keyword.
    - timeframe (str): The timeframe for data retrieval.
    - geo (str): Geographic location (default is worldwide).

    Returns:
    - DataFrame containing the interest over time.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
    return pytrends.interest_over_time()

def update_trend_data(csv_file, keyword):
    """
    Updates the `trendScore` column in the given CSV file with data fetched from Pytrends.

    Parameters:
    - csv_file (str): Path to the CSV file to update.
    - keyword (str): The search keyword for the trend score.
    """
    # Load existing data
    if not os.path.exists(csv_file):
        print(f"File '{csv_file}' does not exist. Please create it first.")
        return

    trend_data = pd.read_csv(csv_file)
    trend_data['time'] = pd.to_datetime(trend_data['time'])
    
    # Identify rows with missing trend scores
    missing_rows = trend_data[trend_data[f'trendScore={keyword}'].isna()]

    if missing_rows.empty:
        print("No missing values to update.")
        return

    # Loop through missing rows and fetch data
    for idx, row in missing_rows.iterrows():
        date = row['time']
        timeframe = f"{date.strftime('%Y-%m-%d')} {date.strftime('%Y-%m-%d')}"
        print(f"Fetching data for {date.strftime('%Y-%m-%d')}...")
        
        try:
            data = fetch_trend_data(keyword, timeframe)
            if not data.empty and keyword in data.columns:
                trend_score = data[keyword].iloc[0]
                trend_data.at[idx, f'trendScore={keyword}'] = trend_score
        except Exception as e:
            print(f"Error fetching data for {date}: {e}")

    # Save the updated CSV
    trend_data.to_csv(csv_file, index=False)
    print(f"CSV file '{csv_file}' has been updated.")

if __name__ == "__main__":
    # CSV file and keyword
    csv_file = 'trend_data.csv'
    keyword_to_search = "Bitcoin"

    # Update the trend data
    update_trend_data(csv_file, keyword_to_search)
