import pandas as pd
import matplotlib.pyplot as plt

# Read the data
try:
    df = pd.read_csv('daily_summary.csv')
    print("Data loaded successfully:", df)

    # Create a stacked bar chart
    ax = df.plot(x='date', y=['positive', 'negative', 'neutral'], kind='bar', stacked=True)
    plt.title('Daily Sentiment Counts for Tesla Tweets')
    plt.xlabel('Date')
    plt.ylabel('Number of Tweets')
    plt.savefig('sentiment_summary.png')
    plt.show()

    print("Visualization saved as 'sentiment_summary.png'")
except FileNotFoundError:
    print("Error: 'daily_summary.csv' not found. Please run 'sentiment_dashboard.py' first.")
except Exception as e:
    print(f"Error generating visualization: {e}")