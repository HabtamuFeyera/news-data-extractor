# News Data Extractor

This Python script allows you to scrape news data from the AP News website based on specified search criteria and save it to an Excel file.

## Features

- Scrapes news articles from AP News website.
- Allows specifying search phrase, news category/section/topic, and time period for data extraction.
- Downloads and saves pictures associated with news articles.
- Saves scraped data to an Excel file for further analysis.

## Prerequisites

- Python 3.6 or higher
- Robocorp platform (optional, for accessing work item variables from Robocorp Control Room)

## Installation

1. Clone this repository to your local machine:

https://github.com/HabtamuFeyera/news-data-extractor.git


2. Navigate to the project directory:

cd news-data-extractor


3. Install the required Python packages using pip:

pip install -r requirements.txt


## Usage

1. Ensure that you have defined the necessary work item variables such as "search phrase", "news category/section/topic", and "number of months" in your Robocorp Control Room or in a configuration file.

2. Run the `main.py` script using Python:

python main.py


3. Monitor the script execution in the terminal/console. Review the generated Excel file ("ap_news.xlsx") and the downloaded pictures (if applicable) in the "news_pictures" folder.

## Configuration

- Modify the default parameters in the `main.py` file to customize the scraping process according to your requirements.
- Update the `apnews_scraper.py` file to adjust any scraping logic or behavior.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This script utilizes the [Robocorp](https://robocorp.com/) libraries for interacting with work items and web elements.
- Special thanks to the developers of the [RPA Framework](https://rpaframework.org/) for providing useful automation tools and libraries.


