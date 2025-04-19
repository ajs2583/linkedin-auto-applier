import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv

# ─── Config & Constants ────────────────────────────────────────────────────────
load_dotenv()

LINKEDIN_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4203792789&f_AL=true&keywords=python%20developer"

# Environment
USER_NAME = os.getenv("LINKEDIN_USERNAME")
PW = os.getenv("LINKEDIN_PASSWORD")
PHONE = os.getenv("LINKEDIN_PHONE")

if not USER_NAME or not PW:
    raise ValueError("Missing LinkedIn credentials in environment variables.")

# Selenium Selectors
SELECTOR_SIGN_IN_BTN = (By.CSS_SELECTOR, "button[data-modal='base-sign-in-modal']")
SELECTOR_USERNAME_FIELD = (By.NAME, "session_key")
SELECTOR_PASSWORD_FIELD = (By.NAME, "session_password")
SELECTOR_JOB_LISTINGS = (By.CSS_SELECTOR, "a.job-card-list__title--link")
SELECTOR_EASY_APPLY_BTN = (By.CSS_SELECTOR, "button.jobs-apply-button")
SELECTOR_PHONE_INPUT = (By.CSS_SELECTOR, "input.artdeco-text-input--input")
SELECTOR_REVIEW_BTN = (By.XPATH, "//button[contains(., 'Review')]")
SELECTOR_SUBMIT_BTN = (By.CSS_SELECTOR, "button[aria-label='Submit application']")
SELECTOR_NEXT_BTN = (By.XPATH, "//button[contains(., 'Next')]")
SELECTOR_MODAL_CLOSE = (By.CLASS_NAME, "artdeco-modal__dismiss")
SELECTOR_DISCARD_BTN = (By.CLASS_NAME, "artdeco-modal__confirm-dialog-btn")
SELECTOR_MODAL_OVERLAY = (By.CLASS_NAME, "artdeco-modal__overlay")

# ─── Setup Selenium ─────────────────────────────────────────────────────────────
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)


# ─── Helper: Abort Application ──────────────────────────────────────────────────
def abort_application():
    try:
        close_button = driver.find_element(*SELECTOR_MODAL_CLOSE)
        close_button.click()
        print("Clicked modal close")
        time.sleep(1)

        discard_buttons = driver.find_elements(*SELECTOR_DISCARD_BTN)
        if discard_buttons:
            discard_buttons[0].click()
            print("Clicked discard confirmation")
    except Exception as e:
        print("Error during abort:", e)


# ─── Main Job Application Logic ─────────────────────────────────────────────────
def apply_to_jobs():
    job_cards = wait.until(EC.presence_of_all_elements_located(SELECTOR_JOB_LISTINGS))

    for i in range(len(job_cards)):
        try:
            job_cards = wait.until(
                EC.presence_of_all_elements_located(SELECTOR_JOB_LISTINGS)
            )
            job = job_cards[i]
            print(f"Clicking job {i + 1}: {job.text.strip().splitlines()[0]}")

            try:
                overlay = driver.find_element(*SELECTOR_MODAL_OVERLAY)
                if overlay.is_displayed():
                    abort_application()
                    time.sleep(1)
            except NoSuchElementException:
                pass

            driver.execute_script("arguments[0].scrollIntoView();", job)
            job.click()

            easy_apply_btn = wait.until(
                EC.element_to_be_clickable(SELECTOR_EASY_APPLY_BTN)
            )
            easy_apply_btn.click()
            print("Clicked Easy Apply")

            try:
                phone_input = wait.until(
                    EC.presence_of_element_located(SELECTOR_PHONE_INPUT)
                )
                if phone_input.get_attribute("value").strip() == "":
                    phone_input.send_keys(PHONE)
                    print("Phone number filled.")
                else:
                    print("Phone number already present.")
            except:
                print("Phone input not found — aborting.")
                abort_application()
                continue

            for _ in range(5):
                time.sleep(1)

                try:
                    review_btn = driver.find_element(*SELECTOR_REVIEW_BTN)
                    if review_btn.is_displayed():
                        review_btn.click()
                        print("Clicked Review")

                        try:
                            submit_btn = wait.until(
                                EC.element_to_be_clickable(SELECTOR_SUBMIT_BTN)
                            )
                            submit_btn.click()
                            print("Application submitted.")
                            break
                        except:
                            print("Submit button not found after review — aborting.")
                            abort_application()
                            break
                except NoSuchElementException:
                    pass

                try:
                    submit_btn = driver.find_element(*SELECTOR_SUBMIT_BTN)
                    if submit_btn.is_displayed():
                        submit_btn.click()
                        print("Application submitted.")
                        break
                except NoSuchElementException:
                    pass

                try:
                    next_btn = driver.find_element(*SELECTOR_NEXT_BTN)
                    if next_btn.is_displayed() and next_btn.is_enabled():
                        next_btn.click()
                        print("Clicked Next to continue application...")
                        continue
                except NoSuchElementException:
                    print("No Next/Review/Submit — possibly complex")
                    break
            else:
                print("Too many steps — aborting.")
                abort_application()
                continue

            time.sleep(2)

        except Exception as e:
            print(f"Error during job {i + 1}: {e}")
            abort_application()
            continue


# ─── Login and Start ────────────────────────────────────────────────────────────
def main():
    try:
        driver.get(LINKEDIN_URL)
        driver.maximize_window()

        sign_in_btn = wait.until(EC.presence_of_element_located(SELECTOR_SIGN_IN_BTN))
        sign_in_btn.click()

        username_input = wait.until(
            EC.presence_of_element_located(SELECTOR_USERNAME_FIELD)
        )
        password_input = wait.until(
            EC.presence_of_element_located(SELECTOR_PASSWORD_FIELD)
        )

        username_input.send_keys(USER_NAME)
        password_input.send_keys(PW)
        password_input.send_keys(Keys.ENTER)

        apply_to_jobs()

    finally:
        driver.quit()


# ─── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

