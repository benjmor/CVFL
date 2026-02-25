from datetime import datetime, date
from selenium.webdriver.common.by import By
import logging
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def login_to_tabroom(browser, tabroom_username, tabroom_password,):
    """Log in to Tabroom using Selenium to access protected results pages."""
    logging.debug("Starting browser session")
    # Logging in to Tabroom to access protected results pages
    login_url = "https://www.tabroom.com/user/login/login.mhtml"
    # need to hit the login url to get the salt and SHA in order to pass those values in the login_save request
    browser.get(login_url)
    salt = browser.find_element(By.NAME, "salt").get_attribute("value")
    sha = browser.find_element(By.NAME, "sha").get_attribute("value")

    login_data = {
        "username": tabroom_username,
        "password": tabroom_password,
        "salt": salt,
        "sha": sha,
    }
    login_save_url = "https://www.tabroom.com/user/login/login_save.mhtml"
    # Send a post request to the login_save URL with the login data to authenticate the session
    browser.execute_script(
        """
        function post(path, params) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = path;
            for (const key in params) {
                const hiddenField = document.createElement('input');
                hiddenField.type = 'hidden';
                hiddenField.name = key;
                hiddenField.value = params[key];
                form.appendChild(hiddenField);
            }
            document.body.appendChild(form);
            form.submit();
        }
        post("%s", %s);
        """
        % (login_save_url, json.dumps(login_data, cls=DateTimeEncoder))
    )
