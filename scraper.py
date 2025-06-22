from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging as log
from config import XPATHS, FALLBACKXPATHS, DATAPATH
from pandas import DataFrame
from base import BaseScraper
from kamikaze import Kamikaze

class Scraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.data = None



    def _get_startup_details(self):
            
        try:
            startup_details = {
                "name": self._get_text(XPATHS["name"], FALLBACKXPATHS["name"]),

                "sector": self._get_text(XPATHS["sector"], FALLBACKXPATHS["sector"]),

                "technologies":self._get_text(XPATHS["technologies"], FALLBACKXPATHS["technologies"]),

                "city": self._get_text(XPATHS["city"], FALLBACKXPATHS["city"]),

                "description": self._get_text(XPATHS["description"],FALLBACKXPATHS["description"])
            }

            return startup_details
            
        except Exception as e:
            log.error(f"\nError processing current startup, exception: {e}")
            return {}
        
        finally: self.driver.back()


    # to be called only inside the get_startup_details
    def _get_text(self, xpath, fallback_xpaths=None):
        try:
            return self.driver.find_element(By.XPATH, xpath).text.strip()
        except:
            if fallback_xpaths:
                for fallback in fallback_xpaths:
                    try:
                        return self.driver.find_element(By.XPATH, fallback).text.strip()
                    except:
                        continue
            return "N/A"
        
    
    def scrape(self):

        try: self.driver.get(self.main_url)
        except TimeoutException: log.error(f"Scraper: Failed to get Technopark's URL.")

        current_page = 0  # Track current page (0-indexed)
        data = []
        navigated = True  # just to start the loop.

        try:
            while navigated:
                try:
                    n_startups_in_page = self._count_page_startups()
                    for n_startup in range(n_startups_in_page):
                        # we should get the links each time because of the StaleElementReferenceException.
                        page_links = self._get_page_startups_links()
                        startup_link = page_links[n_startup]
                        self._click_startup_link(startup_link)
                        startup_details = self._get_startup_details()  # this calls driver.back() at the end, forcing us to the 1st page each time.

                        #ayo launch the kamikaze mission: I always feel excited abt this for no reason.
                        kamikaze_agent = Kamikaze()
                        kamikaze_mission_outcome = kamikaze_agent.kamikaze(current_page, n_startup)
                        startup_details.update(kamikaze_mission_outcome)

                        data.append(startup_details)
                        log.info(f'Scraper: Added "{startup_details["name"]}".')

                        # Navigate back to the correct page after driver.back() took us to page 1
                        for _ in range(current_page):
                            # Navigate forward to get back to our current page
                            navigated = self._click_the_triangle_button()
                            if not navigated:  # If we can't navigate, we've reached the end
                                break

                    # Move to next page after processing all startups on current page
                    current_page += 1
                    navigated = self._click_the_triangle_button()

                # for pages that might not contain the expected number of startups, this error is expected from the bigger 'for' loop.
                except IndexError:
                    current_page += 1
                    navigated = self._click_the_triangle_button()
                    continue
            else:
                log.info("\nScraper: SCRAPING FINISHED SUCCESSFULLY!")

        except KeyboardInterrupt:
            log.warning("Scraper: Process interrupted manually!")

        finally:
            self.driver.quit()

        self.data = data
        return self #this will enable me to "enchainer les appels" (I don't even know how to say it in eng, maybe chain?)



    def save_data(self):
        if self.data is not None: 
            try:
                df = DataFrame(self.data)
                df.to_json(path_or_buf= DATAPATH, orient= "records") #records as it contains lists.
                log.info("Scraper: Data saved to json successfully!")
            except Exception as e:
                log.error(f"Scraper: Failed to save data, exception: {e}")
        
        else:
            log.warning("Scraper: You should run the scraper first.")




