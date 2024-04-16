import logging
import os
import re
from datetime import datetime, timedelta
from dateutil import parser
from urllib.parse import urlparse
import requests

from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Robocorp.WorkItems import WorkItems
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApnewsScraper:
    def __init__(self, url, work_items, excel_file="ap_news.xlsx"):
        self.browser = Selenium()
        self.http = HTTP()
        self.work_items = work_items
        self.url = url
        self.excel_file = excel_file
        self.picture_folder = "news_pictures"
        os.makedirs(self.picture_folder, exist_ok=True)

    def get_search_phrase(self):
        try:
            return self.work_items.get("search phrase")
        except Exception as e:
            logger.error(f"Error fetching search phrase from work items: {e}")
            return None

    def open_website(self):
        try:
            self.browser.open_available_browser(self.url, maximized=True)
            logger.info("Opened the AP News website")
        except Exception as e:
            logger.error(f"Error opening website: {e}")

    def open_search_option(self):
        search_button_xpath = '//*[@id="Page-header-trending-zephr"]/div[1]/div[3]/bsp-search-overlay/div/form/label/input'
        try:
            search_button = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, search_button_xpath))
            )
            search_button.click()
            logger.info("Opened the search option")
        except Exception as e:
            logger.error(f"Error opening the search option: {e}")

    def select_news_category(self):
        topic = self.work_items.get("news category/section/topic")
        if topic:
            try:
                category_xpath = f"//span[text()='{topic}']"
                self.browser.wait_until_element_is_visible(category_xpath, 30)
                self.browser.click_element(category_xpath)
                logger.info(f"Selected news category: {topic}")
            except Exception as e:
                logger.warning(f"Error selecting news category: {e}")

    def choose_latest_news(self):
        select_xpath = "//select[@id='search-sort-option']"
        try:
            self.browser.wait_until_element_is_enabled(select_xpath, 120)
            self.browser.click_element(select_xpath)
            option_xpath = "//option[@value='date']"
            self.browser.wait_until_element_is_enabled(option_xpath, 120)
            self.browser.click_element(option_xpath)
            logger.info("Chose the latest news")
        except Exception as e:
            logger.error(f"Error choosing the latest news: {e}")

    def extract_data_and_save_to_excel(self):
        current_date = datetime.now()

        month_no = int(self.work_items.get("number of months"))

        if month_no == 0 or month_no == 1:
            start_date = current_date.replace(day=1)
        elif month_no > 1:
            middle_date = current_date.replace(day=15)
            days_to_subtract = (month_no - 1) * 30
            new_date = middle_date - timedelta(days=days_to_subtract)
            start_date = new_date.replace(day=1)

        data = {
            "Title": [],
            "Date": [],
            "Description": [],
            "Title Count": [],
            "Description Count": [],
            "Money Present": [],
            "Picture Filename": []
        }

        i = 1
        while True:
            try:
                link_xpath = f"(//a[@class='u-clickable-card__link'])[{i}]"
                self.browser.wait_until_element_is_enabled(link_xpath, 10)
                self.browser.scroll_element_into_view(link_xpath)
                paragraph = self.browser.get_text(f'(//div[@class="gc__excerpt"]//p)[{i}]')

                splitted = paragraph.split('...')
                date = splitted[0]

                if 'ago' in date:
                    current_time = datetime.now()
                    value, units, _ = date.split()
                    unit_mapping = {'hour': 'hours', 'hours': 'hours', 'minute': 'minutes', 'minutes': 'minutes', 'min\xadutes': 'minutes', 'day': 'days', 'days': 'days'}

                    delta = timedelta(**{unit_mapping[units]: int(value)})
                    date_obj = current_time - delta
                else:
                    date_obj = parser.parse(date)

                if start_date <= date_obj:
                    titles = self.browser.get_text(link_xpath)
                    data["Title"].append(titles)

                    description = splitted[1]
                    data["Description"].append(description)

                    data["Date"].append(date_obj)
                    count_title = titles.lower().count(self.get_search_phrase().lower())
                    count_description = description.lower().count(self.get_search_phrase().lower())
                    data["Title Count"].append(count_title)
                    data["Description Count"].append(count_description)

                    money_pattern = r'\$|\d+ dollars|\d+\s*USD'
                    money_in_title = re.search(money_pattern, titles, re.IGNORECASE)
                    money_in_description = re.search(money_pattern, description, re.IGNORECASE)

                    money_present = bool(money_in_title or money_in_description)
                    data["Money Present"].append(money_present)

                    picture_xpath = f"{link_xpath}/ancestor::div[@class='gc__card__media']//img"
                    picture_url = self.browser.get_element_attribute(picture_xpath, "src")
                    picture_filename = self.download_picture(picture_url)
                    data["Picture Filename"].append(picture_filename)

                    i += 1
                else:
                    break
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                break

        logger.info("Extracted data successfully:")
        for key, value in data.items():
            logger.info(f"{key}: {len(value)}")

        df = pd.DataFrame(data)
        logger.info(df.head())  # Log the first few rows of the DataFrame
        try:
            df.to_excel(self.excel_file, index=False)
            logger.info(f"Data saved to {self.excel_file}")
        except Exception as e:
            logger.error(f"Error saving data to Excel: {e}")

    def download_picture(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                picture_filename = os.path.basename(urlparse(url).path)
                picture_path = os.path.join(self.picture_folder, picture_filename)
                with open(picture_path, "wb") as f:
                    f.write(response.content)
                return picture_filename
            else:
                logger.warning(f"Failed to download picture from {url}")
                return ""
        except Exception as e:
            logger.error(f"Error downloading picture: {e}")
            return ""
