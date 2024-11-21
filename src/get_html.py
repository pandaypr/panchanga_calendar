import os
import time

import requests
import shubhlipi as sh
from typer import Typer
from rich.prompt import Confirm
from rich.console import Console
from time_info import DAYS_IN_MONTH, MONTH_NAMES

app = Typer()
console = Console()


URL = "https://www.prokerala.com/astrology/panchang/{date}.html"
# date format: year-month_name_lower-day
HTML_DATA_FOLDER = "raw_html"
START_YEAR = 2024
END_YEAR = 2026


def get_html(date: list[int]):
    try:
        url = URL.format(
            date=f"{date[2]}-{MONTH_NAMES[date[1] - 1].lower()}-{sh.prefix_zeros(date[0], 2)}"
        )
        console.print(
            f"[bold white]Started {date[2]}-{date[1]}-{date[0]} : [/]",
            end="",
        )
        date_str = f"{date[2]}-{date[1]}-{date[0]}"
        req = requests.get(
            url,
            headers={
                "User-Agent": "Mozila/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
            },
        )
        if not req.ok:
            raise Exception(
                f"Error while downloading {date_str}, code: {req.status_code}"
            )
        html = req.text
        sh.write(f"{HTML_DATA_FOLDER}/{date_str.replace("/", '-')}.html", html)
        console.print(f"[green]Downloaded [/]")
        time.sleep(10)
    except Exception as e:
        console.print(f"[red bold]Error while downloading [/] {date_str}", e)


@app.command()
def main(del_folder: bool = False):
    if os.path.isdir(HTML_DATA_FOLDER):
        if not del_folder:
            del_folder_ask = Confirm.ask(
                "[bold][white]Folder already exists[/][red] sure to delete it ?[/][/]"
            )
            if not del_folder_ask:
                return
        sh.delete_folder(HTML_DATA_FOLDER)

    os.mkdir(HTML_DATA_FOLDER)

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):

            def process_date(day: int):
                date = [day, month, year]
                get_html(date)

            for day in range(1, DAYS_IN_MONTH[month - 1] + 1):
                process_date(day)
            if year % 4 == 0 and month == 2:
                # leap year
                process_date(29)


if __name__ == "__main__":
    app()
