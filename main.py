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
import random
from fake_useragent import UserAgent
import random
from fake_useragent import UserAgent

# Configure logger
logger.add("scraper.log", rotation="1 day")

# Constants
EXCEL_FILE = "price_history_.xlsx" # here after history_ should put what is the name of the excel file
BASE_URL = "https://" # here should be the main page and should start with https:
url = f"{BASE_URL}/" #here after the / there should be the redirect of the main page

def setup_driver() -> webdriver.Firefox:
    """Setup and return a Firefox webdriver with proper options"""
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    
    # Generate random user agent
    try:
        ua = UserAgent()
        user_agent = ua.random
    except Exception:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    firefox_options.add_argument(f'user-agent={user_agent}')
    
    # Add additional Firefox preferences to make it more browser-like
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference('useAutomationExtension', False)
    
    # Generate random user agent
    try:
        ua = UserAgent()
        user_agent = ua.random
    except Exception:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    firefox_options.add_argument(f'user-agent={user_agent}')
    
    # Add additional Firefox preferences to make it more browser-like
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference('useAutomationExtension', False)
    
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    # Set longer timeout for slower connections
    driver.implicitly_wait(15)  # Wait up to 15 seconds for elements to appear
    
    # Set window size to a common desktop resolution
    driver.set_window_size(1920, 1080)
    
    
    # Set longer timeout for slower connections
    driver.implicitly_wait(15)  # Wait up to 15 seconds for elements to appear
    
    # Set window size to a common desktop resolution
    driver.set_window_size(1920, 1080)
    
    return driver

