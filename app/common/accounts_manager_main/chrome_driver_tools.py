import undetected_chromedriver as uc
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import WebElement


def search_element_with_timeout(driver: uc.Chrome, by: str, text: str, timeout: int = 10) -> WebElement or None:
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, text))
        )
        return element
    except TimeoutException:
        print("Element not found")
        return None
