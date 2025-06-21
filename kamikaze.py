import logging as log
from scraper import technopark_url, click_startup_link, click_startup_website_icon
from scraper import click_the_triangle_button, get_page_startups_links, initialize_driver,  get_startup_contact_info


def kamikaze(n_pages, n_startup):
     #this function will create a driver that will do everything to get the startups website, and then dieeeee :) thus the name
    kamikaze, wait = initialize_driver()
    kamikaze.get(technopark_url)
    collected_data = {}

    for _ in range(n_pages): click_the_triangle_button(kamikaze, wait)  #navigate to the page in which we were. 

    page_links = get_page_startups_links(wait)
    link = page_links[n_startup]
    click_startup_link(kamikaze, link)
    details_tab = kamikaze.current_window_handle

    clicked_icon = click_startup_website_icon(kamikaze, wait)
    handles = kamikaze.window_handles
    
    if clicked_icon:  
        opened_tab = [tab  for tab in handles if tab != details_tab][0]     
        kamikaze.switch_to.window(opened_tab)
        log.info("Kamikaze: Mission successful.")
        try: 
            startup_website = kamikaze.current_url
            startup_contacts = get_startup_contact_info(kamikaze)

        except Exception as e: 
            log.warning(f"Kamikaze: Mission failed: exception: {e.msg}")
            startup_website = "N/A"
            startup_contacts = {'emails': [], "phones" : [], "addresses": []}
    else: 
        log.info("Kamikaze: Mission failed: the startup likely doesn't have a website")
        kamikaze.quit()
        startup_website = "N/A"
        startup_contacts = {"emails": [], "phones" : [], "addresses": []}

    kamikaze.quit()
    collected_data['website'] = startup_website
    collected_data.update(startup_contacts)
    return collected_data
        
   
