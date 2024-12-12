import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers

# Load dataset
df = pd.read_csv('merged_combined_final.csv')

# Drop specified columns
columns_to_drop = [
    'AVAXUSDT_1day_change', 'AVAXUSDT_2day_change', 'AVAXUSDT_3day_change',
    'AVAXUSDT_4day_change', 'AVAXUSDT_5day_change', 'AVAXUSDT_6day_change',
    'AVAXUSDT_7day_change', 'AVAXUSDT_yesterday_change', 'ETHUSDT_1day_change',
    'ETHUSDT_2day_change', 'ETHUSDT_3day_change', 'ETHUSDT_4day_change',
    'ETHUSDT_5day_change', 'ETHUSDT_6day_change', 'ETHUSDT_7day_change',
    'ETHUSDT_yesterday_change', 'BTCUSDT_1day_change', 'BTCUSDT_2day_change',
    'BTCUSDT_3day_change', 'BTCUSDT_4day_change', 'BTCUSDT_5day_change',
    'BTCUSDT_6day_change', 'BTCUSDT_7day_change', 'BTCUSDT_yesterday_change',
    'crypto to buy now', 'TargetVal', 'crypto crash', 'BTC_SMA'
]
df = df.drop(columns=columns_to_drop, errors='ignore')

# Convert date column to datetime
def str_to_datetime(s):
    if pd.isna(s):
        return None
    try:
        split = str(s).split('-')
        year, month, day = int(split[0]), int(split[1]), int(split[2])
        return datetime.datetime(year=year, month=month, day=day)
    except Exception as e:
        print(f"Invalid date format: {s}, Error: {e}")
        return None

df['date'] = df['date'].apply(str_to_datetime)
df.index = df.pop('date')

# Handle missing values and normalize features
def preprocess_data(dataframe, target_col):
    """
    Normalize the features and fill missing values with column averages,
    but leave the target column unscaled.
    """
    dataframe = dataframe.copy()

    # Drop columns with all NaN values
    dataframe = dataframe.dropna(axis=1, how='all')

    # Fill missing values with column averages
    for col in dataframe.columns:
        if dataframe[col].isna().any():
            dataframe[col] = dataframe[col].fillna(dataframe[col].mean())
    
    # Normalize only the features (not the target column)
    scalers = {}
    normalized_df = pd.DataFrame(index=dataframe.index)
    for col in dataframe.columns:
        if col != target_col:  # Skip normalization for the target column
            scaler = MinMaxScaler()
            normalized_df[col] = scaler.fit_transform(dataframe[[col]])
            scalers[col] = scaler  # Save scaler for inverse transformation
        else:
            normalized_df[col] = dataframe[col]  # Leave target as is
    
    return normalized_df, scalers

# Preprocess data
target_col = 'AVAXUSDT_close'
normalized_df, scalers = preprocess_data(df, target_col)

# Generate windowed DataFrame
def df_to_windowed_df_all_features(dataframe, target_col, n=7):
    """
    Create a windowed DataFrame for time-series prediction using past feature values only.

    Parameters:
    - dataframe: The input DataFrame.
    - target_col: The name of the column to use as the prediction target.
    - n: The size of the sliding window (number of past days).

    Returns:
    - A new DataFrame with windows and the target column aligned for prediction.
    """
    features = dataframe.drop(columns=[target_col]).columns
    X, Y, dates = [], [], []

    for i in range(n, len(dataframe)):  # Start at index `n` to ensure enough past data
        # Use the past `n` days (excluding the current day's features)
        window = dataframe.iloc[i - n:i][features].to_numpy()
        # Use the current day's target value (to predict the target for the current day)
        target = dataframe.iloc[i][target_col]

        X.append(window)
        Y.append(target)
        dates.append(dataframe.index[i])

    # Flatten the windowed features for DataFrame representation
    flat_X = np.array(X).reshape(len(X), -1)
    ret_df = pd.DataFrame(flat_X, columns=[
        f'{col}_t-{j+1}' for j in range(n) for col in features
    ])
    ret_df['Target'] = Y
    ret_df['Date'] = dates

    return ret_df

windowed_df = df_to_windowed_df_all_features(normalized_df, target_col=target_col, n=7)

# Prepare data for LSTM
def windowed_df_to_date_X_y(windowed_dataframe, n=7):
    df_as_np = windowed_dataframe.to_numpy()
    dates = df_as_np[:, -1]
    middle_matrix = df_as_np[:, 0:-2]
    n_features = middle_matrix.shape[1] // n  # Infer the number of features
    X = middle_matrix.reshape((len(dates), n, n_features))
    Y = df_as_np[:, -2]
    return dates, X.astype(np.float32), Y.astype(np.float32)

dates, X, y = windowed_df_to_date_X_y(windowed_df)

# Train/Validation/Test Split
q_70 = int(len(dates) * 0.7)
q_80 = int(len(dates) * 0.8)

dates_train, X_train, y_train = dates[:q_70], X[:q_70], y[:q_70]
dates_val, X_val, y_val = dates[q_70:q_80], X[q_70:q_80], y[q_70:q_80]
dates_test, X_test, y_test = dates[q_80:], X[q_80:], y[q_80:]

# Build and Train LSTM Model
model = Sequential([
    layers.Input((7, X_train.shape[2])),
    layers.LSTM(64),
    layers.Dense(32, activation='relu'),
    layers.Dense(64, activation='relu'),
    layers.Dense(1)
])

model.compile(loss='mse', optimizer=Adam(learning_rate=0.001), metrics=['mean_absolute_error'])

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=500)

# Predict and evaluate on the original scale
predictions = model.predict(X_test)

plt.plot(dates_test, y_test)
plt.plot(dates_test, predictions)

plt.legend(['Acutal', 'Predicted'])
plt.show()

mae_original_scale = mean_absolute_error(y_test, predictions)

print(f"MAE on original scale: {mae_original_scale}")