import requests
import json
from time import sleep
from pprint import pprint
from datetime import date, timedelta, datetime


def main():
        with open("./config.json", "r") as config, open("./restaurants.json", "r") as restaurants:
            cfg = json.load(config)

            restaurant = cfg["restaurant"]
            from_date = cfg["from_date"]
            to_date = cfg["to_date"]
            from_time = cfg["from_time"]
            to_time = cfg["to_time"]

            restaurants_dict = json.load(restaurants)
            restaurant_dict = restaurants_dict[restaurant]
            dates_to_check = [str(str_to_date(from_date)+timedelta(days=x+1)) for x in range((str_to_date(to_date)-str_to_date(from_date)).days)]
            available_times = {k: [] for k in dates_to_check}
            table_found = False

            while not table_found:
                now = datetime.now()

                if now.time() <= datetime.strptime(cfg["booking_release_time"], '%H:%M:%S').time():
                    print(f"Time is not {cfg['booking_release_time']} yet. Waiting...")
                    sleep(cfg['checking_delay'])
                    continue

                print(f"INFO: Checking dates: {dates_to_check}")
                for date in dates_to_check:

                    # Create request
                    body_times = f"{{'testmode':0,'date_code':'','date':'{date}','amount':{cfg['num_people']},'mealid':'{restaurant_dict['mealId']}','mc_code':'','hd_meal':'','hash':'{restaurant_dict['hash']}','int_test':'N','{restaurant_dict['key']}':'{restaurant_dict['keyValue']}'}}".replace(
                        "'", '\"')

                    # Fetch times
                    res = requests.post("https://app.waiteraid.com/booking-widget/api/getTimes", data=body_times,
                                        headers={"referer": restaurant_dict["hash"]})

                    res_dict = json.loads(res.text)

                    if "times" in res_dict: # Nested if:s to ensure order.
                        if(len(res_dict["times"]) > 0):
                            for key, time_tuple in res_dict["times"].items():
                                available_times[date].append(time_tuple[0])

                filtered_slots = {k: [] for k in available_times.keys()}

                for date, times in available_times.items():
                    if date not in cfg['ignore_dates']:
                        if(len(times) > 0):
                            for time in times:
                                if is_time_between(from_time, to_time, time):
                                    filtered_slots[date].append(time)

                if not is_array_dict_empty(filtered_slots):
                    print(f"INFO: Found desired slots: {filtered_slots}")
                    for date, times in filtered_slots.items():
                        for time in times:
                            save_body = format_save_body(restaurant_dict, cfg['firstname'], cfg['lastname'], cfg['email'], cfg['phone_number'], cfg['num_people'], date, time)
                            print(f"INFO: Attempting to submit: {save_body}")

                            book_res = requests.post("https://app.waiteraid.com/reservation/api/booking/saveBooking",
                                               data=save_body)

                            book_res_dict = json.loads(book_res.text)
                            if book_res_dict["success"]:
                                pprint(book_res_dict)
                                print("Booked a table!")
                                input("Press enter to try to book next...")
                            else:
                                pprint(book_res_dict)
                                print("Failed to book available table")
                                input("Press enter to try to book next...")
                else:
                    print("INFO: No available times found!")

def is_time_between(begin_time, end_time, check_time=None):
    # Taken from https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def str_to_date(str):
    return datetime.strptime(str, "%Y-%m-%d").date()

def format_save_body(restaurant_dict, name, last_name, email, phone_number, num_people, date, time):
    return f"{{'mealid':'{restaurant_dict['mealId']}'," \
                f"'firstname':'{name}'," \
                f"'lastname':'{last_name}'," \
                f"'email':'{email}'," \
                f"'phone':'{phone_number}'," \
                f"'country_code':'+46'," \
                f"'dial_code':'+46'," \
                f"'amount':{num_people}," \
                f"'date':'{date}'" \
                f",'offer_ID':0," \
                f"'time':'{time}'," \
                f"'bookingid':0," \
                f"'comment':''," \
                f"'waitlist':false," \
                f"'waitlist_end':null," \
                f"'length':{restaurant_dict['length']}," \
                f"'saveinfo':1," \
                f"'hd_meal':''," \
                f"'ap_label':''," \
                f"'testmode':0," \
                f"'mc_code':''," \
                f"'from_url':''," \
                f"'hash':'{restaurant_dict['hash']}'," \
                f"'date_code':''," \
                f"'products':[]," \
                f"'segment':''," \
                f"'terms':{{'general':true,'restaurant':true,'bokabord':true}}," \
                f"'temp_sid':''," \
                f"'waitb':''," \
                f"'city':''," \
                f"'widget_lang':''," \
                f"'{restaurant_dict['key']}':'{restaurant_dict['keyValue']}'}}".replace("\'", '"')

def is_array_dict_empty(dict):
    is_empty = True
    for key, value in dict.items():
        if len(value) > 0:
            is_empty = False
    return is_empty


if __name__ == '__main__':
    main()