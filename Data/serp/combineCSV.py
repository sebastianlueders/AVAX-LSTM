import pandas as pd

# Read the CSV files
bitcoin_df = pd.read_csv('combined_data.csv')
ethereum_df = pd.read_csv('_trends.csv')

# Strip any leading/trailing spaces from the column names
bitcoin_df.columns = bitcoin_df.columns.str.strip()
ethereum_df.columns = ethereum_df.columns.str.strip()

# Convert the 'date' column to datetime format (without specifying the format)
bitcoin_df['date'] = pd.to_datetime(bitcoin_df['date'])  # Automatically infers the format
ethereum_df['date'] = pd.to_datetime(ethereum_df['date'])  # Automatically infers the format

# Check the column names and the 'date' column
print("Columns in bitcoin_df:", bitcoin_df.columns)
print("Columns in ethereum_df:", ethereum_df.columns)

# Merge the dataframes on the 'date' column using outer join to include all dates
merged_df = pd.merge(bitcoin_df, ethereum_df, on='date', how='outer')

# Sort the merged dataframe by 'date'
merged_df = merged_df.sort_values(by='date')

# Save the merged dataframe to a new CSV file
merged_df.to_csv('combined_data.csv', index=False)

print("CSV files have been combined and saved to 'combined_data.csv'")
