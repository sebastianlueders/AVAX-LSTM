import os
from datetime import datetime, timedelta
import pandas as pd
from pytrends.request import TrendReq

def fetch_hourly_data_in_batches(keyword, geo='', output_folder='pytrends_output'):
    """
    Fetches hourly search data for a given keyword in weekly batches and saves it as a CSV.

    Parameters:
    - keyword (str): The search keyword.
    - geo (str): Geographic location (default is worldwide). Use region codes like 'US' for United States.
    - output_folder (str): The folder to save the output CSV.
    """
    # Initialize pytrends
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Define the date range for the query
    start_date = datetime(2017, 12, 1)  # Start date (6 years ago)
    end_date = datetime.now()  # Current date
    delta = timedelta(days=7)  # Weekly intervals
    
    all_data = []  # To store results from each batch
    
    # Iterate through the date range in weekly batches
    while start_date < end_date:
        batch_start = start_date
        batch_end = min(start_date + delta, end_date)
        
        # Define the timeframe for the current batch
        timeframe = f"{batch_start.strftime('%Y-%m-%d')} {batch_end.strftime('%Y-%m-%d')}"
        
        print(f"Fetching data for timeframe: {timeframe}")
        
        try:
            # Request data from pytrends
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
            batch_data = pytrends.interest_over_time()
            
            if not batch_data.empty:
                all_data.append(batch_data)
        except Exception as e:
            print(f"Error fetching data for timeframe {timeframe}: {e}")
        
        # Move to the next batch
        start_date = batch_end
    
    # Combine all batches into a single DataFrame
    if all_data:
        combined_data = pd.concat(all_data)
        combined_data = combined_data.reset_index()
        combined_data = combined_data.rename(columns={keyword: 'search_count', 'date': 'time_interval'})
        combined_data = combined_data[['time_interval', 'search_count']]
        
        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        # Save the combined data to a CSV file
        output_file = os.path.join(output_folder, f"{keyword}_pytrends.csv")
        combined_data.to_csv(output_file, index=False)
        
        print(f"Hourly data saved to {output_file}")
    else:
        print("No data retrieved for the given keyword.")

# Example usage
if __name__ == "__main__":
    keyword_to_search = "Bitcoin"
    fetch_hourly_data_in_batches(keyword=keyword_to_search, geo="", output_folder="pytrends_output")