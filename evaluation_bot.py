import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import setup_browser, login

def safe_click_js(driver, elem):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
    driver.execute_script("arguments[0].click();", elem)

def run_evaluation(username=None, password=None, keep_browser_open=False, debug=False, logger=print):
    """
    Returns True if evaluation process completed (no more Evaluate links),
    False on error.
    keep_browser_open: if True driver won't be quit in finally.
    """
    driver = setup_browser()
    wait = WebDriverWait(driver, 15)
    try:
        login(driver, username=username, password=password)
        driver.get("https://sts.ug.edu.gh/services/evaluation")
        time.sleep(1)

        while True:
            evaluate_links = driver.find_elements(By.XPATH, "//a[contains(., 'Evaluate Course')]")
            if not evaluate_links:
                logger("No more 'Evaluate Course' links found. Done with evaluations.")
                break

            # Click the first evaluate link
            link = evaluate_links[0]
            link_text = (link.text or link.get_attribute("href"))[:80]
            logger(f"Opening: {link_text}")
            safe_click_js(driver, link)

            # Wait for the form to load (coursecode field present)
            try:
                wait.until(EC.presence_of_element_located((By.NAME, "coursecode")))
            except TimeoutException:
                logger("Form did not load in time; trying to continue...")
                driver.get("https://sts.ug.edu.gh/services/evaluation")
                continue
            time.sleep(0.4)

           
            # NEW Lecturer card/image selection handling
            try:
                # Find all profile cards
                cards = driver.find_elements(By.CSS_SELECTOR, ".profile-card")
                real_cards = [c for c in cards if c.get_attribute("data-user-id") and c.get_attribute("data-user-id").strip()]
                
                if len(real_cards) == 0:
                    logger("No lecturer cards found.")
                elif len(real_cards) == 1:
                    safe_click_js(driver, real_cards[0])
                    logger(f"Selected lecturer: {real_cards[0].get_attribute('data-user-id').split('^^')[-1]}")
                else:
                    logger("Multiple lecturers detected. Auto-selecting the first one.")
                    # In a real UI, we could pause here, but for now we follow the "automation" goal.
                    safe_click_js(driver, real_cards[0])
                    logger(f"Selected lecturer: {real_cards[0].get_attribute('data-user-id').split('^^')[-1]}")
            except Exception as e:
                if debug: logger(f"Lecturer card selection error: {e}")

            # Fill radio Q1..Q21 with value = 3 (Neutral)
            for qnum in [1,2,3,4,5,6,7,8,9,12,13,14,15,16,17,18,19,20,21]:
                xpath = f"//input[@name='Q{qnum}' and @value='3']"
                try:
                    rb = driver.find_element(By.XPATH, xpath)
                    driver.execute_script("arguments[0].click();", rb)
                except Exception:
                    logger(f"  Q{qnum}: radio with value=3 not found (skipped)")

            # Fill textareas optional
            try:
                ta1 = driver.find_element(By.NAME, "OQ1")
                ta2 = driver.find_element(By.NAME, "OQ2")
                ta1.clear(); ta1.send_keys("No comment.")
                ta2.clear(); ta2.send_keys("No suggestions.")
            except Exception:
                pass

            # Automate Submit button click
            logger("Form filled. Submitting...")
            try:
                submit_btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(., 'Submit')]")
                safe_click_js(driver, submit_btn)
                logger("Form submitted.")
            except Exception as e:
                logger(f"Could not find or click Submit button: {e}")
                # Fallback: maybe it's already submitted or we need to wait
            
            time.sleep(1) # Wait for redirect

            # After submit, wait short time for the evaluation page to reappear
            try:
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(., 'Evaluate Course')]")))
                time.sleep(0.4)
            except TimeoutException:
                # No evaluate links detected — assume done or check if we are on the right page
                if "evaluation" not in driver.current_url:
                    driver.get("https://sts.ug.edu.gh/services/evaluation")
                    time.sleep(1)
                
                evaluate_links = driver.find_elements(By.XPATH, "//a[contains(., 'Evaluate Course')]")
                if not evaluate_links:
                    logger("No evaluate links found after submit (maybe last course).")
                    break

        return True

    except Exception as ex:
        logger(f"Error in evaluation: {ex}")
        return False

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
