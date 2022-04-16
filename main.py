import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import requests
import smtplib, ssl
from bs4 import BeautifulSoup

url = "https://in.bookmyshow.com/buytickets/k-g-f-chapter-2-hyderabad/movie-hyd-ET00312036-MT/20220414"
old_theatres = []

while True:
    sleep_time = random.randint(25, 50)
    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")

    theatres = []

    venue_list = soup.find("ul", {"id": "venuelist"})

    html = """\
        <ul>
        """

    for venue in venue_list.findAll("li"):
        if venue["data-name"] in old_theatres:
            continue
        theatre_atts = {}
        theatre_atts["name"] = venue["data-name"]
        showtimes = venue.findAll("a", {"class": "showtime-pill"})
        shows = []
        is_atmos_enabled = False
        for showtime in showtimes:
            showtime_atts = {}
            try:
                availability = True if "Available" in showtime["data-cat-popup"] else False
                if not availability:
                    break
                showtime_atts["time"] = showtime.text.strip()
                showtime_atts["is_atmos"] = False if showtime["data-is-atmos-enabled"]=="N" else True
                if showtime_atts["is_atmos"]:
                    is_atmos_enabled = True
                if showtime_atts:
                    shows += [showtime_atts]
            except KeyError as ke:
                pass
        if shows:
            theatre_atts["showtime"] = shows
            theatres += [theatre_atts]
            html += f"<li>{venue['data-name']} ; atmos_enabled: {is_atmos_enabled}</li>"
        old_theatres.append(venue["data-name"])
    html += "</ul>"
    
    if not theatres:
        print(f"No new theatres! Sleeping for {sleep_time} secs")
        time.sleep(sleep_time)
        continue

    print(f"Total new theatres: {len(theatres)}")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"New theatres: {len(theatres)}"
    
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # message.attach(part1)
    message.attach(part2)

    # sending email
    port = 465

    # create a secure SSL context
    context = ssl.create_default_context()

    sender_email = input("Enter your email ID: ")
    password = input("Input your password and hit Enter: ")
    receiver_email = input("Enter receiver email ID: ")

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(user_email, password)
        server.sendmail(sender_email, reciever_email, message.as_string())

    print(f"Email sent. Sleeping for {sleep_time} secs.")
    time.sleep(sleep_time)
