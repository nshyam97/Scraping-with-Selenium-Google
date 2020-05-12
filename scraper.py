import requests
from selenium import webdriver
from github import Github
import secrets
import time
from selenium.webdriver.chrome.options import Options
import pandas
import numpy

pandas.set_option('display.width', 1000)
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', 15)

# URL of Google Community Mobility Reports
URL = 'https://www.google.com/covid19/mobility/'
# My headers
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                         'Version/13.1 Safari/605.1.15'}


# function to download the csv from the link in the webpage
def download_csv(download_link):
    data = pandas.read_csv(download_link)
    data = data.drop('sub_region_2', axis=1)
    GB = data[(data['country_region_code'] == 'GB') & (data['sub_region_1'].isnull())]
    GB = GB.drop(['country_region_code', 'sub_region_1'], axis=1)
    # return the content of the csv file to upload to github
    return GB.to_csv(index=False)


# function to scrape the website and identify the csv link
def scrape_website():
    # Set options and choose headless = true to run the driver in headless mode
    options = Options()
    options.headless = True
    # start the Chrome webdriver
    wd = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)
    # Navigate to the URL
    wd.get(URL)
    # Find all elements by a tag to get the href we want
    links = wd.find_elements_by_tag_name('a')
    # Wait 3 seconds for the elements to be found. Can cause problems if we don't wait
    time.sleep(3)
    # Iterate through each a tag
    for link in links:
        if link.get_attribute('class') == 'icon-link':
            csv_link = link.get_attribute('href')
            # Get the content from this link
            content = download_csv(csv_link)
            # Send this content to github
            send_to_github(content)

    wd.quit()


# Send the downloaded csv file and update the file in github
def send_to_github(file):
    # Access github using token
    g = Github(secrets.token)
    # Identify the repo we want to commit to
    repo = g.get_repo('nshyam97/Google-Community-Mobility-Data')
    # Identify the file we want to update
    contents = repo.get_contents('UK_Global_Mobility_Report.csv')
    # Update and commit new contents to file
    repo.update_file(contents.path, 'file update', file, contents.sha, branch='master')


scrape_website()
