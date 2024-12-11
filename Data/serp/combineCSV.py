import pandas as pd

# Read the CSV files using relative paths
combined_df = pd.read_csv('Data/final-dataset.csv')
target_df = pd.read_csv('Data/merged_combined_data.csv')  # Assuming this file is in the same folder as the script

# Strip leading/trailing spaces from column names
combined_df.columns = combined_df.columns.str.strip()
target_df.columns = target_df.columns.str.strip()

# Standardize the date column names
combined_df.rename(columns={'Date': 'date'}, inplace=True)

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
merged_df.to_csv('merged_combined_dataThree.csv', index=False)
print("CSV files have been combined and saved to 'merged_combined_dataThree.csv'")
