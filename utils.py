# utils.py
import os, time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
STS_USERNAME = os.getenv("STS_USERNAME")
STS_PASSWORD = os.getenv("STS_PASSWORD")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")  # optional: full path to chromedriver
HEADLESS = os.getenv("HEADLESS", "0") == "1"

def setup_browser():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
    opts.add_argument("--start-maximized")
    service = Service(CHROMEDRIVER_PATH) if CHROMEDRIVER_PATH else Service()
    driver = webdriver.Chrome(service=service, options=opts)
    driver.implicitly_wait(3)
    return driver

def login(driver):
    """Log in as student (selects 'Student' radio robustly)."""
    wait = WebDriverWait(driver, 15)
    driver.get("https://sts.ug.edu.gh/services/login")
    wait.until(EC.presence_of_element_located((By.ID, "studentid")))

    # Try clicking label that contains 'Student'
    try:
        label_student = driver.find_element(By.XPATH, "//label[.//span[contains(., 'Student')]]")
        driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", label_student)
    except Exception:
        # fallback set input checked via JS
        driver.execute_script(
            "let i = document.querySelector('input[name=\"loginas\"][value=\"student\"]');"
            " if(i){ i.checked = true; i.dispatchEvent(new Event('change')); }"
        )

    # Fill credentials and submit
    driver.find_element(By.ID, "studentid").clear()
    driver.find_element(By.ID, "studentid").send_keys(STS_USERNAME)
    driver.find_element(By.ID, "pin").clear()
    driver.find_element(By.ID, "pin").send_keys(STS_PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait small moment for dashboard
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)
