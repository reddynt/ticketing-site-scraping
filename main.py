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
    message["Subject"] = f"KGF Chapter-2. New theatres: {len(theatres)}"
    
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # message.attach(part1)
    message.attach(part2)

    # sending email
    port = 465
    password = "gmaiL.t#3n"

    # create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("tharun313@gmail.com", password)
        sender_email = "tharun313@gmail.com"
        reciever_email = "bujalapravalikareddy@gmail.com"
        # message = "\n" + json.dumps(theatres)
        server.sendmail(sender_email, reciever_email, message.as_string())

    print(f"Email sent. Sleeping for {sleep_time} secs.")
    time.sleep(sleep_time)


# <div class="showtime-pill-container" data-online="Y">
# <a class="showtime-pill" data-attributes="" 
# data-availability="A" data-cat-popup='[{"price":"175.00","desc":"Balcony","availabilityClass":"_available","availabilityText":"Available"}]' 
# data-cut-off-date-time="202204100815" data-date-time="10:45 AM" data-display-showtime="10:45 AM" data-event-id="ET00094579" data-is-atmos-enabled="N" 
# data-is-unpaid="0" data-price-filter-index="[2]" data-seats-percent="89" data-session-id="20798" data-session-popup-desc="" 
# data-showtime-code="1045" data-showtime-filter-index="morning" data-unpaid-quota="0" data-venue-code="PTTH" href="/booktickets/PTTH/20798">