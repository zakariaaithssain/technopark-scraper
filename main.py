from scraper import Scraper


techno_scraper = Scraper()

try: (techno_scraper.scrape()
                    .save_data()) #we can chain the methods calls as I made scrape() return self.
    
except AttributeError: pass #when scraping is stopped manually



