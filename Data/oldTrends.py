import os
from datetime import datetime, timedelta
import pandas as pd
from pytrends.request import TrendReq
import time  # For the timer
import random  # For generating random intervals



# List to store missing timeframes
missingData = []

def fetch_hourly_data_in_batches(keyword, geo='', output_folder='pytrends_output'):
    """
    Fetches hourly search data for a given keyword in weekly batches and retries missing timeframes.
    """
    pytrends = TrendReq(hl='en-US', tz=360)

    # Define the date range for the query
    start_date = datetime(2020, 12, 18)
    end_date = datetime.now()
    delta = timedelta(days=7)
    all_data = []

    # Iterate through the date range in weekly batches
    while start_date < end_date:
        batch_start = start_date
        batch_end = min(start_date + delta, end_date)
        timeframe = f"{batch_start.strftime('%Y-%m-%d')} {batch_end.strftime('%Y-%m-%d')}"
        print(f"Fetching data for timeframe: {timeframe}")
        
        try:
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
            batch_data = pytrends.interest_over_time()
            
            if not batch_data.empty:
                all_data.append(batch_data)
        except Exception as e:
            missingData.append(timeframe)
            print(f"Error fetching data for timeframe {timeframe}: {e}")
        
        start_date = batch_end

    # Retry for missing data
    # Retry for missing data
    while missingData:
        current_round = missingData.copy()  # Copy current list to avoid modifying while iterating
        missingData.clear()  # Clear to only re-add failures from this round

        for retry_timeframe in current_round:
            print(f"Retrying for missing timeframe: {retry_timeframe}")
            
            try:
                pytrends.build_payload([keyword], cat=0, timeframe=retry_timeframe, geo=geo, gprop='')
                retry_data = pytrends.interest_over_time()
                
                if not retry_data.empty:
                    all_data.append(retry_data)
                else:
                    print(f"No data available for timeframe {retry_timeframe}")
            except Exception as e:
                print(f"Failed again for timeframe {retry_timeframe}: {e}")
                missingData.append(retry_timeframe)  # Re-add to the missing list to retry later
        
        # Add a random delay of 0 to 10 minutes after one round of retries
        if missingData:
            delay_minutes = random.randint(0, 10)
            print(f"Delaying next retry round by {delay_minutes} minutes...")
            time.sleep(delay_minutes * 60)
    

    # Combine all batches into a single DataFrame
    if all_data:
        combined_data = pd.concat(all_data)
        combined_data = combined_data.reset_index()
        combined_data = combined_data.rename(columns={keyword: 'search_count', 'date': 'time_interval'})
        combined_data = combined_data[['time_interval', 'search_count']]

        # Sort by the 'time_interval' column
        combined_data['time_interval'] = pd.to_datetime(combined_data['time_interval'])  # Ensure it's in datetime format
        combined_data = combined_data.sort_values(by='time_interval')

        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{keyword}_pytrends.csv")
        combined_data.to_csv(output_file, index=False)

        print(f"Hourly data saved to {output_file}")
    else:
        print("No data retrieved for the given keyword.")

# Example usage
if __name__ == "__main__":
    keyword_to_search = "Bitcoin"
    fetch_hourly_data_in_batches(keyword=keyword_to_search, geo="", output_folder="pytrends_output")
