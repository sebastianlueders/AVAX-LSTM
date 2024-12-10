import pandas as pd

# Read the CSV files
bitcoin_df = pd.read_csv('bitcoin.csv')
ethereum_df = pd.read_csv('ethereum.csv')

# Merge the dataframes on the 'Date' column
merged_df = pd.merge(bitcoin_df, ethereum_df, on='Date', how='outer')

# Save the merged dataframe to a new CSV file
merged_df.to_csv('combined_data.csv', index=False)

print("CSV files have been combined and saved to 'combined_data.csv'")

