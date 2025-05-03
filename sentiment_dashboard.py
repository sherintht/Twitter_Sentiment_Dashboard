import pandas as pd
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import os
from tenacity import retry, stop_after_attempt, wait_fixed

# Download NLTK data (run once)
nltk.download('punkt')
nltk.download('stopwords')

# Configuration (Google Sheets credentials)
from twitter_config import GC_SHEET_KEY, SHEET_ID

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(GC_SHEET_KEY, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet_name = 'Sheet1'

# Global variables
sentiment_data = []
daily_summary = []
processed_dates = set()

# Text cleaning function
def clean_tweet(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'@\w+|\#', '', text)  # Remove mentions and hashtags
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower().strip()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in tokens if word not in stop_words])
    return text

# Sentiment analysis function
def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity < 0:
        return 'negative'
    else:
        return 'neutral'

# Append to Google Sheet with retry logic
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def append_to_google_sheet(data):
    values = [[d['timestamp'], d['tweet'], d['cleaned_tweet'], d['sentiment']] for d in data]
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A1',
        valueInputOption='RAW',
        body=body
    ).execute()

# Update daily summary based on tweet timestamps
def update_daily_summary():
    global processed_dates
    # Group sentiment data by date
    df = pd.DataFrame(sentiment_data)
    if not df.empty:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        for tweet_date in df['date'].unique():
            if tweet_date not in processed_dates:
                date_data = df[df['date'] == tweet_date]
                summary = {
                    'date': tweet_date,
                    'positive': sum(1 for _, row in date_data.iterrows() if row['sentiment'] == 'positive'),
                    'negative': sum(1 for _, row in date_data.iterrows() if row['sentiment'] == 'negative'),
                    'neutral': sum(1 for _, row in date_data.iterrows() if row['sentiment'] == 'neutral')
                }
                daily_summary.append(summary)
                processed_dates.add(tweet_date)
        # Save to CSV
        if daily_summary:
            pd.DataFrame(daily_summary).to_csv('daily_summary.csv', index=False)

# Main function to process manual dataset
def process_manual_dataset():
    try:
        # Read the manual dataset
        df = pd.read_csv('manual_sentiment_log.csv')
        
        # Process each tweet
        for _, row in df.iterrows():
            text = row['tweet']
            timestamp = row['timestamp']
            
            # Clean the tweet and analyze sentiment
            cleaned_text = clean_tweet(text)
            sentiment = get_sentiment(cleaned_text)
            
            # Update the row with cleaned text and sentiment if not already provided
            data = {
                'timestamp': timestamp,
                'tweet': text,
                'cleaned_tweet': cleaned_text,
                'sentiment': sentiment
            }
            sentiment_data.append(data)
            print(f"Tweet: {text} | Sentiment: {sentiment}")

        # Save to CSV
        if not os.path.exists('sentiment_log.csv'):
            pd.DataFrame(sentiment_data).to_csv('sentiment_log.csv', index=False)
        else:
            pd.DataFrame(sentiment_data).to_csv('sentiment_log.csv', mode='a', index=False, header=False)

        # Append to Google Sheet
        if sentiment_data:
            append_to_google_sheet(sentiment_data)

        # Update daily summary
        update_daily_summary()

    except Exception as e:
        print(f"Error processing dataset: {e}")

if __name__ == "__main__":
    process_manual_dataset()