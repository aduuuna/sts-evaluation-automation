# checkin_bot.py
# Automatically clicks "Check In to Exam" buttons until none left.
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import setup_browser, login

def run_checkin():
    driver = setup_browser()
    wait = WebDriverWait(driver, 12)
    try:
        login(driver)
        driver.get("https://sts.ug.edu.gh/services/evaluation")
        time.sleep(1.2)

        attempt = 0
        while True:
            attempt += 1
            # XPath union for button or anchor text containing 'Check In' (case variations)
            checkin_elems = driver.find_elements(By.XPATH,
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'check in') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'check-in') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'checkin')] | //a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'check in') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'check-in') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'checkin')]")

            # filter visible & enabled
            candidates = [e for e in checkin_elems if e.is_displayed() and e.is_enabled()]
            if not candidates:
                print("✅ No more check-in buttons found. All done.")
                break

            print(f"Try #{attempt}: found {len(candidates)} check-in button(s). Clicking them...")
            for el in candidates:
                try:
                    coursecode = el.get_attribute("coursecode") or el.text.strip()[:80]
                    print(" -> clicking check-in for:", coursecode)
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(1.0)
                except Exception as e:
                    print("    could not click:", e)

            # reload/refresh and retry (gives UI time to update)
            time.sleep(1.2)
            driver.refresh()
            time.sleep(1.5)

        return True

    except Exception as e:
        print("Error in check-in script:", e)
        return False

    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    ok = run_checkin()
    print("Check-in completed:", ok)
