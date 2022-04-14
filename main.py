import requests as req
from json import dumps
from datetime import datetime
from bs4 import BeautifulSoup

if __name__ == "__main__":
    EMAIL = ""
    PASSWORD = ""
    date = datetime.now()

    URL = "https://www.mittlivsstil.se/umbraco/surface/ActivitySchedule/SearchActivitiesByWeekAndYear?locale=sv-SE&referrer=2818"
    DATA = {
        "year": date.year,
        "week": int(date.strftime("%U"))+1, #https://www.w3schools.com/python/python_datetime.asp
        "units": 1, #idk what this is, just show one week???
        "productIds": 1527, #ID for badminton on mittlivsstil
        "locale": "sv-SE"
    }
    site = req.post(URL, data=DATA)
    soup = BeautifulSoup(site.text, 'html.parser')

    #Get information
    freeSlots = {
        "tisdag":0,
        "onsdag":0,
        "torsdag":0
    }
    bookingQuery = {
        "tisdag":"",
        "onsdag":"",
        "torsdag":""
    }
    for day in soup.find_all('li', {'class': 'day'}):
        currDay = day['data-title']
        slots = day.find_all('div', {'class', 'status'})[1].find('span', {'class', 'hint--left'}).text.strip()
        urlQuery = day.find('div', {'class', 'button-holder'}).find('a').attrs["href"]

        freeSlots[currDay] = slots
        bookingQuery[currDay] = urlQuery
    
    #Auth
    client = req.Session() #Keep Session
    client.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"})
    r = client.get("https://www.mittlivsstil.se/umbraco/Surface/User/UserLogin")

    login_soup = BeautifulSoup(r.content, "html.parser")
    verToken = login_soup.find("input", {"name": "__RequestVerificationToken"})["value"]

    data = {
        "Username":EMAIL,
        "Password":PASSWORD,
        "__RequestVerificationToken": verToken,
        "X-Requested-With": "XMLHttpRequest"
    }
    r = client.post("https://www.mittlivsstil.se/umbraco/Surface/User/UserLogin", data=data)
    if r.json()["Success"] != True:
        print("Login failed")
        exit
    else:
        print("Login Successful")
    
    #Book badminton
    r = client.get("https://www.mittlivsstil.se"+bookingQuery["tisdag"])
    booking_soup = BeautifulSoup(r.content, "html.parser")
    
    ActivityId = booking_soup.find("input", {"name": "ActivityId"})["value"]
    BookingId = booking_soup.find("input", {"name": "BookingId"})["value"]
    Title = booking_soup.find("input", {"name": "Title"})["value"]
    Location = booking_soup.find("input", {"name": "Location"})["value"]
    StartDate = booking_soup.find("input", {"name": "StartDate"})["value"]
    StopDate = booking_soup.find("input", {"name": "StopDate"})["value"]
    WaitingList = booking_soup.find("input", {"name": "WaitingList"})["value"]

    data = {
        "ActivityId": ActivityId,
        "BookingId": BookingId,
        "ProductId": 0,
        "EventId": 0,
        "ServiceData": "",
        "Title": Title,
        "Location": Location,
        "StartDate": StartDate,
        "StopDate": StopDate,
        "WaitingList": WaitingList
    }
    r = client.post("https://www.mittlivsstil.se/umbraco/Surface/Booking/AddBooking", data=data)
    if(r.status_code == 200):
        print("Booking successful")
    else:
        print("Booking failed")