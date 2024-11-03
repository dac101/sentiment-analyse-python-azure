# Sentiment Analysis for Depression Detection on Social Media

## Project Description

This project is a **sentiment analysis tool** designed to identify depression-related sentiment from social media posts, specifically from Reddit. By using Python and various NLP techniques, this tool collects and analyzes user-generated content to determine sentiment, providing valuable insights for mental health monitoring.

## Features

- **Data Collection**: Scrapes Reddit posts relevant to depression using Python scripts.
- **Sentiment Analysis**: Uses Natural Language Processing (NLP) to determine sentiment polarity.
- **Data Visualization**: Insights are presented through visualizations to make data interpretation straightforward and actionable.
- **Azure/AWS Integration**: Optionally utilizes cloud services for data storage and analysis.

## Project Structure

- **`data_collection_reddit_scrapper.py`**: Script for scraping Reddit posts.
- **`read_reddit.py`**: Processes Reddit data for sentiment analysis.
- **`sentiment_analyzer.py`**: Analyzes the sentiment of the text data.
- **`azure_blob_uploader.py`**: Uploads data files to Azure Blob Storage.

## Requirements

- Python 3.8+
- Libraries: `pandas`, `nltk`, `textblob`, `requests`, `azure.storage.blob`, etc.
- Azure account (optional)

## Installation

1. Clone the repository:
2.pip install -r requirements.txt

## usage :
python data_collection_reddit_scrapper.py
python sentiment_analyzer.py
python azure_blob_uploader.py

