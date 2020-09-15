from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import time
import pymongo
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    data = {}

    browser = init_browser()

    # Visit Nasa Mars News site
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    time.sleep(2)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')

    sidebar = soup.find('ul', class_='item_list')
    headings = sidebar.find_all('div', class_="content_title")
    paragraphs = sidebar.find_all('div', class_="article_teaser_body")

    title_list = []
    paragraph_list = []

    try:
        for heading in headings:
            title = heading.text.strip()
            title_list.append(title)
    except:
        pass

    for paragraph in paragraphs:
        description = paragraph.text.strip()
        paragraph_list.append(description)

    news_title = title_list[0]
    news_p = paragraph_list[0]

    data.update(news_title = title_list[0])
    data.update(news_p = paragraph_list[0])

    # Visit NASA Image site
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)

    browser.click_link_by_id('full_image')

    html = browser.html
    soup = bs(html, 'html.parser')

    jpl_url = 'https://www.jpl.nasa.gov'

    first_layer = soup.find('a', class_="button fancybox")
    image_url = first_layer.attrs['data-fancybox-href']

    featured_image_url = [jpl_url + image_url]

    data.update(featured_image_url = jpl_url + image_url)


    # Visit Mars Facts Site
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    facts_df = tables[0]
    facts_df = facts_df.rename(columns={0:"FACT", 1:"Details"})
    facts_df.set_index("FACT", inplace=True)
    html_table = facts_df.to_html()

    data.update(html_table = facts_df.to_html())

    # Visit Hemisphere Images Site
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    soup = bs(html, 'html.parser')

    sidebar = soup.find('div', class_='collapsible results')
    categories = sidebar.find_all('div', class_='description')

    moon_list = []
    url_list = []
    moon_url_list = []
    for category in categories:
        moon = category.find('h3').text.strip()
        moon_list.append(moon)
        moon_url = category.find('a')['href']
        url_list.append(moon_url)

    moon_url_list = ['https://astrogeology.usgs.gov' + url for url in url_list]

    img_urls = []
    for moon_url in moon_url_list:
        url = moon_url
        browser.visit(url)
        browser.click_link_by_partial_text('Open')
        html = browser.html
        soup = bs(html, 'html.parser')
        sidebar = soup.find('div', class_='container')
        category = sidebar.find('div', class_='downloads')
        moon_image = category.find('ul')
        moon_image_text = moon_image.find('a')
        moon_image_url = moon_image_text.attrs['href']
        img_urls.append(moon_image_url)

    hemisphere_image_urls = []
    for m in range(0,4):
        moon = {"title": moon_list[m], "img_url": img_urls[m]}
        hemisphere_image_urls.append(moon)
        
    data["hemisphere_image_urls"] = hemisphere_image_urls

# Close the browser after scraping
    browser.quit()

    return data

if __name__ == "__main__":
    result = scrape_info()
    print(result)






