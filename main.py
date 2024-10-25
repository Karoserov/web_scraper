import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import os

# URL of the page to scrape
url = "https://tavex.bg/zlato/zlatni-moneti/"

# Scraper function
def scrape_prices():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extracting product names and prices
    products = []
    prices = []

    for product in soup.find_all("div", class_="product-item"):
        name = product.find("h2").text
        price = product.find("span", class_="price").text
        products.append(name)
        prices.append(float(price.replace("$", "")))

    # Create a DataFrame with the current date
    data = pd.DataFrame({
        "Date": [datetime.datetime.now().date()] * len(products),
        "Product": products,
        "Price": prices
    })

    # Append to an Excel file
    filename = "product_prices.xlsx"
    if os.path.exists(filename):
        existing_data = pd.read_excel(filename)
        data = pd.concat([existing_data, data], ignore_index=True)

    data.to_excel(filename, index=False)

    return data

# Reporting function
def generate_report(data):
    # Load data if not provided
    if data is None:
        data = pd.read_excel("product_prices.xlsx")

    # Generate chart of price trends
    plt.figure(figsize=(10, 6))
    for product in data["Product"].unique():
        product_data = data[data["Product"] == product]
        plt.plot(product_data["Date"], product_data["Price"], label=product)

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Product Price Trends")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("price_trends.png")
    plt.show()

if __name__ == "__main__":
    data = scrape_prices()
    generate_report(data)
