from datetime import date
import uuid

from icalendar import Calendar, Event
import shubhlipi as sh
from typer import Typer
from rich.console import Console


app = Typer()
console = Console()


@app.command()
def main():
    calendar = Calendar()
    calendar.add("prodid", "-//Panchanga 2024-2026//mxm.dk//")  # Identifier
    calendar.add("version", "2.0")
    calendar.add("x-wr-calname", "panchanga_2024_2026")  # Name of the calendar
    calendar.add("x-wr-timezone", "Asia/Kolkata")

    event = Event()
    event.add("summary", "Test Event")  # Event title
    event.add("dtstart", date(2024, 11, 20))  # Start time
    event.add("dtend", date(2024, 11, 20))  # End time
    event.add("status", "CONFIRMED")
    # set generated from uuid lib
    event.add("uid", str(uuid.uuid4()))

    calendar.add_component(event)

    with open("out/panchanga.ics", "wb") as file:
        file.write(calendar.to_ical())

    # replace \r\n with \n
    file = sh.read("out/panchanga.ics")
    file = file.replace("\r\n", "\n")
    sh.write("out/panchanga.ics", file)


if __name__ == "__main__":
    app()
