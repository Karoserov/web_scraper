from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup, Tag
import matplotlib.pyplot as plt
from datetime import datetime
from loguru import logger
import pandas as pd
import os
import time

# Configure logger
logger.add("scraper.log", rotation="1 day")

# Constants
EXCEL_FILE = "price_history_.xlsx" # here after history_ should put what is the name of the excel file
BASE_URL = "" # here should be the main page
url = f"{BASE_URL}/" #here after the / there should be the redirect of the main page

def setup_driver() -> webdriver.Firefox:
    """Setup and return a Firefox webdriver with proper options"""
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear
    return driver

def get_page_content(url: str) -> str:
    """Get page content using Selenium and wait for dynamic content to load"""
    driver = setup_driver()
    try:
        logger.debug(f"Accessing {url}")
        driver.get(url)
        
        # Accept cookies if present
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "js-cookie-policy-agree"))
            )
            cookie_button.click()
            logger.debug("Accepted cookies")
        except Exception:
            logger.debug("No cookie consent button found or already accepted")
        
        # Wait for product grid to load
        selectors = [
            (By.CLASS_NAME, "product"),  # Main product container
            (By.CLASS_NAME, "product__title"),  # Product title
            (By.CLASS_NAME, "product__meta"),  # Product metadata container
        ]
        
        found_selector = False
        for selector in selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(selector)
                )
                logger.debug(f"Found selector: {selector}")
                found_selector = True
                break
            except Exception:
                continue
                
        if not found_selector:
            logger.error("Could not find any product elements on the page")
            logger.debug("Current page URL: " + driver.current_url)
        
        # Scroll down to load all products
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        return driver.page_source
    except Exception as e:
        logger.error(f"Error fetching page: {str(e)}")
        if hasattr(driver, 'page_source') and driver.page_source:
            logger.debug("Page source sample:")
            logger.debug(driver.page_source[:1000])
        raise
    finally:
        driver.quit()

def clean_price(price_text: str) -> float:
    """Clean and convert price text to float"""
    try:
        # Remove currency symbol and any whitespace, then convert to float
        cleaned = price_text.replace('лв.', '').replace('$', '').replace(',', '.').strip()
        return float(cleaned)
    except ValueError as e:
        logger.error(f"Error converting price {price_text}: {str(e)}")
        return None

def load_existing_data() -> pd.DataFrame:
    """Load existing price history from Excel file"""
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=['Timestamp', 'Product', 'Price', 'URL'])

def save_to_excel(new_data: pd.DataFrame):
    """Save price data to Excel file"""
    try:
        existing_data = load_existing_data()
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        updated_data.to_excel(EXCEL_FILE, index=False)
        logger.success(f"Data saved to {EXCEL_FILE}")
    except Exception as e:
        logger.error(f"Error saving to Excel: {str(e)}")

def scrape_prices():
    """Scrape prices and save to Excel"""
    logger.info("Starting price scraping")
    try:
        # Get page content using Selenium
        page_content = get_page_content(url)
        soup = BeautifulSoup(page_content, 'html.parser')
        
        products_scraped = 0
        current_time = datetime.now()
        
        # Lists to store scraped data
        timestamps = []
        products = []
        prices = []
        urls = []

        # Find all product containers
        product_items = soup.find_all('a', class_='product')
        
        if not product_items:
            logger.debug("Trying alternative product selector...")
            product_items = soup.find_all('div', class_='product__meta')
        
        logger.debug(f"Found {len(product_items)} product items")
        
        if not product_items:
            logger.error("Could not find product items using any selector")
            logger.debug("Page content sample:")
            logger.debug(soup.prettify()[:1000])
            return False
            
        logger.debug(f"Found {len(product_items)} product items")

        for product in product_items:
            try:
                # Get product name and URL
                if isinstance(product, Tag):
                    name_elem = product.find('span', class_='product__title-inner')
                    if not name_elem:
                        continue
                        
                    name = name_elem.text.strip()
                    product_url = product.get('href', '') if product.name == 'a' else ''
                    
                    # Get price from parent elements if needed
                    price_elem = None
                    current = product
                    for _ in range(3):  # Look up to 3 levels up
                        if price_elem:
                            break
                        price_elem = current.find('span', class_='price')
                        current = current.parent
                    
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price = clean_price(price_text)
                        
                        if price and name:
                            timestamps.append(current_time)
                            products.append(name)
                            prices.append(price)
                            urls.append(product_url)
                            products_scraped += 1
                            logger.debug(f"Scraped price for {name}: {price} BGN")
                
            except Exception as e:
                logger.error(f"Error extracting product data: {str(e)}")
                continue

        if products_scraped > 0:
            # Create DataFrame with new data
            new_data = pd.DataFrame({
                'Timestamp': timestamps,
                'Product': products,
                'Price': prices,
                'URL': urls
            })
            save_to_excel(new_data)
            logger.success(f"Successfully scraped {products_scraped} products")
            return True
        else:
            logger.warning("No products were scraped")
            logger.debug(f"Page content: {soup.prettify()[:500]}...")
            return False

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return False

def generate_report():
    """Generate price trend report"""
    logger.info("Generating price report")
    try:
        df = load_existing_data()
        if df.empty:
            logger.warning("No price history found")
            return

        # Create a plot for each product
        plt.figure(figsize=(12, 8))
        for product in df['Product'].unique():
            product_data = df[df['Product'] == product]
            plt.plot(product_data['Timestamp'], product_data['Price'], 
                     label=product, marker='o')

        plt.xlabel("Date")
        plt.ylabel("Price (BGN)")
        plt.title("Product Price Trends")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("price_trends.png", dpi=300, bbox_inches='tight')
        logger.success("Price trend report generated successfully")

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")

def main():
    if scrape_prices():
        generate_report()

if __name__ == "__main__":
    main()
