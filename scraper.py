from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd 
import logging as log
from config import XPATHS
from config import CHROME_OPTIONS
from config import FALLBACKXPATHS


technopark_url = "https://www.technopark.ma/start-ups-du-mois/"
log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='scraper.log')

#webdriver setups
def initialize_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument(CHROME_OPTIONS["disable_automation_flag"])
        log.info("Automation flag disabled.")

        options.add_argument(CHROME_OPTIONS["custom_user_agent"])
        log.info("User agent customized.")
        
        options.add_argument(CHROME_OPTIONS["headless_mode"])
        log.info("Headless mode activated.")
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        log.error(f"Failed to initialize the webdriver, exception: {e}")
    


def count_page_startups(wait):
    try:
        links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
        n_links = len(links)
        return n_links
    except Exception as e:
        log.error(f"Failed to count current page startups, exception: {e}")
        return 0


def get_page_startups_links(wait):
    try: 
        voir_links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
        if voir_links: 
            return voir_links
        else: 
            log.warning("No startups found in current page.")
            return []
    except Exception as e:
        log.error(f"Failed to get startups links from current page, exception: {e}")
        return []




def click_startup_link(driver, link):
    try: #clicking via js
        driver.execute_script("arguments[0].click();", link)

    except Exception: #if it didn't work, we try clicking via selenium
        link.click()
        
    except Exception as e:
        log.error(f"Both clicking methods failed to click on current startup link, exception: {e}")
    
                    
def get_startup_details(driver):
        
    try:
        startup_details = {
            "name": _get_text(driver, XPATHS["name"], FALLBACKXPATHS["name"]),

            "sector": _get_text(driver, XPATHS["sector"], FALLBACKXPATHS["sector"]),

            "technologies": _get_text(driver, XPATHS["technologies"], FALLBACKXPATHS["technologies"]),

            "city": _get_text(driver, XPATHS["city"], FALLBACKXPATHS["city"]),

            "description": _get_text(driver, XPATHS["description"],FALLBACKXPATHS["description"]),
        }
        
        return startup_details
        
    except Exception as e:
        log.error(f"\nError processing current startup, exception: {e}")
        return {}
    
    finally: #this is used to go back from the startup details to the page containing the rest of startups.
        driver.back() 




# to be called only inside the get_startup_details
def _get_text(driver, xpath, fallback_xpaths=None):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        if fallback_xpaths:
            for fallback in fallback_xpaths:
                try:
                    return driver.find_element(By.XPATH, fallback).text.strip()
                except:
                    continue
        return "N/A"




def click_the_triangle_button(driver, wait):
    #We will click the '>' like button to show the next pages numbers buttons.
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, XPATHS["triangle_button"])))
        triangle_button = driver.find_element(By.XPATH, f'{XPATHS["triangle_button"]}/button')
        if triangle_button.is_displayed() and triangle_button.is_enabled(): 
            driver.execute_script("arguments[0].click();", triangle_button)
            return True
        
        else: return False

    except NoSuchElementException:
        log.warning("The triangle button is not found in current page!")
        return False
    





def run_scraping():
    driver = initialize_driver()
    try:
     driver.get(technopark_url)
    except Exception as e: 
        log.error(f"Failed to get: {technopark_url} \nException: {e}")

    wait = WebDriverWait(driver, 10)
    n_pages = 0
    data = []
    navigated = True #just to start the loop.

    try:
        while navigated:
            
            try:
                n_startups_in_page = count_page_startups(wait)
                log.info(f"\n The number of startups found in page {n_pages + 1} is: {n_startups_in_page} ")

                for n_startup in range(n_startups_in_page):
                    #we should get the links each time because of the StaleElementReferenceException.
                    page_links = get_page_startups_links(wait)
                    startup_link = page_links[n_startup]
                    click_startup_link(driver, startup_link)
                    startup_details = get_startup_details(driver) #this calls driver.back() at the end, forcing us to the 1st page each time.
                    data.append(startup_details)
                    log.info(f'Added "{startup_details["name"]}".')
                    
                    #this loop enables us to go back to the page we are fetching as the driver.back() takes us to the very 1st page each time.
                    for n_page in range(n_pages): 
                        #this will be false when the triangle button is no longer clickable ( we reached the final page, thus stop the loop).
                        navigated = click_the_triangle_button(driver, wait)
                
                #we are done with one page.  
                n_pages +=1

    #for pages that might not contain the expected the number of startups, this error is expected from the bigger 'for' loop.
            except IndexError: 
                navigated = click_the_triangle_button(driver, wait)
                continue
        else:
            log.info("\n SCRAPING FINISHED SUCCESSFULLY!")


    except KeyboardInterrupt:
        log.warning(" Process interrupted manually!")

    finally:
        driver.quit()

    data_without_duplicates = [dict(t) for t in set(tuple(sorted(d.items())) for d in data)]
    log.info(f"Number of unique startups: { len(data_without_duplicates)}")

    return data


def save_data(data):
    try:
        df = pd.DataFrame(data= data, columns=["name", "sector", "technologies", "city", "description"])
        df.to_json(path_or_buf= "data/technopark_startups.json", orient= "records")
        log.info("Data saved successfully!")
    except Exception as e:
        log.error(f"Enable to save data, because of the following exception: {e}")
    

data = run_scraping()
save_data(data)




