from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
import time
import re
import json 

# WebDriver setup
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36')
# options.add_argument('--headless=new')  # Uncomment for headless mode

driver = webdriver.Chrome(options=options)
technopark_url = "https://www.technopark.ma/start-ups-du-mois/"
driver.get(technopark_url)
wait = WebDriverWait(driver, 10)

def get_text(xpath, fallback_xpaths=None):
    """Extract text from element using XPath with fallback options"""
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

def get_page_signature():
    """Get a unique signature of the current page to detect changes"""
    try:
        # Method 1: Get first few 'Voir Détails' links to identify page content
        voir_links = driver.find_elements(By.LINK_TEXT, "Voir Détails")
        
        # Method 2: Get image sources if available
        imgs = driver.find_elements(By.XPATH, "//*[@id='root']/div/div/div/div[2]/div[2]/div[9]/div[1]/span/img")
        img_sources = [img.get_attribute('src') for img in imgs[:3] if img.get_attribute('src')]
        
        # Method 3: Get any text content that might indicate page differences
        text_elements = driver.find_elements(By.XPATH, "//h2 | //h3 | //h4")
        text_content = [elem.text.strip() for elem in text_elements[:5] if elem.text.strip()]
        
        # Method 4: Check URL for page parameters
        current_url = driver.current_url
        
        signature = {
            'voir_links_count': len(voir_links),
            'img_sources': img_sources,
            'text_content': text_content,
            'url': current_url,
            'timestamp': time.time()
        }
        
        print(f"Page signature: {len(voir_links)} 'Voir Détails' links, {len(img_sources)} images, {len(text_content)} text elements")
        if text_content:
            print(f"First text element: '{text_content[0]}'")
        
        return signature
        
    except Exception as e:
        print(f"Error getting page signature: {e}")
        return {'error': str(e), 'timestamp': time.time()}

