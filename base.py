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
import os 
from abc import ABC





class BaseScraper(ABC): 
    def __init__(self):

        log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                            log.FileHandler("scraper.log", mode='w'),
                            log.StreamHandler()  # shows logs in terminal
                            ]
                )
        self.main_url = "https://www.technopark.ma/start-ups-du-mois/"
        self.driver = None
        self.wait = None
        self._initialize_driver()



    def _initialize_driver(self):
        
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

        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(20)  # Shorter timeout for faster failures
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.set_page_load_timeout(30)

        


    def _count_page_startups(self):
        try:
            links = self.wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
            n_links = len(links)
            return n_links
        except Exception as e:
            log.error(f"Failed to count current page startups, exception: {e}")
            return 0


    def _get_page_startups_links(self):
        try: 
            voir_links = self.wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
            if voir_links: 
                return voir_links
            else: 
                log.warning("No startups found in current page.")
                return []
        except Exception as e:
            log.error(f"Failed to get startups links from current page, exception: {e}")
            return []




    def _click_startup_link(self, link):
        try: #clicking via js
            self.driver.execute_script("arguments[0].click();", link)

        except Exception: #if it didn't work, we try clicking via selenium
            link.click()
            
        except Exception as e:
            log.error(f"Both clicking methods failed to click on current startup link, exception: {e}")
        
                        

    def _click_the_triangle_button(self):
        #We will click the '>' like button to show the next pages numbers buttons.
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS["triangle_button"])))
            triangle_button = self.driver.find_element(By.XPATH, f'{XPATHS["triangle_button"]}/button')
            if triangle_button.is_displayed() and triangle_button.is_enabled(): 
                self.driver.execute_script("arguments[0].click();", triangle_button)
                return True
            
            else: return False

        except (NoSuchElementException, TimeoutException):
            log.warning("The triangle button is not found in current page!")
            return False



    
            


