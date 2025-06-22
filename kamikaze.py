import logging as log
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging as log
from config import XPATHS
import re
from base import BaseScraper

 


class Kamikaze(BaseScraper):

    def __init__(self):
        super().__init__()
        self.data = {}


    def _click_startup_website_icon(self):
            #wait for and find the website's button
        self.wait.until(EC.presence_of_element_located((By.XPATH, XPATHS["websites_button"])))
        website_button = self.driver.find_element(By.XPATH, XPATHS["websites_button"])
        
        if website_button.is_displayed() and website_button.is_enabled(): 
            self.driver.execute_script("arguments[0].click();", website_button)
            return True
        
        else: return False



    def _get_startup_contact_info(self):
        # Regular expressions for pattern matching
        phone_pattern = r'(?:\+212[\s\.\-]?(?:0)?|0)?[5-7]\d(?:[\s\.\-]?\d{2}){3}'
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        

        result = {
            'phones': set(),
            'emails': set()
        }

        page_source = self.driver.page_source
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        # Combine both sources for comprehensive search
        combined_text = page_source + " " + body_text
        
        # Extract phone numbers
        phone_matches = re.findall(phone_pattern, combined_text)
        result["phones"].update(phone_matches)
        # Extract email addresses
        emails_matches = re.findall(email_pattern, combined_text)
        result['emails'].update(emails_matches)
    
        
        # Convert sets to lists for JSON serialization
        result['phones'] = list(result['phones'])
        result['emails'] = list(result['emails'])

        # Clean up results - remove empty strings and duplicates
        result['phones'] = [p for p in result['phones'] if p.strip()]
        result['emails'] = [e for e in result['emails'] if e.strip()]

        return result
    


    def kamikaze(self, current_page, n_startup):
        #this function will create a driver that will do everything to get the startups website, and then dieeeee :) thus the name
        try:
            self.driver.get(self.main_url)
        except TimeoutException: 
            log.error("Kamikaze: Failed to get Technopark's URL.")


        for _ in range(current_page): self._click_the_triangle_button()  #navigate to the page in which we were. 

        page_links = self._get_page_startups_links()
        startup_link = page_links[n_startup]
        self._click_startup_link(startup_link)
        details_tab = self.driver.current_window_handle

        clicked_icon = self._click_startup_website_icon()
        handles = self.driver.window_handles
        
        if clicked_icon:  
            opened_tab = [tab  for tab in handles if tab != details_tab][0]     
            self.driver.switch_to.window(opened_tab)
            log.info("Kamikaze: Mission successful.")
            try: 
                startup_website = self.driver.current_url
                startup_contacts = self._get_startup_contact_info()

            except Exception as e: 
                log.warning(f"Kamikaze: Mission failed: exception: {e.msg}")
                startup_website = "N/A"
                startup_contacts = {'emails': [], "phones" : []}
        else: 
            log.info("Kamikaze: Mission failed: the startup likely doesn't have a website")
            self.driver.quit()
            startup_website = "N/A"
            startup_contacts = {"emails": [], "phones" : []}

        self.driver.quit()
        self.data['website'] = startup_website
        self.data.update(startup_contacts)
        return self.data
            
    