def get_page_content(url: str) -> str:
    """Get page content using Selenium and wait for dynamic content to load"""
    driver = setup_driver()
    try:
        logger.debug(f"Accessing {url}")
        
        # Add random delay before accessing the page (2-5 seconds)
        time.sleep(random.uniform(2, 5))
        
        
        # Add random delay before accessing the page (2-5 seconds)
        time.sleep(random.uniform(2, 5))
        
        driver.get(url)
        
        # Add random scroll behavior to simulate human browsing
        scroll_pause_time = random.uniform(0.5, 1.5)
        screen_heights = [0.3, 0.5, 0.7, 1.0]  # Partial scroll heights
        
        # Add random scroll behavior to simulate human browsing
        scroll_pause_time = random.uniform(0.5, 1.5)
        screen_heights = [0.3, 0.5, 0.7, 1.0]  # Partial scroll heights
        
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
        
        # Scroll down gradually with random pauses to simulate human behavior
        # Scroll down gradually with random pauses to simulate human behavior
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for scroll_height in screen_heights:
            # Scroll to a percentage of the page height
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_height});")
            time.sleep(scroll_pause_time)
        
        # Final scroll to bottom
        
        for scroll_height in screen_heights:
            # Scroll to a percentage of the page height
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_height});")
            time.sleep(scroll_pause_time)
        
        # Final scroll to bottom
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            time.sleep(random.uniform(1, 2))
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        # Add a final wait to ensure all dynamic content is loaded
        time.sleep(random.uniform(3, 5))
            
        # Add a final wait to ensure all dynamic content is loaded
        time.sleep(random.uniform(3, 5))
        
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
    return pd.DataFrame(columns=['Timestamp', 'Product', 'Buying_Price', 'Selling_Price', 'URL']).reindex(columns=['Timestamp', 'Product', 'Selling_Price', 'Buying_Price', 'URL'])
    return pd.DataFrame(columns=['Timestamp', 'Product', 'Buying_Price', 'Selling_Price', 'URL']).reindex(columns=['Timestamp', 'Product', 'Selling_Price', 'Buying_Price', 'URL'])

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
        selling_prices = []
        buying_prices = []
        selling_prices = []
        buying_prices = []
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
                    
                    # Check if product is out of stock
                    out_of_stock_elem = product.find('span', class_='product__out-of-stock')
                    is_out_of_stock = False
                    if out_of_stock_elem and 'Изчерпан' in out_of_stock_elem.text.strip():
                        is_out_of_stock = True
                        logger.debug(f"Product {name} is out of stock")

                    # Get buying price (from the element marked as selling price)
                    buying_price_elem = product.find('span', class_='js-product-price-from')
                    if not is_out_of_stock and not buying_price_elem:
                        logger.debug(f"Could not find buying price for product with name: {name}")
                        continue

                    # Get selling price (from the element marked as buying price)
                    selling_price_elem = product.find('span', class_='js-product-price-buy')
                    if not selling_price_elem:
                        logger.debug(f"Could not find selling price for product with name: {name}")
                        continue

                    selling_price = None
                    buying_price = None
                    
                    # Extract buying price if not out of stock
                    buying_price = None
                    if not is_out_of_stock:
                        buying_price_text = buying_price_elem.text.strip()
                        buying_price = clean_price(buying_price_text)
                        if not buying_price:
                            # Try to get price from data attribute if text parsing fails
                            try:
                                price_data = buying_price_elem.get('data-pricelist')
                                if price_data:
                                    import json
                                    price_info = json.loads(price_data)
                                    buying_price = float(price_info['sell'][0]['price'])
                            except Exception as e:
                                logger.debug(f"Could not parse buying price from data attribute: {e}")
                        
                        if not buying_price:
                            logger.debug(f"Could not parse buying price text: {buying_price_text} for product: {name}")
                            continue
                    
                    # Extract selling price - first try to find the price-amount-whole element
                    selling_price_whole_elem = selling_price_elem.find('span', class_='price-amount-whole')
                    if selling_price_whole_elem:
                        selling_price_text = selling_price_whole_elem.text.strip()
                        # Add decimals if they exist
                        fraction_elem = selling_price_elem.find('span', class_='price-amount-fraction')
                        if fraction_elem:
                            selling_price_text += '.' + fraction_elem.text.strip()
                        try:
                            selling_price = float(selling_price_text)
                        except ValueError:
                            logger.debug(f"Could not convert selling price text to float: {selling_price_text}")
                    # Check if product is out of stock
                    out_of_stock_elem = product.find('span', class_='product__out-of-stock')
                    is_out_of_stock = False
                    if out_of_stock_elem and 'Изчерпан' in out_of_stock_elem.text.strip():
                        is_out_of_stock = True
                        logger.debug(f"Product {name} is out of stock")

                    # Get buying price (from the element marked as selling price)
                    buying_price_elem = product.find('span', class_='js-product-price-from')
                    if not is_out_of_stock and not buying_price_elem:
                        logger.debug(f"Could not find buying price for product with name: {name}")
                        continue

                    # Get selling price (from the element marked as buying price)
                    selling_price_elem = product.find('span', class_='js-product-price-buy')
                    if not selling_price_elem:
                        logger.debug(f"Could not find selling price for product with name: {name}")
                        continue

                    selling_price = None
                    buying_price = None
                    
                    # Extract buying price if not out of stock
                    buying_price = None
                    if not is_out_of_stock:
                        buying_price_text = buying_price_elem.text.strip()
                        buying_price = clean_price(buying_price_text)
                        if not buying_price:
                            # Try to get price from data attribute if text parsing fails
                            try:
                                price_data = buying_price_elem.get('data-pricelist')
                                if price_data:
                                    import json
                                    price_info = json.loads(price_data)
                                    buying_price = float(price_info['sell'][0]['price'])
                            except Exception as e:
                                logger.debug(f"Could not parse buying price from data attribute: {e}")
                        
                        if not buying_price:
                            logger.debug(f"Could not parse buying price text: {buying_price_text} for product: {name}")
                            continue
                    
                    # Extract selling price - first try to find the price-amount-whole element
                    selling_price_whole_elem = selling_price_elem.find('span', class_='price-amount-whole')
                    if selling_price_whole_elem:
                        selling_price_text = selling_price_whole_elem.text.strip()
                        # Add decimals if they exist
                        fraction_elem = selling_price_elem.find('span', class_='price-amount-fraction')
                        if fraction_elem:
                            selling_price_text += '.' + fraction_elem.text.strip()
                        try:
                            selling_price = float(selling_price_text)
                        except ValueError:
                            logger.debug(f"Could not convert selling price text to float: {selling_price_text}")
                    
                    if not selling_price:
                        # Fallback to regular text parsing if structured elements aren't found
                        selling_price_text = selling_price_elem.text.strip()
                        selling_price = clean_price(selling_price_text)
                    
                    if not selling_price:
                        logger.debug(f"Could not parse selling price text: {selling_price_text} for product: {name}")
                        continue
                    
                    # If we have all the data, add it to our lists
                    timestamps.append(current_time)
                    products.append(name)
                    selling_prices.append(selling_price)
                    buying_prices.append(None if is_out_of_stock else buying_price)
                    urls.append(product_url)
                    products_scraped += 1
                    if is_out_of_stock:
                        logger.debug(f"Successfully scraped out of stock product {name}: Selling: {selling_price} BGN")
                    else:
                        logger.debug(f"Successfully scraped prices for {name}: Selling: {selling_price} BGN, Buying: {buying_price} BGN")
                    if not selling_price:
                        # Fallback to regular text parsing if structured elements aren't found
                        selling_price_text = selling_price_elem.text.strip()
                        selling_price = clean_price(selling_price_text)
                    
                    if not selling_price:
                        logger.debug(f"Could not parse selling price text: {selling_price_text} for product: {name}")
                        continue
                    
                    # If we have all the data, add it to our lists
                    timestamps.append(current_time)
                    products.append(name)
                    selling_prices.append(selling_price)
                    buying_prices.append(None if is_out_of_stock else buying_price)
                    urls.append(product_url)
                    products_scraped += 1
                    if is_out_of_stock:
                        logger.debug(f"Successfully scraped out of stock product {name}: Selling: {selling_price} BGN")
                    else:
                        logger.debug(f"Successfully scraped prices for {name}: Selling: {selling_price} BGN, Buying: {buying_price} BGN")
                
            except Exception as e:
                logger.error(f"Error extracting product data: {str(e)}")
                continue

        if products_scraped > 0:
            # Create DataFrame with new data
            new_data = pd.DataFrame({
                'Timestamp': timestamps,
                'Product': products,
                'Selling_Price': selling_prices,
                'Buying_Price': buying_prices,
                'Selling_Price': selling_prices,
                'Buying_Price': buying_prices,
                'URL': urls
            }).reindex(columns=['Timestamp', 'Product', 'Selling_Price', 'Buying_Price', 'URL'])
            }).reindex(columns=['Timestamp', 'Product', 'Selling_Price', 'Buying_Price', 'URL'])
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
            # Plot selling price
            plt.plot(product_data['Timestamp'], product_data['Selling_Price'], 
                     label=f"{product} (Selling)", marker='o')
            # Plot buying price
            plt.plot(product_data['Timestamp'], product_data['Buying_Price'], 
                     label=f"{product} (Buying)", marker='s')
            # Plot selling price
            plt.plot(product_data['Timestamp'], product_data['Selling_Price'], 
                     label=f"{product} (Selling)", marker='o')
            # Plot buying price
            plt.plot(product_data['Timestamp'], product_data['Buying_Price'], 
                     label=f"{product} (Buying)", marker='s')

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