# config.py
#contains the xpaths, fallback xpaths, and the driver's options.
XPATHS = {
    "triangle_button": '//*[@id="root"]/div/div/div/div[2]/div[3]/nav/ul/li[9]',
    "name" : "//*[@id='root']/div/div/div/div/div/div[2]/div[1]/h2",
    "sector": "//div[2]/div[2]/p",
    "technologies": "//div[2]/div[3]/p",
    "city": "//div[2]/div[4]/p",
    "description": "//div[2]/div[5]//p"
}

FALLBACKXPATHS  = {"name" : None, 
                   "sector" : ["//div[contains(@class, 'sector')]//p"],
                   "technologies" : ["//div[contains(@class, 'tech')]//p"], 
                   "city" : ["//div[contains(@class, 'city')]//p"], 
                   "description" : ["//div[contains(@class, 'description')]//p"]}


CHROME_OPTIONS = {
    # Avoid Selenium detection
    "disable_automation_flag": "--disable-blink-lvl_features=AutomationControlled",  
     # Custom browser identity
    "custom_user_agent": "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36", 
    # Run driver without GUI (with the last version of headless mode)
    "headless_mode": "--headless=new"  
}
