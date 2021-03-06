from selenium import webdriver
from github import Github
import secrets
import time
from selenium.webdriver.chrome.options import Options
import pandas

# URL of Google Community Mobility Reports
URL = 'https://www.google.com/covid19/mobility/'
# My headers
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                         'Version/13.1 Safari/605.1.15'}


# function to download the csv from the link in the webpage
def download_csv(download_link):
    # Read csv into pandas as we need to manipulate before we commit it
    data = pandas.read_csv(download_link)
    # Remove sub region 2 column as not needed
    data = data.drop('sub_region_2', axis=1)
    # Just get the UK rows without a sub region
    GB = data[(data['country_region_code'] == 'GB')]
    # Drop unnecessary columns for export
    GB = GB.drop(['country_region_code'], axis=1)
    # return the final data frame as csv content to push to github
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
    # Get repo contents
    contents = repo.get_contents('')
    for content in contents:
        # Find the csv file within the repo
        if content.path == 'UK_Global_Mobility_Report.csv':
            # Update the file
            repo.update_file(content.path, 'file update', file, content.sha, branch='master')


scrape_website()
