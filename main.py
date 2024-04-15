from RPA.Robocorp.WorkItems import WorkItems
from apnews_scraper import ApnewsScraper

def main():
    # Create a WorkItems instance to access work item variables
    work_items = WorkItems()

    # URL of AP News website
    url = "https://apnews.com/"

    # Create an instance of ApnewsScraper with the fetched parameters
    ap_scraper = ApnewsScraper(url, work_items)

    # Execute the scraping process
    ap_scraper.open_website()
    ap_scraper.open_search_option()
    ap_scraper.search_phrase()
    ap_scraper.select_news_category()
    ap_scraper.choose_latest_news()
    ap_scraper.extract_data_and_save_to_excel()

if __name__ == "__main__":
    main()
