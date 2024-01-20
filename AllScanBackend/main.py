import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import concurrent.futures
import subprocess

import pandas as pd

app = FastAPI()


class Page:

    def __init__(self, link, mainPage=None, pageHTML=None):
        if self._isLink(link):
            self._LINK = link
            self._MAINPAGE = mainPage if mainPage else link
            self._response = requests.get(self._LINK) if (pageHTML is None) else None
            self._soup = BeautifulSoup(self._response.text, 'html.parser') if (pageHTML is None) else BeautifulSoup(
                pageHTML, 'html.parser')
            self._PROTOCOL = self._LINK.split(":")[0]
            self._Connections = []
            self._Domains = []
        else:
            print("link is not defined")

    def _isLink(self, link):
        if re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$').match(link):
            return True
        else:
            return False

    def _urlFormatter(self, url):
        url = str(url)
        if re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$').match(url):
            return url
        elif "www." in url:
            return self._PROTOCOL + "://www." + url.split("www.")[1]
        elif url.startswith("javascript:"):
            return None
        else:
            if url.startswith("/"):
                return self._MAINPAGE + url
            else:
                return self._MAINPAGE + "/" + url

    def _getDomainFromUrl(self, url):
        parsedUrl = urlparse(url)
        if parsedUrl.netloc:
            return parsedUrl.netloc
        else:
            return None

    def setConnections(self):

        for link in self._soup.find_all('a'):
            href = link.get('href')
            # url = self._urlFormatter(href)
            domain = self._getDomainFromUrl(self._urlFormatter(href))

            # if url is not None and url not in self._Connections:
            #    self._Connections.append(url)

            if domain is not None and domain not in self._Domains:
                self._Domains.append(domain)

    def getUrls(self):
        return self._Connections

    def getDomains(self):
        return self._Domains


class UrlScanner:
    def __init__(self, url):
        self.url = url
        self._kasperskyUrl = "https://opentip.kaspersky.com/api/v1/search/domain?request="

    def scanByKaspersky(self):
        headers = {
            "x-api-key": "", #TOKEN
        }
        res = requests.get(self._kasperskyUrl + self.url, headers=headers)

        if res.status_code == 200:
            data = json.loads(res.text)
            return ControlledData(url=data["DomainGeneralInfo"]["Domain"], zone=data["Zone"])


df = None
xls = None


try:
    xls = pd.ExcelFile('database.xlsx')
    df = pd.read_excel(xls, header=None)
except FileNotFoundError:
    df = pd.DataFrame()


def scan_url(url):
    sc = UrlScanner(url)
    return sc.scanByKaspersky()


async def mainRoutine(connections):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await asyncio.gather(*[loop.run_in_executor(pool, scan_url, task) for task in connections])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ControlledData(BaseModel):
    url: str
    zone: str


class User(BaseModel):
    userName: str
    password: str


class PageData(BaseModel):
    content: str
    url: str


class Url(BaseModel):
    url: str


def process_url(url):
    global df
    if url in df.values:
        index = df[df.eq(url).any(axis=1)].index[0]
        zone = df.iloc[index, 1]
        return ControlledData(url=url, zone=zone)
    else:
        scanned_url = UrlScanner(url).scanByKaspersky()
        new_data = pd.DataFrame([[scanned_url.url, scanned_url.zone]], columns=[0, 1])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel('database.xlsx', index=False, header=False)
        return scanned_url


async def process_request(url):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, process_url, url)
    return result


@app.post("/link-control")
async def read_root(url: Url):
    result = await process_request(url.url)
    return result


@app.post("/get-links")
async def getLink(page_data: PageData):
    page = Page(page_data.url, pageHTML=page_data.content)
    page.setConnections()
    return page.getDomains()


@app.get("/update-database")
async def updateDatabase(admin: User):
    if admin.password == 'admin' and admin.userName == 'admin':
        global df
        global xls
        for index, row in df.iterrows():
            selectedRow = row[0]
            processedData = UrlScanner(selectedRow).scanByKaspersky()
            df.at[index, 1] = processedData.zone
            df.to_excel('database.xlsx', index=False, header=False)

        try:

            xls.close()

            xls = pd.ExcelFile('database.xlsx')
            df = pd.read_excel(xls, header=None)
        except FileNotFoundError:
            df = pd.DataFrame()
        return "Database Updated"
    else:
        return "You dont have a permission for this operation"


@app.get("/drop-database")
async def dropDatabase(admin: User):
    if admin.password == 'admin' and admin.userName == 'admin':
        empty_dataframe = pd.DataFrame()
        empty_dataframe.to_excel("database.xlsx", index=False)

        try:
            global df
            global xls
            xls.close()

            xls = pd.ExcelFile('database.xlsx')
            df = pd.read_excel(xls, header=None)
        except FileNotFoundError:
            df = pd.DataFrame()

        return "Database Dropped"
    else:
        return "You dont have a permission for this operation"


if __name__ == '__main__':
    subprocess.run(["uvicorn", "main:app", "--reload"])