def wait_for_page_change(old_signature, max_wait=30):
    """Wait for page content to actually change"""
    print("Waiting for page content to change...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        time.sleep(2)
        new_signature = get_page_signature()
        
        # Compare signatures
        if new_signature.get('voir_links_count') != old_signature.get('voir_links_count'):
            print("✅ Page content changed (different number of 'Voir Détails' links)")
            return True
            
        if new_signature.get('img_sources') != old_signature.get('img_sources'):
            print("✅ Page content changed (different images)")
            return True
            
        if new_signature.get('text_content') != old_signature.get('text_content'):
            print("✅ Page content changed (different text content)")
            return True
            
        if new_signature.get('url') != old_signature.get('url'):
            print("✅ Page content changed (different URL)")
            return True
            
        print(f"⏳ Content unchanged, waiting... ({int(time.time() - start_time)}s)")
    
    print("❌ Timeout: Page content did not change")
    return False

def get_one_page_startups_details():
    """Extract startup details from current page"""
    startups_list = []
    
    try:
        # Wait for page to load completely
        print("🔍 Waiting for page to load...")
        time.sleep(3)
        
        # Find the total number of startups on current page
        voir_links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
        total = len(voir_links)
        print(f"Total 'Voir Détails' links found on this page: {total}")
        
        if total == 0:
            print("⚠️ No 'Voir Détails' links found on this page")
            return []
        
        for i in range(total):
            try:
                print(f"\n--- Processing startup {i+1}/{total} ---")
                
                # Re-find the links after each navigation back
                voir_links = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, "Voir Détails")))
                
                if i >= len(voir_links):
                    print(f"Link {i+1} no longer exists, skipping...")
                    continue
                
                # Get the current link
                link = voir_links[i]
                
                # Scroll to element
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(1)
                
                # Click using JavaScript (more reliable)
                try:
                    driver.execute_script("arguments[0].click();", link)
                    print(f"✓ Clicked on startup {i+1} using JavaScript")
                except Exception as js_error:
                    print(f"JS click failed: {js_error}")
                    link.click()
                    print(f"✓ Clicked on startup {i+1} using Selenium")
                
                # Wait for the detail page to load
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                    time.sleep(2)  # Additional wait for content to load
                except TimeoutException:
                    print(f"❌ Timeout waiting for detail page {i+1}")
                    driver.back()
                    time.sleep(2)
                    continue
                
                # Extract startup details
                startup_details = {
                    "page_number": "current",  # Will be updated by main function
                    "startup_index": i + 1,
                    "name": get_text("/html/body/div/div/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div/div/div/div/div[2]/div[1]/h2"),
                    "sector": get_text("//div[2]/div[2]/p", ["//div[contains(@class, 'sector')]//p"]),
                    "technologies": get_text("//div[2]/div[3]/p", ["//div[contains(@class, 'tech')]//p"]),
                    "city": get_text("//div[2]/div[4]/p", ["//div[contains(@class, 'city')]//p"]),
                    "description": get_text("//div[2]/div[5]//p", ["//div[contains(@class, 'description')]//p"]),
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print(f"✅ Startup {i+1} fetched: {startup_details['name']}")
                startups_list.append(startup_details)
                
            except Exception as e:
                print(f"❌ Error processing startup {i+1}: {e}")
            
            finally:
                try:
                    # Navigate back to the main page
                    driver.back()
                    time.sleep(2)
                    
                    # Wait for the main page to load
                    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Voir Détails")))
                    
                except Exception as back_error:
                    print(f"Error navigating back: {back_error}")
                    # Fallback: reload the main page
                    driver.get("https://www.technopark.ma/start-ups-du-mois")
                    time.sleep(3)
        
        print(f"🎯 Successfully extracted {len(startups_list)} startups from this page")
        return startups_list
        
    except Exception as e:
        print(f"❌ Error in get_one_page_startups_details: {e}")
        return []

def navigate_to_next_page_with_validation():
    """Navigate to next page with validation that content actually changed"""
    
    # Get current page signature BEFORE navigation
    old_signature = get_page_signature()
    print(f"\n--- BEFORE NAVIGATION ---")
    print(f"Current page has {old_signature.get('voir_links_count', 0)} startups")
    
    try:
        # Wait for next button
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div/div/div/div[2]/div[3]/nav/ul/li[9]")))
        next_button = driver.find_element(By.XPATH, "//*[@id='root']/div/div/div/div[2]/div[3]/nav/ul/li[9]/button")
        
        print(f"Button state - Enabled: {next_button.is_enabled()}, Displayed: {next_button.is_displayed()}")
        print(f"Button text: '{next_button.text}'")
        
        if not next_button.is_enabled() or not next_button.is_displayed():
            print("Next button not available - end of pages")
            return False
        
        # Scroll and click
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
        time.sleep(1)
        
        print("Clicking next button...")
        try:
            driver.execute_script("arguments[0].click();", next_button)
            print("✓ Clicked with JavaScript")
        except Exception as e:
            print(f"JS click failed: {e}, trying Selenium")
            next_button.click()
            print("✓ Clicked with Selenium")
        
        # CRITICAL: Wait for actual page change, not just loading
        if wait_for_page_change(old_signature, max_wait=30):
            print("✅ Navigation successful - page content changed")
            
            # Additional wait for content to fully load
            time.sleep(3)
            
            # Verify we have new content
            new_signature = get_page_signature()
            print(f"\n--- AFTER NAVIGATION ---")
            print(f"New page has {new_signature.get('voir_links_count', 0)} startups")
            
            return True
        else:
            print("❌ Navigation failed - page content did not change")
            print("This indicates the pagination might not be working correctly")
            return False
            
    except TimeoutException:
        print("❌ Timeout waiting for navigation elements")
        return False
    except Exception as e:
        print(f"❌ Navigation error: {e}")
        return False

def get_all_startups_details():
    """Main function to scrape all startup details with page change validation"""
    
    all_startups = []
    page_count = 0
    seen_signatures = set()  # Track seen content to avoid duplicates
    
    print("🚀 Starting Technopark startup data collection...")
    print(f"Initial URL: {driver.current_url}")
    
    while True:
        page_count += 1
        print(f"\n{'='*60}")
        print(f"PROCESSING PAGE {page_count}")
        print(f"{'='*60}")
        
        # Get current page signature
        current_signature = get_page_signature()
        signature_key = f"{current_signature.get('voir_links_count', 0)}-{str(sorted(current_signature.get('text_content', [])))}"
        
        # Check if we've seen this content before
        if signature_key in seen_signatures and signature_key != "0-[]":
            print("🔄 DUPLICATE CONTENT DETECTED!")
            print("This page has the same content as a previous page.")
            print("Stopping scraping to avoid infinite loop.")
            break
        
        seen_signatures.add(signature_key)
        
        # Get startups from current page
        try:
            print("Fetching startup data from current page...")
            startups = get_one_page_startups_details()
            startup_count = len(startups) if startups else 0
            
            print(f"📊 Found {startup_count} startups on page {page_count}")
            
            if startups:
                # Add page number to each startup
                for startup in startups:
                    startup['page_number'] = page_count
                
                all_startups.extend(startups)
                print(f"📈 Total startups collected so far: {len(all_startups)}")
                
                # Show first few startups for verification
                for i, startup in enumerate(startups[:3]):
                    print(f"  {i+1}. {startup.get('name', 'Unknown')}")
                    
            else:
                print("⚠️ No startups found on this page")
                
        except Exception as e:
            print(f"❌ Error fetching startups from page {page_count}: {e}")
            break
        
        # Try to navigate to next page
        print(f"\n🔄 Attempting to navigate to page {page_count + 1}...")
        
        if navigate_to_next_page_with_validation():
            print(f"✅ Successfully navigated to page {page_count + 1}")
        else:
            print("❌ Navigation failed or reached end of pages")
            break
        
        # Safety check
        if page_count >= 50:  # Adjust based on expected number of pages
            print("⚠️ Reached safety limit of 50 pages")
            break
    
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Pages processed: {page_count}")
    print(f"Total startups collected: {len(all_startups)}")
    print(f"Unique page signatures: {len(seen_signatures)}")
    
    # Save results to JSON file
    try:
        with open('technopark_startups.json', 'w', encoding='utf-8') as f:
            json.dump(all_startups, f, ensure_ascii=False, indent=2)
        print(f"✅ Results saved to 'technopark_startups.json'")
    except Exception as e:
        print(f"❌ Error saving results: {e}")
    
    return all_startups

def debug_current_page():
    """Debug function to check current page state"""
    print("=== DEBUG: CURRENT PAGE STATE ===")
    
    try:
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        voir_links = driver.find_elements(By.LINK_TEXT, "Voir Détails")
        print(f"'Voir Détails' links found: {len(voir_links)}")
        
        nav_items = driver.find_elements(By.XPATH, "//*[@id='root']/div/div/div/div[2]/div[3]/nav/ul/li")
        print(f"Navigation items found: {len(nav_items)}")
        
        for i, item in enumerate(nav_items):
            try:
                text = item.text.strip()
                classes = item.get_attribute('class')
                print(f"  Nav item {i+1}: '{text}' (classes: {classes})")
            except:
                print(f"  Nav item {i+1}: <error getting text>")
        
        # Get page signature
        signature = get_page_signature()
        print(f"Page signature: {signature}")
        
    except Exception as e:
        print(f"Debug error: {e}")
    
    print("=== END DEBUG ===")

# Main execution
def main():
    """Main function to run the scraper"""
    try:
        print("🎯 Starting Technopark Startup Scraper")
        print("=" * 50)
        
        # Debug initial state
        debug_current_page()
        
        # Run the scraper
        data = get_all_startups_details()
        
        print(f"\n🎉 Scraping completed successfully!")
        print(f"Total startups scraped: {len(data)}")
        
        return data
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        return []
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        debug_current_page()
        return []
    finally:
        # Clean up
        try:
            driver.quit()
            print("🔧 Browser closed successfully")
        except:
            pass

# Run the scraper
if __name__ == "__main__":
    results = main()