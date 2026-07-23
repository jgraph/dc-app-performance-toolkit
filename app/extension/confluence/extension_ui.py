import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates, AdminPage, Editor
from selenium_ui.confluence.pages.selectors import EditorLocators, PageLocators
from selenium.webdriver.common.keys import Keys
from util.conf import CONFLUENCE_SETTINGS

# Server-roundtrip waits (diagram publish, page save) need more than the
# default 20 s timeout when the instance is under full load.
UNDER_LOAD_TIMEOUT = 60


def __recover_from_editor(webdriver):
    # Never leave the browser on a dirty editor page: a pending 'unsaved
    # changes' prompt hangs the next navigation (log out) for 120 s and
    # poisons the webdriver session for every test that follows.
    try:
        webdriver.switch_to.default_content()
        webdriver.execute_script(
            "window.onbeforeunload = null;"
            "if (window.AJS && AJS.$) { AJS.$(window).off('beforeunload unload'); }")
        webdriver.get(f"{CONFLUENCE_SETTINGS.server_url}/dashboard.action")
    except Exception:
        pass


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    app_specific_page_id = datasets.get('custom_page_id')
    if not app_specific_page_id:
        return

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

    editor_page = Editor(webdriver)

    @print_timing("selenium_app_custom_action:open_editor")
    def measure_open_editor():
        page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/pages/editpage.action?pageId={app_specific_page_id}")
        editor_page.wait_for_page_loaded()

    @print_timing("selenium_app_custom_action:insert_drawio_macro")
    def measure_insert_macro():
        editor_iframe = webdriver.find_element(By.ID, "wysiwygTextarea_ifr")
        webdriver.switch_to.frame(editor_iframe)
        page.wait_until_visible((By.ID, "tinymce"))
        page_body = webdriver.find_element(By.ID, "tinymce")
        page_body.click()
        webdriver.switch_to.default_content()
        drawio_macro_item = (By.CLASS_NAME, "macro-drawio")
        page.wait_until_clickable((By.ID, "insert-menu"))
        for attempt in range(3):
            webdriver.find_element(By.ID, "insert-menu").click()
            if page.became_visible_in_time(drawio_macro_item, 5):
                break
        page.wait_until_visible(drawio_macro_item)
        insert_macro = webdriver.find_element(*drawio_macro_item)
        insert_macro.click()
        page.wait_until_visible((By.CSS_SELECTOR, "li[data-libs='general;flowchart']"))
        diagram_cat = webdriver.find_element(By.CSS_SELECTOR, "li[data-libs='general;flowchart']")
        diagram_cat.click()
        create_button = page.wait_until_clickable((By.ID, "create-button"))
        create_button.click()
        page.wait_until_visible((By.ID, "drawioEditor"))  # Wait for draw.io editor iframe
        drawio_iframe = webdriver.find_element(By.ID, "drawioEditor")
        webdriver.switch_to.frame(drawio_iframe)
        page.wait_until_visible((By.CLASS_NAME, "geDiagramContainer"))

    @print_timing("selenium_app_custom_action:publish_diagram")
    def measure_publish_diagram():
        # Add diagram elements
        diagram_container = webdriver.find_element(By.CLASS_NAME, "geDiagramContainer")
        diagram_container.click()
        diagram_container.send_keys("D")
        # Publish the diagram
        publish_button = webdriver.find_element(By.XPATH, "//div[@class='geButtonContainer']/button[1]")
        publish_button.click()
        page.wait_until_visible((By.CLASS_NAME, "geDialog"))
        diagram_name = webdriver.find_element(By.XPATH, "//div[@class='geDialog']//input")
        diagram_name.send_keys(str(random.randint(1, 100000)) + "Test Diagram.drawio")
        diagram_name.send_keys(Keys.ENTER)
        webdriver.switch_to.default_content()
        editor_iframe = webdriver.find_element(By.ID, "wysiwygTextarea_ifr")
        webdriver.switch_to.frame(editor_iframe)
        page.wait_until_visible((By.CSS_SELECTOR, "img[data-macro-name='drawio']"), timeout=UNDER_LOAD_TIMEOUT)
        webdriver.switch_to.default_content()
        # The drawio overlay closes asynchronously and intercepts clicks until it is gone
        page.wait_until_invisible((By.ID, "drawioEditor"), timeout=UNDER_LOAD_TIMEOUT)

    @print_timing("selenium_app_custom_action:save_page")
    def measure_save_page():
        # Same flow as Editor.save_edited_page() but with load-tolerant timeouts
        page.wait_until_clickable(EditorLocators.publish_button).click()
        if page.get_elements(EditorLocators.confirm_publishing_button):
            if webdriver.find_element(*EditorLocators.confirm_publishing_button).is_displayed():
                webdriver.find_element(*EditorLocators.confirm_publishing_button).click()
        page.wait_until_invisible(EditorLocators.save_spinner, timeout=UNDER_LOAD_TIMEOUT)
        page.wait_until_any_ec_presented(
            selectors=[PageLocators.page_title, EditorLocators.confirm_publishing_button],
            timeout=UNDER_LOAD_TIMEOUT)

    try:
        measure_open_editor()
        measure_insert_macro()
        measure_publish_diagram()
        measure_save_page()
    except Exception:
        __recover_from_editor(webdriver)
        raise
