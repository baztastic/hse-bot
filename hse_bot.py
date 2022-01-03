### This Selenium bot opens google chrome in headless mode and
### clicks through the HSE PCR Test website (https://covid19test.healthservice.ie/hse-self-referral/)
### until it reaches the page the shows the number of available appointments.
### It will keep retrying RETRIES times every RETRYTIME seconds.
### If the website is under stress it will probably fail, so the `hse_rest.py` bot is more reliable.

### NOTE:
### I wouldn't advise extending this bot to actually make bookings on your behalf, as you need to retrieve
### an SMS code from your phone to make the booking, and must show another SMS code when you attend.

import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

SLEEPTIME = 1           # number of sceonds to sleep between button clicks
RETRIES = 100           # number of times to retry
RETRYTIME = 60          # number of seconds to sleep between retries
MAXRETRIES = RETRIES


def click_button(path):
    button = driver.find_element(By.XPATH, path)
    button.click()


def select_option(path, option):
    sel = Select(driver.find_element(By.XPATH, path))
    sel.select_by_visible_text(option)
    

def get_slots(centre_num):
    test_centre_path = f'/html/body/div/div/div/div[2]/div[2]/div/div[{centre_num}]/div/div'
    test_centre_name_path = test_centre_path + '/div[1]/h5'
    test_centre_appts_path = test_centre_path + '/div[2]/div'
    test_centre_name = driver.find_element(By.XPATH, test_centre_name_path)
    test_centre_appts = driver.find_element(By.XPATH, test_centre_appts_path)
    test_centre_name_text = test_centre_name.text
    test_centre_appts_text = test_centre_appts.text
    return([test_centre_name_text, test_centre_appts_text])


if __name__ == "__main__":
    ser = Service("/Users/baz/Downloads/chromedriver")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    url = 'https://covid19test.healthservice.ie/hse-self-referral/'
    while RETRIES > 0:
        try:
            driver = webdriver.Chrome(service=ser, options=options)  # open the browser
            driver.set_window_position(300, 10, windowHandle='current')
            # load hse website
            driver.get(url)

            time.sleep(SLEEPTIME)

            # start button
            start_path = '/html/body/div/div/div/div[2]/div/button'
            click_button(start_path)

            time.sleep(SLEEPTIME)

            # positive antigen yes
            yes_posi_path = '/html/body/div/div/div/div[2]/div[2]/div/form/fieldset/div/div/div[1]/label'
            click_button(yes_posi_path)

            # next button
            next_path = '/html/body/div/div/div/div[2]/div[2]/div/form/button'
            click_button(next_path)

            time.sleep(SLEEPTIME)

            # Day of positive antigen test
            day_path = '/html/body/div/div/div/div[2]/div[2]/div/form/div/div/div/div[1]/select'
            select_option(day_path, '01')
            month_path = '/html/body/div/div/div/div[2]/div[2]/div/form/div/div/div/div[2]/select'
            select_option(month_path, 'Jan')
            year_path = '/html/body/div/div/div/div[2]/div[2]/div/form/div/div/div/div[3]/select'
            select_option(year_path, '2022')
            click_button(next_path)

            time.sleep(SLEEPTIME)

            # reason for taking antigen test
            reason_path = '/html/body/div/div/div/div[2]/div[2]/div/form/fieldset[1]/div/select'
            select_option(reason_path, 'Other')
            click_button(next_path)

            time.sleep(SLEEPTIME)

            # vaccine status
            vax_path = '/html/body/div/div/div/div[2]/div[2]/div/form/fieldset/div/div/div[1]/label'
            click_button(vax_path)
            click_button(next_path)

            time.sleep(SLEEPTIME)
            # covid symptoms
            # first, scroll to bottom of page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            symptoms_path = '/html/body/div/div/div/div[2]/div[2]/div/form/fieldset/div/div/div[1]/label'
            click_button(symptoms_path)
            click_button(next_path)

            counties = [
            'Carlow',
            'Cavan',
            'Clare',
            'Cork',
            'Donegal',
            'Dublin',
            'Galway',
            'Kerry',
            'Kildare',
            'Kilkenny',
            'Laois',
            'Leitrim',
            'Limerick',
            'Longford',
            'Louth',
            'Mayo',
            'Meath',
            'Monaghan',
            'Offaly',
            'Roscommon',
            'Sligo',
            'Tipperary',
            'Waterford',
            'Westmeath',
            'Wexford',
            'Wicklow',
            ]

            slots = pd.DataFrame(columns = ["timestamp", "county", "centre", "appts"])

            for COUNTY in counties:
                time.sleep(SLEEPTIME)
                print(f"County: {COUNTY}")

                county_path = '/html/body/div/div/div/div[2]/div[2]/div/fieldset/div/select'
                select_option(county_path, COUNTY)

                county_next_path = '/html/body/div/div/div/div[2]/div[2]/div/a'
                click_button(county_next_path)

                time.sleep(SLEEPTIME*2)
                # get number of available slots
                # there are up to 10 test centres per county
                for i in range(1,11):
                    # first check if the test centre exists, and if so get slots
                    if driver.find_elements(By.XPATH, f'/html/body/div/div/div/div[2]/div[2]/div/div[{i}]/div/div'):
                        [centre, appts] = get_slots(i)
                        slots = slots.append(pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), COUNTY, centre, appts]], columns = ["timestamp", "county", "centre", "appts"]))
                        print(centre)
                        print(appts)
                    else:
                        continue

                    if(len(appts)>0 and appts != "0 appts") and centre == 'CHO5 - Wexford (Whitemill) - Self Referral':
                        try:
                            os.system(f'say "{appts.split(" ")[0]} appointments available at {centre} in county {COUNTY}"')
                        except:
                            print("\a")
                        print("\n\n")
                        print("-----!!!!!!!!!-----")
                        print(f"{appts} - APPOINTMENT(S) AVAILABLE AT {centre} IN {COUNTY} AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print("-----!!!!!!!!!-----")
                        print("\n\n")
                        break
                
                back_path = '/html/body/div/div/div/div[2]/div[1]/div/div[1]/div/a'
                if len(counties) > 1:
                    click_button(back_path)
                else:
                    pass
            # Log the current scraped rows
            # During your first run hse_scraped.csv doesn't exist, 
            # so first create it by commenting out the following and using:
            # slots.to_csv("hse_scraped.csv")
            logs = pd.read_csv(f"hse_scraped.csv")
            logs = pd.concat([logs, slots])
            logs = logs.reset_index().drop(['index', 'Unnamed: 0'], axis=1)
            logs.to_csv(f"hse_scraped.csv")
            
            RETRIES -= 1
            time.sleep(RETRYTIME)
            print(f'Retrying {MAXRETRIES - RETRIES} of {MAXRETRIES} times')
        except Exception as e:
            print("\a")
            print(e)
            print("Retrying")
        finally:
            driver.close()

    try:
        os.system(f'say "Finished test run"')
    except:
        print("Finished test run, exiting.")
