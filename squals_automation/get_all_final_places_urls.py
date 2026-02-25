from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time


def get_all_final_places_urls(browser, base_url):
    """
    Navigate to the base URL, find all event results from the Event Results dropdown,
    navigate to each event's results page, and extract the "Final Places" link.

    Args:
        base_url: The URL of the results_generic.html page

    Returns:
        A list of tuples containing (event_name, final_places_url)
    """
    final_places_urls = []

    browser.get(base_url)
    time.sleep(2)

    # Find the Event Results dropdown
    event_select = Select(browser.find_element(By.NAME, "event_id"))

    # Get all available options (excluding the first empty or default option if any)
    options = event_select.options
    event_values = [(option.text, option.get_attribute("value")) for option in options]

    # Iterate through each event
    for event_name, event_value in event_values:
        try:
            # Re-find the select element to avoid stale element reference
            event_select = Select(browser.find_element(By.NAME, "event_id"))
            event_select.select_by_value(event_value)
            time.sleep(2)

            # Find the "Final Places" link within the current event's sidebar
            try:
                final_places_link = browser.find_element(
                    By.XPATH, "//a[contains(text(), 'Final Places')]"
                )
                final_places_url = final_places_link.get_attribute("href")
                final_places_urls.append((event_name, final_places_url))
                print(f"{event_name}: {final_places_url}")
            except Exception as e:
                print(f"No 'Final Places' link found for {event_name}")

        except Exception as e:
            print(f"Error processing event {event_name}: {str(e)}")

    return final_places_urls
