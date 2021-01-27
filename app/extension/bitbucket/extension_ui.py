import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import BITBUCKET_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    rnd_repo = random.choice(datasets["repos"])

    project_key = rnd_repo[1]
    repo_slug = rnd_repo[0]

    page_url = None

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:view_repo_settings")
        def sub_measure1():
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugins/servlet/pages-settings/{project_key}/{repo_slug}")
            # Wait for list of branches to load.
            page.wait_until_visible((By.CLASS_NAME, 'default-branch-lozenge'))
        sub_measure1()

        @print_timing("selenium_app_custom_action:enable_pages_for_branch")
        def sub_measure2():
            # Enable serving pages from a branch.
            branch_container = page.get_element((By.XPATH, '//tr[@class="pages-config disabled"]'))
            enable_button = branch_container.find_element(By.XPATH, '//button[@title="Enable pages for this branch"]')
            enable_button.click()

            # Wait for the pages link to show up.
            href = branch_container.find_element(By.XPATH, '//td[@class="pages-ref-link"]/a')
            nonlocal page_url
            page_url = href.get_attribute('href')
            WebDriverWait(webdriver, 10).until(EC.visibility_of(href))
        sub_measure2()

        @print_timing("selenium_app_custom_action:serve_page")
        def sub_measure3():
            nonlocal page_url
            page.go_to_url(page_url)
            # No index.html in the testing data, expect 404 response.
            page.wait_until_visible((By.XPATH, '//div[@class="error-image _404"]'))
        sub_measure3()
    measure()
