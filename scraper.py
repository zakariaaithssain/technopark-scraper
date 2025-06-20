from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd 


technopark_url = "https://www.technopark.ma/start-ups-du-mois/"

#webdriver setups
def initialize_driver():
    options = webdriver.ChromeOptions()
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-lvl_features=AutomationControlled')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36')
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    return driver
    


def count_page_startups(wait):
    try:
        links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
        n_links = len(links)
        return n_links
    except Exception as e:
        print(f"Failed to count current page startups, exception: {e}")
        return 0


def get_page_startups_links(wait):
    try: 
        voir_links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
        if voir_links: 
            return voir_links
        else: 
            print("No startups found in current page!")
            return []
    except Exception as e:
        print(f"Failed to get startups links from current page, exception: {e}")
        return []




def click_startup_link(driver, link):
    try: #clicking via js
        driver.execute_script("arguments[0].click();", link)

    except Exception as js_error: #if it didn't work, we try clicking via selenium
        link.click()
        
    except Exception as e:
        print(f"Both clicking methods failed to click on current startup link, exception: {e}")
    
                    
def get_startup_details(driver):
        
    try:
        startup_details = {
            "name": _get_text(driver, "/html/body/div/div/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div/div/div/div/div[2]/div[1]/h2"),
            "sector": _get_text(driver, "//div[2]/div[2]/p", ["//div[contains(@class, 'sector')]//p"]),
            "technologies": _get_text(driver, "//div[2]/div[3]/p", ["//div[contains(@class, 'tech')]//p"]),
            "city": _get_text(driver, "//div[2]/div[4]/p", ["//div[contains(@class, 'city')]//p"]),
            "description": _get_text(driver, "//div[2]/div[5]//p", ["//div[contains(@class, 'description')]//p"]),
        }
        
        return startup_details
        
    except Exception as e:
        print(f"\nError processing current startup, exception: {e}")
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
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div[2]/div[3]/nav/ul/li[9]')))
        triangle_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div[2]/div[3]/nav/ul/li[9]/button')
        if triangle_button.is_displayed() and triangle_button.is_enabled(): 
            driver.execute_script("arguments[0].click();", triangle_button)
            return True
        
        else: return False

    except NoSuchElementException:
        print("The triangle button is not found in current page!")
        return False
    





def run_scraping():
    driver = initialize_driver()
    driver.get(technopark_url)
    wait = WebDriverWait(driver, 10)
    n_pages = 0
    data = []
    navigated = True #just to start the loop.

    try:

        while navigated:
            
            try:
                n_startups_in_page = count_page_startups(wait)
                print(f"\n#################### The number of startups found in page {n_pages + 1}: {n_startups_in_page} ####################")

                for n_startup in range(n_startups_in_page):
                    #we should get the links each time because of the StaleElementReferenceException.
                    page_links = get_page_startups_links(wait)
                    startup_link = page_links[n_startup]
                    click_startup_link(driver, startup_link)
                    startup_details = get_startup_details(driver) #this calls driver.back() at the end, forcing us to the 1st page each time.
                    data.append(startup_details)
                    print(f'"{startup_details["name"]}" details are successfully added!')
                    
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
            print("\n \n #################### SCRAPING FINISHED SUCCESSFULLY ! #####################")


    except KeyboardInterrupt:
        print("#################### You interrupted the process! ####################")

    finally:
        driver.quit()

    print("Number of startups with duplications: ", len(data))

    data_without_duplicates = [dict(t) for t in set(tuple(sorted(d.items())) for d in data)]
    print("Number of unique startups: ", len(data_without_duplicates))

    return data


def save_data(data):
    try:
        df = pd.DataFrame(data= data, columns=["name", "sector", "technologies", "city", "description"])
        df.to_json(path_or_buf= "data/technopark_startups.json", orient= "records")
        print("Data saved successfully!")
    except Exception as e:
        print("Enable to save data, because of the following exception: ", e)
    

data = run_scraping()
save_data(data)




