### This is a python implementation of williamoconnorme's HSE PCR Test bot
### Based on his REST API commands here:
### https://github.com/williamoconnorme/hse-pcr-test-appointment-alerts
### Run in terminal and it will print and log all available appointments in an infinite loop until halted

### If you care about a particular centre, it can alert you by speaking through your computer
### See the comment way down below

import requests
import time
import os
import pandas as pd
from datetime import datetime


def GetCounties(my_headers):
    url = "https://covid19test.healthservice.ie/swiftflow.php"
    
    payload = {
        "task": "getCountiesInFacility", 
        "flow": "routine"
        }
    
    response = requests.post(
        url,
        headers=my_headers,
        json=payload,
    )
    r = response.json()
    return(r['data'])


def GetCountyFacilities(countyUuid, my_headers):
    url = "https://covid19test.healthservice.ie/swiftflow.php"

    payload = {
        "task": "getConsultantsInCounty",
        "county_uuid": countyUuid,
        "flow": "routine",
    }

    ## Get all the facility ids for the county:
    response = requests.post(
        url,
        headers=my_headers,
        json=payload,
    )
    
    ## can fail from time to time - just print the exception and continue
    try:
        r = response.json()
    except Exception as e:
        print(e)
        return(None)
    print("   ", datetime.fromtimestamp(int(r['timestamp'])))
    return(r)


def GetAppointments(fkey, type_id, my_headers):
    ## Get the number of appointments per facility
    url = "https://covid19test.healthservice.ie/swiftflow.php?future_days=1&minutes_buffer=60&enforce_future_days=1&enforce_today_or_tomorrow_only=0"
    
    payload =  {
        "task" : "getConsultantAvailability",
        "facility_id": fkey, #facility["fkey"],
        "type_id": type_id, #facility["appointment_types"][0]["id"],
        "flow":"routine"
    }
    
    response = requests.post(
        url,
        headers=my_headers,
        json=payload,
        )

    ## can fail from time to time - just print the exception and continue
    try:
        r = response.json()
    except Exception as e:
        print(e)
        return(None, None)
    return([r['data']['type']['total_slots_available'], r['data']['slots']])


while True:
    my_headers = {
        "Authority": "covid19test.healthservice.ie" ,
        "Pragma": "no-cache" ,
        "Cache-Control": "no-cache" ,
        "Sec-CH-UA": "\"Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Microsoft Edge\";v=\"96\"" ,
        "Accept": "application/json, text/plain, */*" ,
        "Content-Type": "application/json" ,
        "Sec-CH-UA-Mobile": "?0" ,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62" ,
        "Sec-CH-UA-Platform": "\"Windows\"" ,
        "Origin": "https://covid19test.healthservice.ie" ,
        "Sec-Fetch-Site": "same-origin" ,
        "Sec-Fetch-Mode": "cors" ,
        "Sec-Fetch-Dest": "empty" ,
        "Referer": "https://covid19test.healthservice.ie/hse-self-referral/facilities/" ,
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8" ,
    }

    counties = GetCounties(my_headers)
    slot_log = pd.DataFrame(columns = ["timestamp", "county", "centre", "appts"])
    for county in counties:
        # Uncomment to focus on a particular county (E.g. Wexford)
        if county['name'] != "Wexford":
            continue
        else:
            pass
        
        print("    County", county['name'])
        r = GetCountyFacilities(county['uuid'], my_headers)
        if r is None:
            continue
        else:
            pass

        for f in r['data']:
            [appts, slots] = GetAppointments(f['fkey'], f["appointment_types"][0]["id"], my_headers)
            if appts is None:
                continue
            else:
                pass
            # todo format slots
            # slots = [{'date': '2022-01-04', 'time': '15:40', 'availability': 1}]
            if appts != 0:
                print(f"!!! {f['name']} :\t{appts} slot(s) available \t!!!")
                print("Slot times:")
                [print("-->", s['date'], s['time']) for s in slots]
                print()
            else:
                print(f"    {f['name']} :\t{appts} slots")
            
            ### If there's a particular centre you care about, update it here
            ### If running on macos, your computer will speak when it finds an appointment there
            ### Otherwise it will try to send a "bell" to your terminal
            if f['name'] == "CHO5 - Wexford (Whitemill) - Self Referral" and appts != 0:
                try:
                    ### MacOS has the `say` command
                    os.system(f'say "{appts} appointments available at {f["name"]} in county {county["name"]}"')
                except:
                    ### Otherwise send a "bell" to the terminal
                    print("\a")
                print("\n\n")
                print("-----!!!!!!!!!-----")
                print(f"{appts} - APPOINTMENT(S) AVAILABLE AT {f['name']} in {county['name']} - found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-----!!!!!!!!!-----")
                print("\n\n")
            slot_log = slot_log.append(pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), county['name'], f['name'], appts, slots]], columns = ["timestamp", "county", "centre", "appts", "slots"])).reset_index().drop(['index'], axis=1)
        print()
    ### log slots available
    ### for first run, comment out the following and use this to create the log file:
    # slot_log.to_csv("rest_log.csv")
    logs = pd.read_csv("rest_log.csv")
    logs = pd.concat([logs, slot_log])
    logs = logs.reset_index().drop(['index', 'Unnamed: 0'], axis=1)
    logs.to_csv("rest_log.csv")

    # sleep between runs
    time.sleep(10)
