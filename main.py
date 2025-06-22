from scraper import Scraper




techno_scraper = Scraper()
techno_scraper.scrape().save_data() #we can chain the methods calls as I made scrape() return self.

