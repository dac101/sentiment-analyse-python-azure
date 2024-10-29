#Done By Dacorie Smith

import json

import pandas as pd
import csv
import os
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime


class CSVHandler:
    def __init__(self, folder_path, columns):
        self.folder_path = folder_path
        self.columns = columns

    def get_all_csv_files(self):
        """Retrieves all CSV files from the given folder."""
        return [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]

    def read_csv(self, csv_file_path):
        """Reads a CSV file into a pandas DataFrame."""
        full_path = os.path.join(self.folder_path, csv_file_path)
        if os.path.exists(full_path):
            return pd.read_csv(full_path, encoding='utf-8')
        else:
            return pd.DataFrame(columns=self.columns)

    def write_csv(self, df, csv_file_path):
        """Writes the DataFrame back to the CSV file."""
        full_path = os.path.join(self.folder_path, csv_file_path)
        df.to_csv(full_path, index=False, encoding='utf-8')


class DataProcessor:
    def __init__(self, df):
        self.df = df

    def remove_duplicates(self, subset_columns):
        """Removes duplicates based on specific columns and keeps the first occurrence."""
        self.df = self.df.drop_duplicates(subset=subset_columns, keep='first')

    def get_dataframe(self):
        return self.df


class SentimentAnalyzer:
    def __init__(self, input_file_path, folder_path):
        self.input_file_path = input_file_path
        self.folder_path = folder_path
        self.updated_file_path = self.generate_updated_csv_path()
        self.sia = SentimentIntensityAnalyzer()

    def generate_updated_csv_path(self):
        """Generates the file path for the updated CSV by appending the current timestamp."""
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = os.path.basename(self.input_file_path).replace('.csv', '')
        updated_file_name = f"{file_name}_with_sentiment_{current_time}.csv"
        return os.path.join(self.folder_path, updated_file_name)

    @staticmethod
    def categorize_sentiment(compound_score):
        """Categorizes sentiment based on compound score."""
        if compound_score > 0.05:
            return 'good'
        elif compound_score < -0.05:
            return 'bad'
        else:
            return 'neutral'

    def analyze_and_update_csv(self):
        """Reads the CSV, performs sentiment analysis, and writes the updated rows to a new CSV."""
        with open(self.input_file_path, mode='r', newline='', encoding='utf-8') as file, \
                open(self.updated_file_path, mode='w', newline='', encoding='utf-8') as updated_file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames + ['neg_sentiment', 'neu_sentiment', 'pos_sentiment', 'compound_sentiment',
                                              'overall_sentiment']
            writer = csv.DictWriter(updated_file, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Perform sentiment analysis on the concatenated title and selftext columns
                text_to_analyze = row['title'] + row.get('selftext', '')
                sentiment_score = self.sia.polarity_scores(text_to_analyze)

                # Add sentiment scores to the row
                row['neg_sentiment'] = sentiment_score['neg']
                row['neu_sentiment'] = sentiment_score['neu']
                row['pos_sentiment'] = sentiment_score['pos']
                row['compound_sentiment'] = sentiment_score['compound']
                row['overall_sentiment'] = self.categorize_sentiment(sentiment_score['compound'])

                # Write the updated row to the new CSV
                writer.writerow(row)

class JSONHandler:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def write_json(self, data, json_file_path):
        """Writes data to a JSON file."""
        full_path = os.path.join(self.folder_path, json_file_path)
        with open(full_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def read_json(self, json_file_path):
        """Reads data from a JSON file into a list of dictionaries."""
        full_path = os.path.join(self.folder_path, json_file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return []


def main():
    # Define the folder where the CSV files are stored
    folder_path = "data"

    # Initialize CSV handler
    csv_columns = ['title', 'category', 'likes', 'num_comments', 'subreddit', 'view_count', 'selftext']
    csv_handler = CSVHandler(folder_path, csv_columns)

    # Retrieve all CSV files in the folder
    csv_files = csv_handler.get_all_csv_files()


    # Initialize JSON handler
    json_handler = JSONHandler(folder_path)

    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")

        # Read the CSV into a DataFrame
        df = csv_handler.read_csv(csv_file)

        # Process the data: Remove duplicates
        processor = DataProcessor(df)
        processor.remove_duplicates(subset_columns=['title', 'selftext'])

        # Save the cleaned DataFrame back to the original CSV
        csv_handler.write_csv(processor.get_dataframe(), csv_file)

        # Perform sentiment analysis and write to a new CSV with the current timestamp
        sentiment_analyzer = SentimentAnalyzer(os.path.join(folder_path, csv_file), folder_path)
        sentiment_analyzer.analyze_and_update_csv()

        # Save the sentiment-analyzed DataFrame to a JSON file
        json_file_path = csv_file.replace('.csv', '.json')
        json_handler.write_json(processor.get_dataframe().to_dict(orient='records'), json_file_path)


if __name__ == "__main__":
    main()
