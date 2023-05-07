import requests
from datetime import date, timedelta

def get_holidays(year, country_code):
    response = requests.get(f"https://date.nager.at/api/v3/publicholidays/{year}/{country_code}")
    list_of_public_holidays = []
    for holiday in response.json():
        list_of_public_holidays.append(holiday['date'])
    return list_of_public_holidays

def get_weekends(year):
    list_of_weekends = []
    d = date(year, 1, 1)                    # January 1st
    d += timedelta(days = 6 - d.weekday())  # First Sunday
    while d.year == year:
        saturday = d - timedelta(days=1)
        if saturday.year == year:
            list_of_weekends.append(saturday.strftime('%Y-%m-%d'))
        list_of_weekends.append(d.strftime('%Y-%m-%d'))
        d += timedelta(days = 7)
    return list_of_weekends
    

def get_leave_days(year, country_code):
    list_of_holidays = sorted(list(set(get_weekends(year) + get_holidays(year, country_code))))
    return list_of_holidays


def get_bridge_days(list_of_holidays, threshold=3):
    list_of_bridge = []
    for i in range(len(list_of_holidays) - 1):
        d1 = date.fromisoformat(list_of_holidays[i])
        d2 = date.fromisoformat(list_of_holidays[i + 1])
        working_days = d2 - d1 - timedelta(days=1)
        if 1 <= working_days.days < threshold:
            for j in range(working_days.days):
                list_of_bridge.append((d1 + timedelta(days=j + 1)).strftime('%Y-%m-%d'))
    return list_of_bridge

def get_consecutive_days(list_of_leave_days):
    consecutive = False
    list_of_consecutive_days = []
    group_holidays = []
    consecutive_days = 0

    for i in range(len(list_of_leave_days) - 1):
        d1 = date.fromisoformat(list_of_leave_days[i])
        d2 = date.fromisoformat(list_of_leave_days[i + 1])
        group_holidays.append(d1.strftime('%Y-%m-%d'))
        delta = d2 - d1
        if delta.days == 1:
            consecutive = True
            consecutive_days += 1
            
        else:
            consecutive = False
            consecutive_days = 0
            if len(group_holidays) > 2:
                list_of_consecutive_days.append(group_holidays)
            group_holidays = []
    return list_of_consecutive_days


def main():
    list_of_holidays = get_leave_days(2023, 'JP')
    list_of_bridge = get_bridge_days(list_of_holidays, 5)
    list_of_leave_days = sorted(list_of_holidays + list_of_bridge)
    list_of_consecutive_days = get_consecutive_days(list_of_leave_days)

    leave_days = {}
    pto_days = []

    for group in list_of_consecutive_days:
        for date in list_of_bridge:
            if date in group:
                pto_days.append(date)
        key = str(group[0]) + ' - ' + str(group[-1]) + ', ' + str(len(group)) + ' days'
        leave_days[key] = leave_days.get(key, []) + pto_days
        pto_days = []
    print("Long holiday dates \t\t| PTO days")
    for key, value in leave_days.items():
        print(f"{key} : {value}")
    print(f"Total PTO taken: {len(list_of_bridge)}")

if __name__ == '__main__':
    main()



                
                



