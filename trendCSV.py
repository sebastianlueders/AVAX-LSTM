import csv
from datetime import datetime, timedelta

# File name for the output CSV
output_file = 'trend_data.csv'

# Start date
start_date = datetime(2020, 12, 18)

# Get today's date
end_date = datetime.today()

# Generate all dates between start and end date
date_range = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
              for i in range((end_date - start_date).days + 1)]

# Write to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header
    csvwriter.writerow(['date', 'trendScore=Bitcoin'])
    
    # Write data rows
    for date in date_range:
        csvwriter.writerow([date, ''])

print(f"CSV file '{output_file}' has been created.")
