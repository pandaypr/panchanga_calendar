import os

from typer import Typer
from rich.console import Console
from pyquery import PyQuery as pq
from pydantic import BaseModel
import shubhlipi as sh
import yaml

app = Typer()
console = Console()

DATA_OUT_PATH = "data"


class PanchangaInfo(BaseModel):
    date: list[int]  # day, month, year
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    vikram_samvat_date: str
    shakaka_samvat_date: str
    purnimanta_month: str  #
    amanta_month: str  #
    tithi: list[str]  #
    nakshatra: list[str]
    dRika_Rtu: str  #
    vedic_Rtu: str


def get_data(file_name: str):
    year = int(file_name.split("/")[-1].split(".")[0].split("-")[0])
    month = int(file_name.split("/")[-1].split(".")[0].split("-")[1])
    day = int(file_name.split("/")[-1].split(".")[0].split("-")[2])

    html = pq(sh.read(file_name))

    # Sunrise, Sunset, Moonrise, Moonset
    sun_moon_info_list_q = html(".panchang-data-sun_moon_timing > ol li")
    sunrise: str = sun_moon_info_list_q.eq(0).text().split("-")[1].strip()
    sunset: str = sun_moon_info_list_q.eq(1).text().split("-")[1].strip()
    moonrise: str = sun_moon_info_list_q.eq(2).text().split("-")[1].strip()
    moonset: str = sun_moon_info_list_q.eq(3).text().split("-")[1].strip()

    # Vikram Samvat, Shakaka Samvat, Purnimanta Month, Amanta Month
    year_month_info_list_q = html(".panchang-data-day > ol li")
    vikram_samvat_date: str = year_month_info_list_q.eq(0).text().split("-")[1].strip()
    shakaka_samvat_date: str = year_month_info_list_q.eq(1).text().split("-")[1].strip()
    purnimanta_month: str = year_month_info_list_q.eq(2).text().split("-")[1].strip()
    amanta_month: str = year_month_info_list_q.eq(3).text().split("-")[1].strip()

    # Tithi, Nakshatra
    tithi_list_q = html(".panchang-data-tithi > ol li")
    tithi: list[str] = []
    for i in range(len(tithi_list_q)):
        tithi.append(tithi_list_q.eq(i).text().strip().replace("\xa0 ", ""))
    nakshatra_list_q = html(".panchang-data-nakshatra > ol li")
    nakshatra: list[str] = []
    for i in range(len(nakshatra_list_q)):
        nakshatra.append(nakshatra_list_q.eq(i).text().strip())

    # DRka Rtu, Vedic Rtu
    lunar_month_info_list_q = html(".panchang-data-lunar-month > ol li")
    dRika_Rtu: str = lunar_month_info_list_q.eq(3).text().split("-")[1].strip()
    vedic_Rtu: str = lunar_month_info_list_q.eq(4).text().split("-")[1].strip()

    panchanga_info = PanchangaInfo(
        date=[day, month, year],
        sunrise=sunrise,
        sunset=sunset,
        moonrise=moonrise,
        moonset=moonset,
        vikram_samvat_date=vikram_samvat_date,
        shakaka_samvat_date=shakaka_samvat_date,
        purnimanta_month=purnimanta_month,
        amanta_month=amanta_month,
        tithi=tithi,
        nakshatra=nakshatra,
        dRika_Rtu=dRika_Rtu,
        vedic_Rtu=vedic_Rtu,
    )
    return panchanga_info


@app.command()
def main():
    if not os.path.isdir("raw_html"):
        console.print("[red bold]raw_html folder not found[/]")
        return
    if os.path.isdir(DATA_OUT_PATH):
        sh.delete_folder(DATA_OUT_PATH)
    os.mkdir(DATA_OUT_PATH)
    console.log("[blue bold]Getting data from html files...[/]")
    month_list: dict[str, dict[int, dict]] = {}
    # Contains list of all panchanga info for each month
    for root, dirs, files in os.walk("raw_html"):
        for file in files:
            if file.endswith(".html"):
                data = get_data(os.path.join(root, file))
                key = f"{data.date[2]}-{data.date[1]}"
                if key not in month_list:
                    month_list[key] = {}
                month_list[key][data.date[0]] = data.model_dump()
    for month in month_list:
        sh.write(
            f"{DATA_OUT_PATH}/{month}.yaml",
            yaml.safe_dump(
                month_list[month], allow_unicode=True, indent=2, sort_keys=True
            ),
        )

    console.log(f"[green bold]Data Extraction successfully completed[/]")


if __name__ == "__main__":
    app()
