# evaluation_bot.py
# Usage: import run_evaluation from this file, or run as script
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import setup_browser, login

def safe_click_js(driver, elem):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
    driver.execute_script("arguments[0].click();", elem)

def run_evaluation(keep_browser_open=False, debug=False):
    """
    Returns True if evaluation process completed (no more Evaluate links),
    False on error.
    keep_browser_open: if True driver won't be quit in finally.
    """
    driver = setup_browser()
    wait = WebDriverWait(driver, 15)
    try:
        login(driver)
        driver.get("https://sts.ug.edu.gh/services/evaluation")
        time.sleep(1)

        while True:
            evaluate_links = driver.find_elements(By.XPATH, "//a[contains(., 'Evaluate Course')]")
            if not evaluate_links:
                print("✅ No more 'Evaluate Course' links found. Done with evaluations.")
                break

            # Click the first evaluate link
            link = evaluate_links[0]
            print("Opening:", (link.text or link.get_attribute("href"))[:80])
            safe_click_js(driver, link)

            # Wait for the form to load (coursecode field present)
            try:
                wait.until(EC.presence_of_element_located((By.NAME, "coursecode")))
            except TimeoutException:
                print("Form did not load in time; trying to continue...")
                driver.get("https://sts.ug.edu.gh/services/evaluation")
                continue
            time.sleep(0.4)

            # Lecturer dropdown handling
            try:
                select_elem = driver.find_element(By.CSS_SELECTOR, "select[name='lect_name']")
                options = select_elem.find_elements(By.TAG_NAME, "option")
                real_opts = [opt for opt in options if opt.get_attribute("value") and opt.get_attribute("value").strip() != ""]
                if len(real_opts) == 0:
                    print("No lecturer options found (empty).")
                elif len(real_opts) == 1:
                    val = real_opts[0].get_attribute("value")
                    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", select_elem, val)
                    print("Selected lecturer:", real_opts[0].text)
                else:
                    print("Multiple lecturers detected:")
                    for i, opt in enumerate(real_opts, start=1):
                        print(f"  {i}. {opt.text}")
                    choice = input("Enter number of the lecturer to select (press Enter for 1): ").strip()
                    try:
                        idx = int(choice) - 1 if choice else 0
                        idx = max(0, min(idx, len(real_opts)-1))
                    except Exception:
                        idx = 0
                    val = real_opts[idx].get_attribute("value")
                    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", select_elem, val)
                    print("Selected lecturer:", real_opts[idx].text)
            except Exception as e:
                if debug: print("Lecturer dropdown handling error:", e)

            # Fill radio Q1..Q21 with value = 1 (Strongly Disagree)
            for qnum in range(1, 22):
                xpath = f"//input[@name='Q{qnum}' and @value='1']"
                try:
                    rb = driver.find_element(By.XPATH, xpath)
                    driver.execute_script("arguments[0].click();", rb)
                except Exception:
                    print(f"  Q{qnum}: radio with value=1 not found (skipped)")

            # Fill textareas optional (you can change/remove)
            try:
                ta1 = driver.find_element(By.NAME, "OQ1")
                ta2 = driver.find_element(By.NAME, "OQ2")
                ta1.clear(); ta1.send_keys("No comment.")
                ta2.clear(); ta2.send_keys("No suggestions.")
            except Exception:
                pass

            # Pause so user can manually review & click Submit
            print("\nForm filled for this course.")
            print("=== REVIEW on the browser and click SUBMIT. After you return to the course list, press ENTER here to continue ===")
            input()

            # After user pressed Enter, wait short time for the evaluation page to reappear
            try:
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(., 'Evaluate Course')]")))
                time.sleep(0.4)
            except TimeoutException:
                # No evaluate links detected — assume done
                print("No evaluate links found after submit (maybe last course).")
                break

        return True

    except Exception as ex:
        print("Error in evaluation:", ex)
        return False

    finally:
        if not keep_browser_open:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    ok = run_evaluation(keep_browser_open=False)
    print("Evaluation completed:", ok)
