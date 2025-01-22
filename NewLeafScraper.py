from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import time
from bs4 import BeautifulSoup


#ChromeDriver set up with Service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = 'https://www.metacritic.com/game/animal-crossing-new-leaf/user-reviews/'
driver.get(url)

driver.maximize_window()

#The whole page is dynamically loaded, scroll to the bottom to load all the reviews
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(2)

    new_height = driver.execute_script("return document.body.scrollHeight")

    if(new_height == last_height):
        break

    else:
        last_height = new_height

soup = BeautifulSoup(driver.page_source, 'html.parser')

review_dict = {'name':[], 'date':[], 'rating':[], 'review':[]}

for review in soup.find_all('div', class_='c-siteReview_main'):
    try:
        review_dict['name'].append(review.find('a', class_='c-siteReviewHeader_username').text.strip())
    except AttributeError:
        review_dict['name'].append(None)
    try:
        review_dict['date'].append(review.find('div', class_='c-siteReviewHeader_reviewDate').text.strip())
    except AttributeError:
        review_dict['date'].append(None)
    try:
        review_dict['rating'].append(review.find('div', class_='c-siteReviewHeader_reviewScore').find_all('div')[0].text)
    except AttributeError:
        review_dict['rating'].append(None)
    try:
        review_dict['review'].append(review.find('div', class_='c-siteReview_quote').find('span').text)
    except AttributeError:
        review_dict['review'].append(None)

df = pd.DataFrame(review_dict)

df.to_csv('test.csv')