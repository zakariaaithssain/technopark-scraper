# config.py
#contains the xpaths for more reliability.
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