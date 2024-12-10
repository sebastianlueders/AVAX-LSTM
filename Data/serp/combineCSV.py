import pandas as pd

# Read the CSV files
combined_df = pd.read_csv('merged_combined_data.csv')
target_df = pd.read_csv('Cryptocurrency fraud_trends.csv')

# Strip leading/trailing spaces from column names
combined_df.columns = combined_df.columns.str.strip()
target_df.columns = target_df.columns.str.strip()

# Convert 'date' columns to datetime format
combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
target_df['date'] = pd.to_datetime(target_df['date'], errors='coerce')

# Check for duplicate dates in each dataframe
print("Duplicate dates in combined_df:")
print(combined_df[combined_df.duplicated(subset='date', keep=False)])

print("Duplicate dates in target_df:")
print(target_df[target_df.duplicated(subset='date', keep=False)])

# Drop duplicates to ensure one-to-one mapping
combined_df = combined_df.drop_duplicates(subset='date', keep='first')
target_df = target_df.drop_duplicates(subset='date', keep='first')

# Perform an outer merge on the 'date' column
merged_df = pd.merge(combined_df, target_df, on='date', how='outer')

# Sort the merged dataframe by 'date'
merged_df = merged_df.sort_values(by='date').reset_index(drop=True)

# Validate alignment: Inspect a sample of the data
print("Sample of merged dataframe:")
print(merged_df[['date', 'bitcoin']].head(10))  # Inspect 'date' and 'bitcoin' columns for alignment

# Check for any rows where 'bitcoin' is NaN
misaligned_rows = merged_df[merged_df['bitcoin'].isna()]
if not misaligned_rows.empty:
    print("Rows with missing bitcoin values after merge:")
    print(misaligned_rows)

# Save the merged dataframe to a new CSV file
merged_df.to_csv('merged_combined_data.csv', index=False)
print("CSV files have been combined and saved to 'merged_combined_dataThree.csv'")

# Optional: Inspect rows in a specific date range to validate alignment
date_range = pd.date_range(start='2023-05-01', end='2023-05-10')
print("Combined_df rows in date range:")
print(combined_df[combined_df['date'].isin(date_range)])

print("Target_df rows in date range:")
print(target_df[target_df['date'].isin(date_range)])

print("Merged_df rows in date range:")
print(merged_df[merged_df['date'].isin(date_range)])
