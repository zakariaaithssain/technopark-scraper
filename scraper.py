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
import re
 

technopark_url = "https://www.technopark.ma/start-ups-du-mois/"

log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                            log.FileHandler("scraper.log", mode='w'),
                            log.StreamHandler()  # shows logs in terminal
                            ]
                )


def initialize_driver():
    
    os.environ['CHROME_LOG_FILE'] = 'NUL'
    
    chrome_options = Options()
    service = Service()
    service.log_path = 'NUL'
    
    log.getLogger('selenium').setLevel(log.CRITICAL)
    log.getLogger('urllib3').setLevel(log.CRITICAL)

    for key, value in CHROME_OPTIONS.items():
        if isinstance(value, tuple):
            # Handle special cases like excludeSwitches
            method_name, method_value = value
            if method_name == "excludeSwitches":
                chrome_options.add_experimental_option("excludeSwitches", method_value)
            elif method_name == "useAutomationExtension":
                chrome_options.add_experimental_option("useAutomationExtension", method_value)
        else:
            # Regular arguments
            chrome_options.add_argument(value)

    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)  # Shorter timeout for faster failures
    wait = WebDriverWait(driver, 10)
    driver.set_page_load_timeout(10)

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



def get_startup_contact_info(driver):
    # Regular expressions for pattern matching
    phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    

    result = {
        'phones': set(),
        'emails': set(),
        'addresses': set()
    }
    page_source = driver.page_source
        
    # Also get visible text
    body_text = driver.find_element(By.TAG_NAME, "body").text
    
    # Combine both sources for comprehensive search
    combined_text = page_source + " " + body_text
    
    # Extract phone numbers
    phone_matches = re.findall(phone_pattern, combined_text)
    for match in phone_matches:
        if isinstance(match, tuple):
            phone = f"({match[0]}) {match[1]}-{match[2]}"
        else:
            phone = match
        result['phones'].add(phone)
    
    # Also look for other phone formats
    other_phone_patterns = [
        r'(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}',
        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
    ]
    
    for pattern in other_phone_patterns:
        phones = re.findall(pattern, combined_text)
        for phone in phones:
            # Clean up the phone number
            clean_phone = re.sub(r'[^\d+]', '', phone)
            if 10 <= len(clean_phone) <= 12:  # Valid phone length
                result['phones'].add(phone)
    
    # Extract email addresses
    emails = re.findall(email_pattern, combined_text)
    result['emails'].update(emails)
    
    # Extract addresses
    try:
        addresses = driver.find_element(By.TAG_NAME, "Adresse").text.strip()
        result['addresses'].update(addresses)

        addresses2 = driver.find_element(By.TAG_NAME, "adresse").text.strip()
        result['addresses'].update(addresses2)

        # Look for common address indicators in structured data
        address_elements = driver.find_elements(By.CSS_SELECTOR, 
            "[class*='address'], [class*='location'], [id*='address'], [id*='location']")
        
        for element in address_elements:
            text = element.text.strip()
            if text and len(text) > 10:  # Basic filter for meaningful addresses
                result['addresses'].add(text)
    
        
    except NoSuchElementException: pass

    
    # Convert sets to lists for JSON serialization
    result['phones'] = list(result['phones'])
    result['emails'] = list(result['emails'])
    result['addresses'] = list(result['addresses'])
    
    # Clean up results - remove empty strings and duplicates
    result['phones'] = [p for p in result['phones'] if p.strip()]
    result['emails'] = [e for e in result['emails'] if e.strip()]
    result['addresses'] = [a for a in result['addresses'] if a.strip()]

    return result