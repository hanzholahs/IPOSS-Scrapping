import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

def get_url(url, parameters):
    for key, val in parameters.items():
        val = str(val).replace(" ", "%20")
        url += f"{key}={val}&"
    return url

def get_product_links(html):
    soup = BeautifulSoup(html, "html.parser")
    data = {"data-testid": "divSRPContentProducts", "data-ssr":"contentProductsSRPSSR"}
    a_tags = soup.body.find("div", data).findAll("a")
    links = [a["href"] for a in a_tags]
    return list(set(links))

def get_product_data(html, url):
    soup = BeautifulSoup(html, "html.parser")
    price = soup.find("div", {"data-testid":"lblPDPDetailProductPrice"}).text
    name = soup.find("h1", {"data-testid":"lblPDPDetailProductName"}).text
    location = [el.text for el in soup.findAll("h2", {"data-unify":"Typography"}) if "Dikirim dari" in el.text]
    return {"url":url,
            "price": price,
            "name": name,
            "location": location}

async def main(url, n_pages):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81"

    async with async_playwright() as p:
        for browser_type in [p.webkit]:
            browser = await browser_type.launch()
            page = await browser.new_page(user_agent=ua)
            
            result = []
            
            for i in range(n_pages):
                url = get_url(url, {"q":"minyak goreng", "page": i})
                await page.goto(url)
                
                html = await page.content()
                with open(f"./pages/content-{i}.html", "w") as f:
                    f.write(html)
                    
                product_links = get_product_links(html)
                
                for link in product_links[:2]:
                    product_page = await browser.new_page(user_agent=ua)
                    await product_page.goto(link)
                    
                    product_html = await product_page.content()
                    with open(f"./pages/product.html", "w", encoding="utf-8") as f:
                        f.write(product_html)
                    
                    product_data = get_product_data(product_html, link)
                    result.append(product_data)
                    
            result = pd.DataFrame(result)
            result.to_excel("output.xslx")
                    
                
                # await page.screenshot(path=f'example-{browser_type.name}.png')
            await browser.close()


if __name__ == "__main__":
    
    url = "https://www.tokopedia.com/search?"
    n_pages = 1
    
    asyncio.run(main(url, n_pages))