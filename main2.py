from datetime import date, datetime

today = datetime.today()
day_of_week = date.weekday(today)

if day_of_week == 5:
    pass
elif day_of_week == 6:
    pass
else:
    pass