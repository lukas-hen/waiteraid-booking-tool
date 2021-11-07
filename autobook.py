import click
import requests
import json
from time import sleep
from pprint import pprint
from datetime import date, timedelta, datetime




@click.command()
@click.argument("arg")
@click.option("--from_date", "-fd")
@click.option("--to_date", "-td")
@click.option("--from_time", "-ft")
@click.option("--to_time", "-tt")
@click.option("--num_people", "-p", default=1)
@click.option("--restaurant", "-r")
@click.option("--name", "-n")
@click.option("--last_name", "-ln")
@click.option("--email", "-e")
@click.option("--phone_number", "-pn")
@click.option("--interval", "-i")
def main(arg, from_date, to_date, from_time, to_time, num_people, restaurant, name, last_name, email, phone_number, interval):
    match arg:
        case "fetch":
            with open("./restaurants.json", "r") as restaurants:
                restaurants_dict = json.load(restaurants)
                restaurant_dict = restaurants_dict[restaurant]
                dates_to_check = [str(str_to_date(from_date)+timedelta(days=x)) for x in range((str_to_date(to_date)-str_to_date(from_date)).days)]
                available_times = {k: [] for k in dates_to_check}
                table_found = False

                while not table_found:

                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print("Current Time =", current_time)

                    if now.time() <= datetime.strptime('09:59:50', '%H:%M:%S').time():
                        print("Time is not 09:59:50 yet. Waiting...")
                        sleep(0.2)
                        continue

                    print(f"INFO: Checking dates: {dates_to_check}")
                    for date in dates_to_check:

                        # Create request
                        body_times = f"{{'testmode':0,'date_code':'','date':'{date}','amount':{num_people},'mealid':'{restaurant_dict['mealId']}','mc_code':'','hd_meal':'','hash':'{restaurant_dict['hash']}','int_test':'N','{restaurant_dict['key']}':'{restaurant_dict['keyValue']}'}}".replace(
                            "'", '\"')
                        #print(f"INFO: Sending request: {body_times}")

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
                        if date != "2021-12-24" and date != "2021-12-23" and date != "2021-12-25":
                            if(len(times) > 0):
                                for time in times:
                                    if is_time_between(from_time, to_time, time):
                                        filtered_slots[date].append(time)

                    if not is_array_dict_empty(filtered_slots):
                        print(f"INFO: Found desired slots: {filtered_slots}")
                        for date, times in filtered_slots.items():
                            for time in times:
                                save_body = format_save_body(restaurant_dict, name, last_name, email, phone_number, num_people, date, time)
                                print(f"INFO: Attempting to submit: {save_body}")

                                res = requests.post("https://app.waiteraid.com/reservation/api/booking/saveBooking",
                                                   data=save_body)

                                res_dict = json.loads(res.text)
                                if res_dict["success"]:
                                    pprint(res_dict)
                                    print("Booked a table!")
                                    input("Press enter to try to book next...")
                                else:
                                    pprint(res_dict)
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


