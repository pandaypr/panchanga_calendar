import datetime
import os

from icalendar import Calendar, Event
import shubhlipi as sh
from typer import Typer
from rich.console import Console
import yaml

from get_data import PanchangaInfo

app = Typer()
console = Console()


def get_month_events(month_data: list[PanchangaInfo], icloud=False) -> list[Event]:
    # Rules for Summary Syntax
    # Titihi (Time of Titihi), Nakshatra, Tithi(Both), Rtu

    events: list[Event] = []

    def get_tithi(val: str, date: datetime.date) -> str:
        tithi_name = val.split("-")[0].split("Paksha")[1].strip().split(" ")[0].strip()
        # ^ Also ignoring the second word which come after name, like "Tithi Vriddhi"

        time_string = val.split("-")[1].split("–")[1].strip()
        parsed_time = datetime.datetime.strptime(
            f"{date.year} {time_string}", "%Y %b %d %I:%M %p"
        ).timetuple()
        year = parsed_time.tm_year
        month = parsed_time.tm_mon
        day = parsed_time.tm_mday
        hour = parsed_time.tm_hour
        minute = parsed_time.tm_min

        plus_sign = (
            "+" if date.year != year or date.month != month or date.day != day else ""
        )
        # A + sign should be added if the upto date is one day ahead

        return f"{tithi_name} ({plus_sign}{sh.prefix_zeros(hour,2)}:{sh.prefix_zeros(minute,2)})"

    for data in month_data:
        event = Event()

        date = datetime.date(data.date[2], data.date[1], data.date[0])
        tithi = get_tithi(data.tithi[0], date)
        nakshatra = data.nakshatra[0].split("-")[0].strip()
        month = f"{data.amanta_month}(A)/{data.purnimanta_month}(P)"
        Rtu = data.dRika_Rtu.strip().split(" ")[0]
        summary = f"{tithi}, {nakshatra}, {month}, {Rtu}"
        event.add("summary", summary)
        event.add("dtstart", date)
        event.add("dtend", date)
        event.add("transp", "TRANSPARENT")  # Mark event as "busy"
        event.add("status", "CONFIRMED")
        date_string = (
            f"{sh.prefix_zeros(date.day,2)}/{sh.prefix_zeros(date.month,2)}/{date.year}"
        )
        if not icloud:
            event.add(
                "description",
                f'<a href="https://www.drikpanchang.com/panchang/day-panchang.html?date={date_string} target="_blank">Drikpanchanaga for <strong>{date_string}</strong></a>',
            )
        elif icloud:
            event.add(
                "description",
                f"Drikpanchanaga for {date_string} : https://www.drikpanchang.com/panchang/day-panchang.html?date={date_string}",
            )
        events.append(event)

    return events


def make_calendar(filename: str, icloud_compatible=False):
    out_file = f"out/{filename}"

    calendar = Calendar()
    calendar.add("prodid", "-//TheSanskritChannel//mxm.dk//")  # Identifier
    calendar.add("version", "2.0")
    calendar.add("x-wr-calname", "Panchanga 2024-2026")  # Name of the calendar
    calendar.add("x-wr-timezone", "Asia/Kolkata")

    for root, dirs, files in os.walk("data"):
        for file in files:
            data_dict_list = yaml.safe_load(sh.read(os.path.join(root, file)))
            data_list: list[PanchangaInfo] = []
            for data_dict in data_dict_list:
                data_list.append(PanchangaInfo(**data_dict_list[data_dict]))
            events = get_month_events(data_list, icloud_compatible)
            for event in events:
                calendar.add_component(event)

    with open(out_file, "wb") as file:
        file.write(calendar.to_ical())

    # replace \r\n with \n
    file = sh.read(out_file)
    file = file.replace("\r\n", "\n")
    sh.write(out_file, file)


@app.command()
def main():
    if not os.path.isdir("data"):
        console.print("[red bold]Data folder not found[/]")
        return

    console.log("[blue bold]Started Making Calendar...[/]")

    make_calendar("panchanga.ics", icloud_compatible=True)
    make_calendar("panchanga_icloud.ics", icloud_compatible=True)
    make_calendar("panchanga_google.ics", icloud_compatible=False)

    console.log("[green bold]Finished Making Calendar...[/]")


if __name__ == "__main__":
    app()
