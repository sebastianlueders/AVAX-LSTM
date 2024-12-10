import csv
from serpapi import GoogleSearch
import pandas as pd
from datetime import datetime, timedelta

# Function to calculate date ranges in 8-month cycles
def get_date_ranges(start_date, end_date):
    ranges = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=30 * 8), end_date)  # 8 months = ~240 days
        ranges.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)
    return ranges

# Function to call the API and process results
def fetch_data_for_date_range(api_key, start_date, end_date, query):
    params = {
        "api_key": api_key,
        "engine": "google_trends",
        "q": query,
        "data_type": "TIMESERIES",
        "cat": "0",
        "date": f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}",
        "csv": "false",
        "include_low_search_volume": "true"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Extract timeline data
    timeline_data = results.get("interest_over_time", {}).get("timeline_data", [])
    extracted_data = [
        {"date": item["date"], "extracted_value": item["values"][0]["extracted_value"]}
        for item in timeline_data
    ]
    return extracted_data

# Main function
def main(keyword):
    # API key and query
    api_key = "1112567fdfb55cd9ed3e23d028cb3e8fec10b7851cc378c85cf915dd6e4c2b8c"  # Replace with your API key
    
    query = keyword

    # Define date range
    start_date = datetime.strptime("2020-09-19", "%Y-%m-%d")
    end_date = datetime.strptime("2024-12-06", "%Y-%m-%d")

    # Get all date ranges
    date_ranges = get_date_ranges(start_date, end_date)

    # Output file
    output_file = f"{query}_trends.csv"

    # Write header to CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date", f"{query}"])  # Header

    # Fetch data for each date range and write to CSV
    for start, end in date_ranges:
        print(f"Fetching data from {start} to {end}...")
        data = fetch_data_for_date_range(api_key, start, end, query)
        with open(output_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow([row["date"], row[f"{query}"]])

    print(f"Data has been saved to {output_file}")

# Run the script
if __name__ == "__main__":
    query = ["query1", "query2"] 
    for q in query:
        main(q)  # Call the main function with each query

