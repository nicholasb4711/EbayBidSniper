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
from selenium.webdriver.common.keys import Keys

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
        """Login to eBay via Google"""
        try:
            self.driver.get('https://www.ebay.com')
            self.wait_for_element(By.LINK_TEXT, 'Sign in').click()
            
            # Click Google sign-in button
            google_signin = self.wait_for_element(By.CSS_SELECTOR, '[data-signin-type="GOOGLE"]')
            google_signin.click()
            
            # Switch to Google login popup
            windows = self.driver.window_handles
            self.driver.switch_to.window(windows[-1])
            
            # Enter Google email
            email_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="email"]')
            email_field.send_keys(username)
            email_field.send_keys(Keys.RETURN)
            
            # Enter Google password
            password_field = self.wait_for_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
            # Switch back to main window
            self.driver.switch_to.window(windows[0])
            logging.info("Successfully logged in via Google")
            
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
    # Testing Configuration
    TEST_MODE = True  # Set to False for real bidding
    TEST_ITEM_URL = "https://www.ebay.com/itm/387804040918?_skw=lego&itmmeta=01JHGN15Z602QD4VDCKPMTD6XQ&hash=item5a4aec0ed6%3Ag%3AlioAAOSw5QlnfmE6&itmprp=enc%3AAQAJAAAAwHoV3kP08IDx%2BKZ9MfhVJKnk%2BBuDhFo7iVjk3uxeSRbYSj9Wa9rVP0UZkGbRO3%2FdTYjwusOhrLq2ExLY1LIfOqyIsyjhH%2Fan9JX2o72%2BD68Pm7FOlX4DMha1xlW%2B3Xzh4WFnhev0xNjjNSHlSKsFapF5l5iUj3Q%2FUuIZDXa2cjRnFf%2FfKDMZ3EC1%2FB4tsg0tLEFy9OdM9HZ0uXvUw6MKlR5pEMR71lEw11ZANjFk5SZZR1czflimkr%2BdGhntx%2B0o8Q%3D%3D%7Ctkp%3ABk9SR-jfhJWMZQ&LH_Auction=1"
    TEST_BID = "1.00"
    MINUTES_BEFORE_END = 0.1  # 6 seconds for testing
    
    # Production Configuration
    ITEM_URL = "https://www.ebay.com/itm/326401182642"  # The eBay item you want to bid on
    MAX_BID = "430.00"  # Your maximum bid amount
    
    # Check environment variables
    EBAY_USERNAME = os.getenv("EBAY_USERNAME")
    EBAY_PASSWORD = os.getenv("EBAY_PASSWORD")
    
    if not EBAY_USERNAME or not EBAY_PASSWORD:
        logging.error("Missing environment variables. Please set EBAY_USERNAME and EBAY_PASSWORD")
        sys.exit(1)
    
    # Create and run sniper in test mode
    if TEST_MODE:
        sniper = EbayBidSniper(TEST_ITEM_URL, TEST_BID, MINUTES_BEFORE_END, test_mode=True)
        sniper.run(EBAY_USERNAME, EBAY_PASSWORD)
    else:
        sniper = EbayBidSniper(ITEM_URL, MAX_BID, MINUTES_BEFORE_END, test_mode=False)
        sniper.run(EBAY_USERNAME, EBAY_PASSWORD)