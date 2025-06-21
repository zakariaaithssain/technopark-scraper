from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging as log
from config import XPATHS
from config import CHROME_OPTIONS
from config import FALLBACKXPATHS
import os 

# YOU STILL NEED TO SCRAPE THE URLS OF STARTUPS  

technopark_url = "https://www.technopark.ma/start-ups-du-mois/"
log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                            log.FileHandler("scraper.log", mode='w'),
                            log.StreamHandler()  # shows logs in terminal
                            ]
                )

#webdriver setups
def initialize_driver():
    """
    Maximum performance configuration with headless mode
    Use this if you don't need to see the browser window
    """
    os.environ['CHROME_LOG_FILE'] = 'NUL'
    
    chrome_options = Options()
    
    # All performance options from above PLUS:
    chrome_options.add_argument('--headless')  # MAJOR performance boost
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-features=TranslateUI,VoiceInteraction,OptimizationHints')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-hang-monitor')
    chrome_options.add_argument('--disable-prompt-on-repost')
    chrome_options.add_argument('--disable-domain-reliability')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--aggressive-cache-discard')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--silent')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Headless-specific optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')  # Don't load images (faster)
    chrome_options.add_argument('--disable-javascript')  # Only if your scraping doesn't need JS
    
    service = Service()
    service.log_path = 'NUL'
    
    log.getLogger('selenium').setLevel(log.CRITICAL)
    log.getLogger('urllib3').setLevel(log.CRITICAL)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)  # Shorter timeout for faster failures
    wait = WebDriverWait(driver, 10)

    return driver, wait


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

            "description": _get_text(driver, XPATHS["description"],FALLBACKXPATHS["description"])
        }

        return startup_details
        
    except Exception as e:
        log.error(f"\nError processing current startup, exception: {e}")
        return {}
    
    finally: driver.back()


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

    except (NoSuchElementException, TimeoutException):
        log.warning("The triangle button is not found in current page!")
        return False


    
def click_startup_website_icon(driver, wait):
        #wait for and find the website's button
    wait.until(EC.presence_of_element_located((By.XPATH, XPATHS["websites_button"])))
    website_button = driver.find_element(By.XPATH, XPATHS["websites_button"])
    
    if website_button.is_displayed() and website_button.is_enabled(): 
        driver.execute_script("arguments[0].click();", website_button)
        return True
    
    else: return False

