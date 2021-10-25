import requests
from secret import url
from bs4 import BeautifulSoup

# Fetch Site
site = requests.get(url)

# make use of beautifulsoap to parse the site
soup = BeautifulSoup(site.text, 'html.parser')

data = []
for day in soup.find_all('li', {'class': 'day'}):
    value = []

    # Find Weekday
    value.append(day.find('h5', {'class', 'brand-font'}).text.strip())

    # Find Time
    activity_full = day.find('li', {'class', 'activity full'})
    time = activity_full.find('div', {'class', 'time'})
    value.append(time.find('h6').text.strip())

    # Find free slots
    status = activity_full.find('div', {'class', 'status'})
    value.append(status.find('h6').find('span').text.strip())

    data.append(value)

print(data)