import requests
import csv

# Function to fetch Google Trends data
def fetch_trends_data(keyword, start_date, end_date, api_key, location="US"):
    base_url = "https://serpapi.com/trends/daily_interest"
    params = {
        "api_key": api_key,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date,
        "location": location,
        "output": "csv",
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}, {response.text}")
        return None

# Save the data to CSV
def save_to_csv(data, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Interest"])
        for date, interest in data.items():
            writer.writerow([date, interest])

# Parameters
api_key = "1112567fdfb55cd9ed3e23d028cb3e8fec10b7851cc378c85cf915dd6e4c2b8c"  # Replace with your SerpAPI key
keyword = "bitcoin"           # Replace with the keyword you want to analyze
start_date = "2020-09-19"
end_date = "2024-12-06"
output_file = "google_trends_daily_interest.csv"

# Fetch and process the data
data = fetch_trends_data(keyword, start_date, end_date, api_key)
if data:
    interest_data = {entry["date"]: entry["value"] for entry in data.get("daily_interest", [])}
    save_to_csv(interest_data, output_file)
    print(f"Data saved to {output_file}.")
else:
    print("No data fetched. Please check your parameters or API key.")
