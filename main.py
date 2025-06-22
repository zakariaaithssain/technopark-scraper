from functions import *
from kamikaze import kamikaze
import pandas as pd



def run_scraping():
    driver, wait = initialize_driver()
    try: driver.get(technopark_url)
    except TimeoutException: log.error(f"Scraper: Failed to get Technopark's URL.")

    current_page = 0  # Track current page (0-indexed)
    data = []
    navigated = True  # just to start the loop.

    try:
        while navigated:
            try:
                n_startups_in_page = count_page_startups(wait)
                for n_startup in range(n_startups_in_page):
                    # we should get the links each time because of the StaleElementReferenceException.
                    page_links = get_page_startups_links(wait)
                    startup_link = page_links[n_startup]
                    click_startup_link(driver, startup_link)
                    startup_details = get_startup_details(driver)  # this calls driver.back() at the end, forcing us to the 1st page each time.

                    kamikaze_mission = kamikaze(current_page, n_startup)
                    startup_details.update(kamikaze_mission)
                    print(kamikaze_mission)

                    data.append(startup_details)
                    log.info(f'Scraper: Added "{startup_details["name"]}".')

                    # Navigate back to the correct page after driver.back() took us to page 1
                    for page_num in range(current_page):
                        # Navigate forward to get back to our current page
                        navigated = click_the_triangle_button(driver, wait)
                        if not navigated:  # If we can't navigate, we've reached the end
                            break

                # Move to next page after processing all startups on current page
                current_page += 1
                navigated = click_the_triangle_button(driver, wait)

            # for pages that might not contain the expected number of startups, this error is expected from the bigger 'for' loop.
            except IndexError:
                current_page += 1
                navigated = click_the_triangle_button(driver, wait)
                continue
        else:
            log.info("\nScraper: SCRAPING FINISHED SUCCESSFULLY!")

    except KeyboardInterrupt:
        log.warning("Scraper: Process interrupted manually!")

    finally:
        driver.quit()

    return data



def save_data(data):
    try:
        df = pd.DataFrame(data)
        df.to_json(path_or_buf= "data/technopark_startups.json", orient= "records")
        log.info("Scraper: Data saved successfully!")
    except Exception as e:
        log.error(f"Scraper: Enable to save data, because of the following exception: {e}")
    



data = run_scraping()
save_data(data)

        