"""

Notes:
python3 autobook.py fetch -r frantzen -p 3 -fd 2021-11-04 -td 2021-11-07 -ft -17:00 -tt 21:00 -n Lukas -ln Hennicks -e hennicks.lukas@gmail.com -pn 0732099090

https://app.waiteraid.com/reservation/api/booking/saveBooking
{"mealid":"146","firstname":"Lukas","lastname":"Hennicks","email":"hennicks.lukas@gmail.com","phone":"0732099090","country_code":"+46","dial_code":"+46","amount":3,"date":"2021-11-04","offer_ID":0,"time":"15:30","bookingid":0,"comment":"","waitlist":false,"waitlist_end":null,"length":105,"saveinfo":1,"hd_meal":"","ap_label":"","testmode":0,"mc_code":"","from_url":"","hash":"0195100c20f372753761a0bbb861f027","date_code":"","products":[],"segment":"","terms":{"general":true,"restaurant":false,"bokabord":false},"temp_sid":"","waitb":"","city":"","widget_lang":"","eHI3SDBEalpkREFNNkhWeW5zQ1hPaDBNMllFPQ":"L2NoYXZMbz0"}

"times":{"46800":["14:00",1637240400]
"times":{"46800":["14:00",1637240400],"47700":["14:15",1637241300],"48600":["14:30",1637242200]}

#body=f"{{'from':'{from_date}','to':'{to_date}','date':'{now}','amount':{num_people}, 'mealid':'{restaurant_dict['mealId']}','hash':'{restaurant_dict['hash']}','{restaurant_dict['key']}':'{restaurant_dict['keyValue']}'}}".replace("'", '\"')
{"from":"2021-11-03","to":"2021-11-27","date":"2021-11-03","amount":3,"mealid":"5123","hash":"77779be66a85c01c2efe78905bbf67e9","ZUc2NUxZS2xKbHlPQzVzM1Rib1FjbHNW":"cjdpQk5kV1hsQzdmanpKMEQ5MVY1UT09"}

{"testmode":0,"date_code":"","date":"2021-11-11","amount":3,"mealid":"5123","mc_code":"","hd_meal":"","hash":"77779be66a85c01c2efe78905bbf67e9","int_test":"N","ZUc2NUxZS2xKbHlPQzVzM1Rib1FjbHNW":"cjdpQk5kV1hsQzdmanpKMEQ5MVY1UT09"}


{"success":true,"msg":"","short_lengths":[],"time_now":1509,"wl_full":[],"lengths":{"146":{"14:00":105,"14:15":105,"14:30":105,"14:45":105,"15:00":105,"15:15":105,"15:30":105,"15:45":105,"16:00":105,"16:15":105,"16:30":105,"16:45":105,"17:00":105,"17:15":105,"17:30":105,"17:45":105,"18:00":105,"18:15":105,"18:30":105,"18:45":105,"19:00":105,"19:15":105,"19:30":105,"19:45":105,"20:00":105,"20:15":105,"20:30":105,"20:45":105,"21:00":105,"21:15":105,"21:30":105,"21:45":105,"22:00":105}},"too_late":[],"alt_meal_obj":false,"stop_time":[],"full_text":{"18:30":2,"22:00":2},"full_text_labels":{"type_1":"Fullbokad l\u00e4gg till v\u00e4ntelista?","type_2":"Fullbokad l\u00e4gg till v\u00e4ntelista?","type_3":"F\u00f6r sent att boka online.","type_4":"F\u00f6r sent att boka online","type_9":"V\u00e4ntelista fulltecknad"},"alt_meal":0,"ap_labels":[],"times":{"46800":["14:00",1637240400],"47700":["14:15",1637241300],"48600":["14:30",1637242200],"49500":["14:45",1637243100],"50400":["15:00",1637244000],"51300":["15:15",1637244900],"52200":["15:30",1637245800],"53100":["15:45",1637246700],"54000":["16:00",1637247600],"54900":["16:15",1637248500],"55800":["16:30",1637249400],"56700":["16:45",1637250300],"57600":["17:00",1637251200],"58500":["17:15",1637252100],"59400":["17:30",1637253000],"60300":["17:45",1637253900],"61200":["18:00",1637254800],"62100":["18:15",1637255700],"63900":["18:45",1637257500],"64800":["19:00",1637258400],"65700":["19:15",1637259300],"66600":["19:30",1637260200],"67500":["19:45",1637261100],"68400":["20:00",1637262000],"69300":["20:15",1637262900],"70200":["20:30",1637263800],"71100":["20:45",1637264700],"72000":["21:00",1637265600],"72900":["21:15",1637266500],"73800":["21:30",1637267400],"74700":["21:45",1637268300]},"full":{"46800":["14:00",1637240400],"47700":["14:15",1637241300],"48600":["14:30",1637242200],"49500":["14:45",1637243100],"50400":["15:00",1637244000],"51300":["15:15",1637244900],"52200":["15:30",1637245800],"53100":["15:45",1637246700],"54000":["16:00",1637247600],"54900":["16:15",1637248500],"55800":["16:30",1637249400],"56700":["16:45",1637250300],"57600":["17:00",1637251200],"58500":["17:15",1637252100],"59400":["17:30",1637253000],"60300":["17:45",1637253900],"61200":["18:00",1637254800],"62100":["18:15",1637255700],"63000":["18:30",1637256600],"63900":["18:45",1637257500],"64800":["19:00",1637258400],"65700":["19:15",1637259300],"66600":["19:30",1637260200],"67500":["19:45",1637261100],"68400":["20:00",1637262000],"69300":["20:15",1637262900],"70200":["20:30",1637263800],"71100":["20:45",1637264700],"72000":["21:00",1637265600],"72900":["21:15",1637266500],"73800":["21:30",1637267400],"74700":["21:45",1637268300]},"alternate_rests":63,"future_availibility":false}

{'booking': {'allergies_confirmed': 0,
             'amount': 3,
             'autopay_activated': None,
             'confirmed': 0,
             'cust_id': 18257871,
             'date': '2021-12-04',
             'email': 'hennicks.lukas@gmail.com',
             'end': 1638639900,
             'eta': 0,
             'firstname': 'Lukas',
             'flags': [],
             'group_booking': False,
             'group_expiry': 0,
             'id': 24416900,
             'langid': 1,
             'lastname': 'Hennicks',
             'meal': {'abbreviation': 'sw:,en:',
                      'active': 1,
                      'allow_if_placed_only': 'Y',
                      'allow_select_seating_time': 'N',
                      'bookable_days': 0,
                      'books_after': '20:00',
                      'cancel_hours': 0,
                      'daily_limit': 0,
                      'date': 0,
                      'dateto': 0,
                      'day1_end': 72000,
                      'day1_start': 46800,
                      'day2_end': 72000,
                      'day2_start': 46800,
                      'day3_end': 75600,
                      'day3_start': 46800,
                      'day4_end': 75600,
                      'day4_start': 46800,
                      'day5_end': 79200,
                      'day5_start': 46800,
                      'day6_end': 79200,
                      'day6_start': 54000,
                      'day7_end': 63900,
                      'day7_start': 46800,
                      'days_disabled': [7],
                      'deleted': 0,
                      'descr': 'a:2:{s:2:"sw";s:68:"Fredagar och lördagar '
                               'efter 21:00 gäller åldersgräns på 23 '
                               'år.";s:2:"en";s:0:"";}',
                      'email_to_rest': 'Y',
                      'enable_auto_placing': 'Y',
                      'gap': -1,
                      'id': 146,
                      'length_min': 105,
                      'length_short_min': 0,
                      'max_amount': 8,
                      'min_amount': 1,
                      'min_time': 'M',
                      'minutes_to_reservation': 30,
                      'must_pay_directly': 'N',
                      'name': 'MIDDAG',
                      'no_show': 'N',
                      'orderby': 3,
                      'ov_id': 0,
                      'restid': 92,
                      'seats_lenght_def': 135,
                      'seats_per_time': 0,
                      'selected_seating_time': 135,
                      'separated': 'N',
                      'short_term_period': 0,
                      'stat_fv': 133,
                      'thumb': 0,
                      'times_visible_full': 'N;',
                      'type': 3,
                      'type_alt': 0,
                      'use_ovl': 1},
             'meal_cost': 0,
             'mealid': 146,
             'no_show_text': '',
             'order_date': 0,
             'parent_order': False,
             'payinwidget': True,
             'phone': '+46 73 209 90 90',
             'products': [],
             'reg_date': 1635748029,
             'require_noshow': False,
             'restid': 92,
             'seating_length': 175,
             'short_code': 't9oH6OYUbY',
             'start': 1638633600,
             'status': 1,
             'time': '17:00',
             'time_formatted': '17:00-18:45',
             'too_late_to_cancel': False,
             'waitlist': 0,
             'widget_confirm_text': ''},
 'messageEnabled': True,
 'msg': '',
 'no_show': False,
 'offer': 0,
 'success': True}

"""