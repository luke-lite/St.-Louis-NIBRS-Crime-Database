from datetime import datetime

date = '12-2023'
date_obj = datetime.strptime(date, '%m-%Y')
update_date = date_obj.strftime('%B%Y')
print(update_date)
