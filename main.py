from scraper import *
from kamikaze import kamikaze
import pandas as pd



def run_scraping():
    driver, wait = initialize_driver()
    try:
        driver.get(technopark_url)
    except Exception as e:
        log.error(f"Failed to get: {technopark_url} \nException: {e}")

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

                    data.append(startup_details)
                    log.info(f'Added "{startup_details["name"]}".')

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
            log.info("\n SCRAPING FINISHED SUCCESSFULLY!")

    except KeyboardInterrupt:
        log.warning(" Process interrupted manually!")

    finally:
        driver.quit()

    data_without_duplicates = [dict(t) for t in set(tuple(sorted(d.items())) for d in data)]
    log.info(f"Number of unique startups: {len(data_without_duplicates)}")

    return data



def save_data(data):
    try:
        df = pd.DataFrame(data)
        df.to_json(path_or_buf= "data/technopark_startups.json", orient= "records")
        log.info("Data saved successfully!")
    except Exception as e:
        log.error(f"Enable to save data, because of the following exception: {e}")
    



data = run_scraping()
save_data(data)

        