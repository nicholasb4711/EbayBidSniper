import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class EbayBidSniper:
    def __init__(self, item_url, max_bid, minutes_before_end=1, test_mode=False):
        self.item_url = item_url
        self.max_bid = max_bid
        self.minutes_before_end = minutes_before_end
        self.driver = None
        self.test_mode = test_mode
        
    def setup_driver(self):
        """Initialize the webdriver with proper settings"""
        options = webdriver.FirefoxOptions()
        options.add_argument('--disable-notifications')
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present and return it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.error(f"Element {value} not found within {timeout} seconds")
            self.cleanup()
            sys.exit(1)

    def login(self, username, password):
        """Login to eBay"""
        try:
            self.driver.get('https://www.ebay.com')
            self.wait_for_element(By.LINK_TEXT, 'Sign in').click()
            
            username_field = self.wait_for_element(By.ID, 'userid')
            username_field.send_keys(username)
            
            password_field = self.wait_for_element(By.ID, 'pass')
            password_field.send_keys(password)
            
            self.wait_for_element(By.ID, 'sgnBt').click()
            logging.info("Successfully logged in")
            
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            self.cleanup()
            sys.exit(1)

    def place_bid(self):
        """Place the bid on the item"""
        try:
            self.driver.get(self.item_url)
            
            # Enter bid amount
            bid_input = self.wait_for_element(By.ID, 'MaxBidId')
            bid_input.clear()
            bid_input.send_keys(self.max_bid)
            
            if self.test_mode:
                logging.info("TEST MODE: Would have placed bid of ${self.max_bid}")
                return
            
            # Click bid button
            self.wait_for_element(By.ID, 'bidBtn_btn').click()
            
            # Confirm bid
            self.wait_for_element(By.CSS_SELECTOR, "a[id*='reviewBidSec_btn']").click()
            logging.info(f"Successfully placed bid of ${self.max_bid}")
            
        except Exception as e:
            logging.error(f"Bid placement failed: {str(e)}")
            
        finally:
            time.sleep(5)  # Wait to see the result
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

    def run(self, username, password):
        """Execute the bid sniping process"""
        try:
            wait_time = self.minutes_before_end * 60
            logging.info(f"Waiting {wait_time} seconds before placing bid...")
            time.sleep(wait_time)
            
            self.setup_driver()
            self.login(username, password)
            self.place_bid()
            
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            self.cleanup()
            sys.exit(1)

if __name__ == "__main__":
    # Configuration
    TEST_ITEM_URL = "https://www.ebay.com/itm/some-low-price-item"  # Use a cheap item for testing
    TEST_BID = "1.00"
    MINUTES_BEFORE_END = 0.1  # 6 seconds for testing
    ITEM_URL = "https://www.ebay.com/itm/326401182642?_skw=power+meter+pedals&epid=20045602354&itmmeta=01JHGKGY2W56HFY9S0C2GNFR53&hash=item4bff06cbb2:g:pS4AAOSwaXpngZFU&itmprp=enc%3AAQAJAAAA8HoV3kP08IDx%2BKZ9MfhVJKnregXLyGe9q4DlJKAs5%2Bcz7d0nxgH2XlD2V2BTDgJ9iGCvKvqgkSWDHvqjbgJRP%2F%2Bg0wzus5zwWFJtai6%2FKIOwjbmhvOjnTwVzj4dEBT9Z7dTaEqiy4%2BtfNBFeuHd2LXNiiua3qFv4%2BUnkSMU2cZ0sSIwCgVTOgDDgrD2I%2BnKXDkF7lsLJJbj54BuUGRJjTaPrsQq74v6pDIczWgDBhF4vCJ7eRJ5O0ZbDBUkmZeDS4bYhncg6x2BU60UduajqHqi07GI1vIrU1jc8r5wUCEWSVyHAuX7xtFXqxdsRP6qzEg%3D%3D%7Ctkp%3ABk9SR9Dhw5OMZQ"
    MAX_BID = "430.00"  # No dollar sign needed
    MINUTES_BEFORE_END = 1
    
    # Check environment variables
    EBAY_USERNAME = os.getenv("EBAY_USERNAME")
    EBAY_PASSWORD = os.getenv("EBAY_PASSWORD")
    
    if not EBAY_USERNAME or not EBAY_PASSWORD:
        logging.error("Missing environment variables. Please set EBAY_USERNAME and EBAY_PASSWORD")
        sys.exit(1)
    
    # Create and run sniper in test mode
    sniper = EbayBidSniper(TEST_ITEM_URL, TEST_BID, MINUTES_BEFORE_END, test_mode=True)
    sniper.run(EBAY_USERNAME, EBAY_PASSWORD)