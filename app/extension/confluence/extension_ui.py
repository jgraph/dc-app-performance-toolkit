import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates, AdminPage
from selenium.webdriver.common.keys import Keys
from util.conf import CONFLUENCE_SETTINGS
import random


def app_specific_action(webdriver, datasets):
    webdriver.implicitly_wait(20)
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.wait_for_page_loaded()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.click_login_button()
    #         if login_page.is_first_login():
    #             login_page.first_user_setup()
    #         all_updates_page = AllUpdates(webdriver)
    #         all_updates_page.wait_for_page_loaded()
    #         # uncomment below line to do web_sudo and authorise access to admin pages
    #         # AdminPage(webdriver).go_to(password=password)
    #
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:add_drawio_macro")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/pages/editpage.action?pageId={app_specific_page_id}")
            page.wait_until_visible((By.ID, "wysiwygTextarea_ifr"))
            editor_iframe = webdriver.find_element(By.ID, "wysiwygTextarea_ifr") 
            webdriver.switch_to.frame(editor_iframe)
            page.wait_until_visible((By.ID, "tinymce"))
            page_body = webdriver.find_element(By.ID, "tinymce")
            page_body.click()
            webdriver.switch_to.default_content()
            page.wait_until_visible((By.ID, "insert-menu"))
            insert_menu = webdriver.find_element(By.ID, "insert-menu")
            insert_menu.click()
            page.wait_until_visible((By.CLASS_NAME, "macro-drawio"))
            insert_macro = webdriver.find_element(By.CLASS_NAME, "macro-drawio")
            insert_macro.click()
            page.wait_until_visible((By.CSS_SELECTOR, "li[data-libs='general;flowchart']"))
            diagram_cat = webdriver.find_element(By.CSS_SELECTOR, "li[data-libs='general;flowchart']")
            diagram_cat.click()
            create_button = webdriver.find_element(By.ID, "create-button")
            create_button.click()
            page.wait_until_visible((By.ID, "drawioEditor")) # Wait for draw.io editor iframe
            #drawio_iframe = webdriver.find_element(By.ID, "drawioEditor") 
            #webdriver.switch_to.frame(drawio_iframe)
            #page.wait_until_visible((By.CLASS_NAME, "geDiagramContainer"))
            # Add diagram elements
            #diagram_container = webdriver.find_element(By.CLASS_NAME, "geDiagramContainer")
            #diagram_container.click()
            #diagram_container.send_keys("D")
            # Publish the diagram
            #publish_button = webdriver.find_element(By.XPATH, "//div[@class='geButtonContainer']/button[1]")
            #publish_button.click()
            #page.wait_until_visible((By.CLASS_NAME, "geDialog"))
            #diagram_name = webdriver.find_element(By.XPATH, "//div[@class='geDialog']//input")
            #diagram_name.send_keys(str(random.randint(1, 100000)) + "Test Diagram.drawio")
            #diagram_name.send_keys(Keys.ENTER)
            #webdriver.switch_to.default_content()
            #webdriver.switch_to.frame(editor_iframe)
            #page.wait_until_visible((By.CSS_SELECTOR, "img[data-macro-name='drawio']"))
        sub_measure()
    measure()
