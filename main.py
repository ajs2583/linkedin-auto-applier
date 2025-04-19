import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException
import time

# Load environment variables
load_dotenv()

# Constants
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4203792789&f_AL=true&keywords=python%20developer"
SIGN_IN_BUTTON_SELECTOR = "button[data-modal='base-sign-in-modal']"
USERNAME_FIELD_NAME = "session_key"
PASSWORD_FIELD_NAME = "session_password"
JOB_LISTING_CSS_SELECTOR = "a.job-card-list__title--link"
APPLY_BUTTON_SELECTOR = 'button[aria-label="Submit application"]'  # "button.jobs-apply-button"
PHONE_INPUT_SELECTOR = "input.artdeco-text-input--input"  # "input[name='phone']"

# Retrieve credentials from environment variables
USER_NAME = os.getenv("LINKEDIN_USERNAME")
PW = os.getenv("LINKEDIN_PASSWORD")
PHONE = os.getenv("LINKEDIN_PHONE")

if not USER_NAME or not PW:
    raise ValueError("Missing LinkedIn credentials in environment variables.")

# Initialize WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)


# Function to check if the phone number is present
def abort_application():
    try:
        close_button = driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss")
        close_button.click()
        print("Clicked modal close")

        time.sleep(1)  # Give time for discard modal to appear

        # Find *all* confirm-dialog buttons and click the first one
        discard_buttons = driver.find_elements(By.CLASS_NAME, "artdeco-modal__confirm-dialog-btn")
        if discard_buttons:
            discard_buttons[0].click()
            print("Clicked discard confirmation")
        else:
            print("Discard button not found.")
    except Exception as e:
        print("Error during abort:", e)


# Open LinkedIn job search page
try:
    # Open LinkedIn job search page
    driver.get(LINKEDIN_URL)
    driver.maximize_window()

    # Click the sign-in button
    sign_up_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SIGN_IN_BUTTON_SELECTOR))
    )
    sign_up_button.click()

    # Enter username and password
    username_input = wait.until(
        EC.presence_of_element_located((By.NAME, USERNAME_FIELD_NAME))
    )
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, PASSWORD_FIELD_NAME))
    )

    username_input.send_keys(USER_NAME)
    password_input.send_keys(PW)
    password_input.send_keys(Keys.ENTER)

    """TODO:
    Picture in big:
    Iterate through all job listings
    Check if the phone number is present
    If the phone number is present, click the apply button
    If the phone number is present, click the close button and discard the application
    If anything besides the phone number and normal application is present, click the close button and discard the application
    """
    # Grab each job listing on the page
    all_job_listings = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, JOB_LISTING_CSS_SELECTOR))
    )

    # 👇 this stays inside the outer try
    for i, job in enumerate(all_job_listings):
        try:
            print(f"Clicking job {i + 1}: {job.text.strip().splitlines()[0]}")

            try:
                overlay = driver.find_element(By.CLASS_NAME, "artdeco-modal__overlay")
                if overlay.is_displayed():
                    abort_application()
                    time.sleep(1)
            except NoSuchElementException:
                pass

            driver.execute_script("arguments[0].scrollIntoView();", job)
            job.click()

            easy_apply_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-apply-button"))
            )
            easy_apply_btn.click()
            print("Clicked Easy Apply")

            try:
                phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PHONE_INPUT_SELECTOR)))
                if phone_input.get_attribute("value").strip() == "":
                    phone_input.send_keys(PHONE)
                    print("Phone number filled.")
                else:
                    print("Phone number already present.")
            except:
                print("Phone input not found — aborting.")
                abort_application()
                continue

            step_attempts = 0
            max_steps = 5
            while step_attempts < max_steps:
                step_attempts += 1
                time.sleep(1)

                try:
                    review_btn = driver.find_element(By.XPATH, "//button[contains(., 'Review')]")
                    if review_btn.is_displayed():
                        review_btn.click()
                        print("Clicked Review")

                        try:
                            submit_btn = wait.until(
                                EC.element_to_be_clickable(
                                    (By.CSS_SELECTOR, 'button[aria-label="Submit application"]'))
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
                    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Submit application"]')
                    if submit_btn.is_displayed():
                        submit_btn.click()
                        print("Application submitted.")
                        break
                except NoSuchElementException:
                    pass

                try:
                    next_btn = driver.find_element(By.XPATH, "//button[contains(., 'Next')]")
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

# ✅ now we close the outer try
finally:
    driver.quit()

