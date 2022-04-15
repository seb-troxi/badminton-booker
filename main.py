import requests as req
from datetime import datetime
from bs4 import BeautifulSoup
import time

def GetDays():
    freeSlots = {}
    bookingQuery = {}
    while True:
        try:
            date = datetime.now()
            DATA = {
                "year": date.year,
                "week": int(date.strftime("%U"))+1, #https://www.w3schools.com/python/python_datetime.asp
                "units": 1, #idk what this is, just show one week???
                "productIds": 1527, #ID for badminton on mittlivsstil
                "locale": "sv-SE"
            }
            #Get all badminton days for the next week
            site = req.post("https://www.mittlivsstil.se/umbraco/surface/ActivitySchedule/SearchActivitiesByWeekAndYear?locale=sv-SE&referrer=2818", data=DATA)
            soup = BeautifulSoup(site.text, 'html.parser')

            #Extract information
            for day in soup.find_all('li', {'class': 'day'}):
                currDay = day['data-title']

                #slots = day.find_all('div', {'class', 'status'})[1].find('span', {'class', 'hint--left'}).text.strip()
                urlQuery = day.find('div', {'class', 'button-holder'}).find('a').attrs["href"]

                #freeSlots[currDay] = slots
                bookingQuery[currDay] = urlQuery
            
            return (freeSlots, bookingQuery)
        except Exception:
            print("Can't get badminton info, retry in 5 seconds")
            time.sleep(5)

def Auth(client):
    tries = 0
    while True:
        try:
            tries = tries + 1

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

            return r.json()["Success"]
        except Exception:
            print("Login problem retries in 5 sec, try: "+str(tries))
            time.sleep(5)

def BookSession(client):
    while True:
        try:
            r = client.get("https://www.mittlivsstil.se"+query["onsdag"])
            booking_soup = BeautifulSoup(r.content, "html.parser")
            
            ActivityId = booking_soup.find("input", {"name": "ActivityId"})["value"]
            BookingId = booking_soup.find("input", {"name": "BookingId"})["value"]
            Title = booking_soup.find("input", {"name": "Title"})["value"]
            Location = booking_soup.find("input", {"name": "Location"})["value"]
            StartDate = booking_soup.find("input", {"name": "StartDate"})["value"]
            StopDate = booking_soup.find("input", {"name": "StopDate"})["value"]
            WaitingList = booking_soup.find("input", {"name": "WaitingList"})["value"]

            if WaitingList == "True":
                print("Full queue. DAMN THESE BOTS :(")
                return False

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
            r = client.post("https://www.mittlivsstil.se/umbraco/Surface/Booking/AddBooking?locale=sv", data=data)
            success_soup = BeautifulSoup(r.content, "html.parser")
            success = success_soup.find("a", {"class": "facebook-post-ui"})

            #SUCCESS
            if(success != None):
                return data

            return False
        except Exception:
            print("Can't book session, retry in 5 seconds")
            time.sleep(5)

if __name__ == "__main__":
    #Credentials, could be in a external 'secret' file
    EMAIL = ""
    PASSWORD = ""

    #Get badminton days and their information
    (slots, query) = GetDays()

    #Auth
    client = req.Session() #Keep Session
    loginSuccess = Auth(client)
    if loginSuccess:
        print("Login Successful")
    else:
        print("Login failed (bad credentials), exiting")
        exit()

    #Book badminton
    booking = BookSession(client)
    if booking != False:
        print(f"Booking Successful\nStart: {booking['StartDate']}\nStop: {booking['StopDate']}")
    else:
        print("Booking failed, maybe you have already booked it")