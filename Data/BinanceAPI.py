import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading

class BinanceAPI:
    BASE_URL = 'https://data.binance.vision'

    def __init__(self, start_date=None, symbols=None, interval='minute', max_workers=5):
        """
        Initialize the BinanceAPI class.

        Args:
            start_date (str): The start date for data retrieval in 'YYYY-MM-DD' format.
            symbols (list): List of trading pair symbols (e.g., ['BTCUSDT', 'ETHUSDT']).
            interval (str): Aggregation interval ('minute', 'hourly', 'daily').
            max_workers (int): Number of threads for parallel processing.
        """
        self.start_date = start_date or '2023-06-25'
        self.symbols = symbols or ['BTCUSDT']
        self.interval = interval
        self.max_workers = max_workers
        self.dates_to_process = self.generate_date_range()

        # Create a folder name based on the trading pairs
        self.output_folder = "_".join(self.symbols)
        os.makedirs(self.output_folder, exist_ok=True)

    def generate_date_range(self):
        """
        Generate a list of dates from the start date to two days before today.

        Returns:
            list: List of date strings in 'YYYY-MM-DD' format.
        """
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.today() - timedelta(days=2)  # Two days before today

        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        print(f"Generated date range from {dates[0]} to {dates[-1]}")
        return dates

    def download_and_process(self, date, symbol):
        """
        Download and process the data for a given date and symbol.

        Args:
            date (str): The date in 'YYYY-MM-DD' format.
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').

        Returns:
            DataFrame: The processed DataFrame for the symbol and date, or None if download fails.
        """
        year, month, day = date.split("-")
        url = f"{self.BASE_URL}/data/spot/daily/trades/{symbol}/{symbol}-trades-{year}-{month}-{day}.zip"
        zip_file_path = os.path.join(self.output_folder, f"{symbol}-trades-{date}.zip")
        csv_file_path = os.path.join(self.output_folder, f"{symbol}-trades-{date}.csv")

        try:
            print(f"Starting download for {symbol} on {date}...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                print(f"Downloaded data for {symbol} on {date}.")
                # Save the zip file locally
                with open(zip_file_path, "wb") as file:
                    file.write(response.content)

                # Extract the CSV file
                import zipfile
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.output_folder)

                print(f"Processing file: {csv_file_path}")
                # Load the CSV into a DataFrame
                df = pd.read_csv(csv_file_path, header=None)
                df.columns = [
                    "trans_id", "price", "amount", "dollar_amount", "unix", "flag1", "flag2"
                ]
                df = df.drop(columns=["flag1", "flag2"])  # Drop unnecessary columns
                return df
            else:
                print(f"Failed to download file for {symbol} on {date}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading or processing data for {symbol} on {date}: {e}")
            return None
        finally:
            # Clean up the zip file after extraction
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)
    def group_data(self, df, symbol):
        """
        Group the data by the specified interval and calculate metrics.

        Args:
            df (DataFrame): The DataFrame for the symbol.
            symbol (str): The trading pair symbol.

        Returns:
            DataFrame: The grouped DataFrame with prefixed metrics.
        """
        print(f"Grouping data for {symbol}...")
        df['datetime'] = pd.to_datetime(df['unix'], unit='ms')

        if self.interval == 'minute':
            df['interval'] = df['datetime'].dt.floor('min')  # Updated to use 'min'
        elif self.interval == 'hourly':
            df['interval'] = df['datetime'].dt.floor('H')
        elif self.interval == 'daily':
            df['interval'] = df['datetime'].dt.date
        else:
            raise ValueError("Invalid interval. Choose 'minute', 'hourly', or 'daily'.")

        grouped = df.groupby('interval').agg(
            date_open=('datetime', 'min'),
            date_close=('datetime', 'max'),
            open=('price', 'first'),
            high=('price', 'max'),
            low=('price', 'min'),
            close=('price', 'last'),
            volume=('amount', 'sum'),
            dollar_volume=('dollar_amount', 'sum'),
            last_id=('trans_id', 'max')
        ).reset_index()

        grouped['tick_size'] = self.interval
        grouped['symbol'] = symbol
        grouped['Change'] = ((grouped['close'] - grouped['open']) / grouped['open']) * 100

        # Prefix columns with the symbol name
        grouped = grouped.rename(columns=lambda col: f"{symbol}_{col}" if col not in ['interval'] else col)
        return grouped

    def merge_csv_files(self):
        """
        Merge all CSV files for all symbols into a single consolidated file with grouping.
        """

        consolidated_df = pd.DataFrame()
        lock = threading.RLock()  # Create a reentrant lock for synchronization

        def process_date_symbol(date_symbol):
            date, symbol = date_symbol
            print(f"Processing {symbol} for {date}...")
            return self.download_and_process(date, symbol)

        # Create a list of all combinations of dates and symbols
        date_symbol_combinations = [(date, symbol) for date in self.dates_to_process for symbol in self.symbols]

        # Use ThreadPoolExecutor for parallel downloads and processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(process_date_symbol, date_symbol_combinations)

        # Consolidate all results
        for (date, symbol), result in zip(date_symbol_combinations, results):
            if result is not None:
                print(f"Grouping data for {symbol} on {date}...")
                grouped_df = self.group_data(result, symbol)

                with lock:  # Acquire the lock before modifying the DataFrame
                    if consolidated_df.empty:
                        consolidated_df = grouped_df
                    else:
                        # Merge with proper suffixes to avoid duplicate columns
                        consolidated_df = pd.merge(
                            consolidated_df,
                            grouped_df,
                            on='interval',
                            how='outer',
                            suffixes=('', f"_{symbol}")
                        )

        # Sort by interval
        consolidated_df = consolidated_df.sort_values(by='interval')

        # Generate the output file name dynamically
        start_date = self.dates_to_process[0]
        end_date = self.dates_to_process[-1]
        output_csv = os.path.join(
            self.output_folder,
            f"Crypto-Metrics-{start_date}-To-{end_date}-{self.interval}.csv"
        )

        # Save the final consolidated CSV
        print(f"Saving consolidated data to {output_csv}...")
        consolidated_df.to_csv(output_csv, index=False)
        print(f"Consolidated data saved to {output_csv}")

        # Clean up individual source files
        print("Cleaning up individual source files...")
        for symbol in self.symbols:
            for date in self.dates_to_process:
                csv_file_path = os.path.join(self.output_folder, f"{symbol}-trades-{date}.csv")
                if os.path.exists(csv_file_path):
                    os.remove(csv_file_path)
                    print(f"Deleted {csv_file_path}")

        print("Clean-up complete.")





    def run(self):
        """
        Run the BinanceAPI workflow to merge and group CSV files.
        """
        print("Starting BinanceAPI workflow...")
        self.merge_csv_files()
        print("BinanceAPI workflow completed.")


if __name__ == "__main__":
    start_date = "2020-01-01"  # Starting date for data retrieval
    symbols = ["BTCUSDT", "ETHUSDT", "AVAXUSDT"]  # List of trading pairs
    interval = "daily"  # Choose from 'minute', 'hourly', 'daily'

    api_processor = BinanceAPI(start_date=start_date, symbols=symbols, interval=interval)
    api_processor.run()
