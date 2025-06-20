url = "https://www.metacritic.com/game/animal-crossing-new-horizons/user-reviews/?platform=nintendo-switch"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import time
from bs4 import BeautifulSoup

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.maximize_window()

driver.get(url)

#close the cookie window
try:
    time.sleep(2)
    cookie_reject = driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
    cookie_reject.click()
except:
    print("no cookie popup")


#since the page is dynamically loaded, scroll down to load in all the reviews first
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(2)

    new_height = driver.execute_script("return document.body.scrollHeight")

    if(new_height == last_height):
        break

    else:
        last_height = new_height

#prep the data structure
review_dict = {
    'name':[], 
    'date':[], 
    'rating':[], 
    'review':[]}

#find all review 'containers' then iterate through them all to scrape
containers = driver.find_elements(By.CLASS_NAME, 'c-siteReview_main')

for i in range(len(containers)):
    #in case the DOM changes after opening a pop-up, find the containers again
    containers = driver.find_elements(By.CLASS_NAME, 'c-siteReview_main')
    container = containers[i]

    container_html = container.get_attribute('outerHTML')
    soup_short = BeautifulSoup(container_html, 'html.parser')

    soup_short_el = soup_short.find('div', class_='c-siteReview_quote')
    if soup_short_el:
        soup_short_span = soup_short_el.find('span')
        short_text = soup_short_span.text.strip() if soup_short_span else ""
    else:
        short_text = ""

    #check if spoiler tag is in short text
    if '[SPOILER ALERT: This review contains spoilers.]' in short_text:
        try:
            read_more_btn = container.find_element(By.XPATH, './/button[@data-testid="global-button"]')
            read_more_btn.click()
            wait = WebDriverWait(driver, 10)
            modal_wrapper = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-globalModal_wrapper")))

            #parse the pop-up with BeautifulSoup
            soup_pop = BeautifulSoup(driver.page_source, 'html.parser')
            popup = soup_pop.find('div', class_='c-globalModal_wrapper')
            
            print("spoiler review found and parsed")

            if popup:
                name_pop = popup.find('a', class_='c-siteReviewHeader_username').text.strip()
                date_pop = popup.find('div', class_='c-siteReviewHeader_reviewDate').text.strip()
                rating_pop = popup.find('div', class_='c-siteReviewHeader_reviewScore').find_all('div')[0].text.strip()
                text_pop = popup.find('div', class_='c-siteReviewReadMore_wrapper').text.strip()
                
                print(name_pop, date_pop, rating_pop, text_pop)

                review_dict['name'].append(name_pop)
                review_dict['date'].append(date_pop)
                review_dict['rating'].append(rating_pop)
                review_dict['review'].append(text_pop)

            #close the pop-up
            try:
                #wait for the parent <div> to be present and clickable
                close_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="c-globalModal_closeButtonWrapper"]')))
                
                #use javascript click if normal click fails
                driver.execute_script("arguments[0].click();", close_div)
                print("Pop-up closed!")

            except Exception as e:
                print("could not close window", e)

        except Exception as e:
            print(f"could not open spoiler for container {i}: {e}")

    else:
        #if there is no spoiler tag just parse the text as normal

        review_dict['name'].append(soup_short.find('a', class_='c-siteReviewHeader_username').text.strip())
        review_dict['date'].append(soup_short.find('div', class_='c-siteReviewHeader_reviewDate').text.strip())
        review_dict['rating'].append(soup_short.find('div', class_='c-siteReviewHeader_reviewScore').find_all('div')[0].text)
        review_dict['review'].append(soup_short.find('div', class_='c-siteReview_quote').find('span').text.strip())


df = pd.DataFrame(review_dict)

save_path = r"C:\Users\Philippa\Documents\GitHub\webscraper\NH_Parsed_Reviews.csv"

df.to_csv(save_path, index=False, encoding='utf-8')

driver.quit()

    

