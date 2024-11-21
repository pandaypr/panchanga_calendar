import os

import pyquery as pq
import requests
import shubhlipi as sh
from typer import Typer
from rich.prompt import Confirm
from rich.console import Console
from time_info import DAYS_IN_MONTH

app = Typer()
console = Console()


URL = "https://www.drikpanchang.com/panchang/day-panchang.html?date={date}"
HTML_DATA_FOLDER = "raw_html"
START_YEAR = 2024
END_YEAR = 2026


def get_url(date: list[int]):
    """`date` -> `[day, month, year]`"""
    str_date = f"{sh.prefix_zeros(date[0], 2)}/{sh.prefix_zeros(date[1], 2)}/{date[2]}"
    return URL.format(date=str_date)


def get_html(url: str, date: list[int]):
    try:
        date_str = f"{date[2]}-{date[1]}-{date[0]}"
        html = requests.get(url).text
        sh.write(f"{HTML_DATA_FOLDER}/{date_str.replace("/", '-')}.html", html)
        console.print(f"[green]Downloaded [/] {date_str}")
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
                url = get_url(date)
                get_html(url, date)

            for day in range(1, DAYS_IN_MONTH[month - 1] + 1):
                process_date(day)
            if year % 4 == 0 and month == 2:
                # leap year
                process_date(29)


if __name__ == "__main__":
    app()
