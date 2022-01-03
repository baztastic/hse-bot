# hse-bot
Two methods in Python for checking the number of PCR Tests available on the HSE system

## hse-bot.py
This uses Selenium to click on buttons on the HSE website. It runs in the background (headless) and prints and logs available slots.

## hse-rest.py
This uses the HSE's REST API to directly query the number of available slots. It's a reimplementation of the API calls from [here](https://github.com/williamoconnorme/hse-pcr-test-appointment-alerts) using the `requests` python package.
