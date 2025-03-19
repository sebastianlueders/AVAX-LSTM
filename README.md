# AVAX-LSTM-Project

## Quick Notes

Interpreters that are built to use the gpu will do better with this model.
libraries: pandas, datetime, matplotlib, scikit-learn, tensorflow

Step 1: Ensure Python is installed. 

Step 2: Ensure tensorflow is installed
pip install tensorflow

Step 3: Ensure scikit-learn is installed
$pip install scikit-learn


As long as you have these libraries installed model1.0.py should running giving the mae of predictions for cryprocurrency prices.

Run Model/model1.0.py to run this script.

## Report

This project aimed to predict the price movements of the AVAX/USDT cryptocurrency pair by integrating a combination of financial, macroeconomic, and trend-based indicators. The task was challenging given the volatile nature of cryptocurrency markets, which often react rapidly to external factors. Our approach was grounded in the idea that incorporating not only market data, such as cryptocurrency price and volume, but also global macroeconomic indicators and signals derived from Google search interest, could provide a more holistic view that might improve predictive accuracy. 

The dataset for this project came from a variety of sources, including historical cryptocurrency price data, macroeconomic indicators like exchange rates and inflation levels, and Google Trends data related to cryptocurrency search terms. For instance, we included daily open, high, low, and close (OHLC) data for multiple cryptocurrencies such as AVAX, Ethereum, and Bitcoin, along with corresponding trading volumes. We also gathered macroeconomic data like EUR/USD exchange rates, real GDP figures, and consumer price indices, as well as search-interest metrics for terms such as “buy bitcoin” and “buy Ethereum.” By integrating these indicators into a single dataset, we hoped to capture the interplay of market conditions, economic climates, and public sentiment that together influence price movements. 

Collecting and integrating such a diverse array of data sources proved to be difficult. We often encountered missing values, irregular date formats, and issues of data availability. Some sources provided comprehensive daily data while others were updated on a weekly or monthly basis. Aligning these differing frequencies and ensuring consistent daily time steps required careful handling, including using forward-filling techniques or choosing to exclude certain features that were not sufficiently granular. A significant hurdle emerged when we attempted to retrieve Google Trends data using the pytrends library, only to encounter multiple HTTP 429 errors due to rate limiting. To circumvent this, we resorted to using a Scraper API, which allowed us to route our data requests through rotating proxies and ultimately procure the trend data we needed. 

Once the data was collected, we focused on preprocessing and feature engineering to ensure it was suitable for modeling. We dropped columns that were either redundant or provided no meaningful predictive power, then filled missing values with column-wise means. To stabilize training and improve the convergence of our neural network models, we normalized most features to a [0, 1] range, leaving the target column (AVAXUSDT_close) unscaled. We also employed a windowing approach to transform the time series into a supervised learning problem: the model would see seven days of historical data and then predict the following day’s closing price. This windowing technique allowed the model to learn temporal dependencies and patterns that might be present in the data. 

For our predictive model, we employed a Long Short-Term Memory (LSTM) neural network implemented in TensorFlow/Keras. The architecture began with an LSTM layer designed to capture temporal patterns, followed by dense layers with ReLU activations for further feature extraction, and concluded with a single output neuron predicting the next day’s price. We used Mean Squared Error as the loss function and Mean Absolute Error as an evaluation metric, given its intuitive interpretation in terms of average absolute deviation from the actual price. The data was split chronologically into training, validation, and test sets, with the training portion being 70%, the validation 10%, and the test 20%. This splitting strategy helped us tune hyperparameters and monitor overfitting on the validation set, and then finally measure the model’s unbiased performance on unseen test data. 

Our results showed that the model could learn certain patterns and trends in the data, yet it struggled with periods of heightened volatility and sudden market shifts. Like when the market was newer in 2020 Although the predictions were not perfect, they established a baseline performance level. By comparing them against simple approaches, such as always predicting yesterday’s price, one could assess the incremental value of incorporating macroeconomic indicators and Google search trends. The complexity and noise of the cryptocurrency market, along with the challenges of interpreting diverse external signals, made this a difficult forecasting task. 

In building our model, several key decisions were made to optimize performance. We chose the F1 score as our evaluation metric due to the imbalanced nature of our dataset, ensuring that both precision and recall were prioritized. During data preprocessing, certain columns, such as AVAX price changes over multiple days and Google Trends data, were dropped as they were either redundant (handled by the sequential nature of the model) or not directly related to the target variable. To prevent overfitting, we limited the number of epochs to 50, as the model was observed to converge early, with additional epochs leading to redundant weight updates and poorer generalization. For the model architecture, we transitioned from a more complex configuration (LSTM: 128, Dense: 64, 64) to a simpler and more effective setup (LSTM: 64, Dense: 32, 64). This change reduced the risk of overfitting while maintaining the ability to capture meaningful patterns in the data. Finally, we selected Mean Absolute Error (MAE) as the loss function because it provides a straightforward measure of prediction accuracy by penalizing errors linearly.

![AVAX-Prediction (1)](https://github.com/user-attachments/assets/ff4761f9-9c9f-4830-8c55-ccc50c0873ee)


In conclusion, despite the difficulties of data collection and preprocessing, including navigating through missing values, incompatible date formats, and scraping restrictions, we successfully assembled and integrated a rich dataset. Our LSTM-based model provided a starting point for understanding how different data modalities might inform price predictions. Future research could improve on these results by experimenting with more advanced neural network architectures, incorporating additional sources of sentiment data, employing more robust scaling and imputation techniques, and implementing feature selection methods. While our current model did not yield groundbreaking forecasting accuracy, the methodology and data integration steps outlined in this project could guide more sophisticated attempts at cryptocurrency price prediction in the future. 

## Contributors
Sebastian Lueders
Daniel Duvic
Ayra Aftab
Kadin Suga
Ethan Grassia
