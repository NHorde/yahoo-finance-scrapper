from bs4 import BeautifulSoup
import requests
import re
from json import loads

from libs.state import State
from libs.logger import BASE_LOGGER

LOGGER = BASE_LOGGER.getChild(__name__)

def request_html(state: State):
    """
    Scrap financial information for a given ticker by retrieving the URL. The HTML is a maze so the idea is to store all paths into many attributes within the
    state.ticker object and crawl from there

    :param state:
    :param: string
    :return:
    """
    soup = BeautifulSoup(requests.get(f"https://finance.yahoo.com/quote/{state.ticker.symbol}/key-statistics?p={state.ticker.symbol}").content, "lxml")
    script = soup.find("script", text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\s+=\s+(\{.*\})", script).group(1))
    state.url = data['context']['dispatcher']['stores']

    LOGGER.info(f"{state.ticker.symbol} | Successfully get URL")

    return parse_current_price(state=state)


def parse_current_price(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.ticker.current_price = state.url['QuoteSummaryStore']['financialData']['currentPrice']['fmt']
        LOGGER.info(f"{state.ticker.symbol} | Current company price: {state.ticker.current_price}")
    except ValueError:
        state.current_price = None
    return parse_price_to_book(state=state)


def parse_price_to_book(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.ticker.price_to_book = state.url['QuoteSummaryStore']["defaultKeyStatistics"]['priceToBook']['fmt']
        LOGGER.info(f"{state.ticker.symbol} | Price to book: {state.ticker.price_to_book}")
    except ValueError:
        state.price_to_book = None
    return status(state=state)


def status(state: State):
    """
    :param state: object
    :type state: class
    :rtype: dict
    :return: state
    """
    state.ticker.status = 100
    LOGGER.info(f"{state.ticker.symbol} | Scrapping status: {state.ticker.status}")
    return state


def manager(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.ticker.symbol = "AMZN"
        result = request_html(state)
    except:
        result = state
    # defaultKeyStatistics
    # financialsTemplate
    # price
    # financialData
    # quoteType
    # calendarEvents
    # summaryDetail
    # symbol
    # pageViews

    print(state.url["QuoteTimeSeriesStore"]["timeSeries"]["trailingPbRatio"][2]["reportedValue"]["fmt"])
    print(state.url["QuoteTimeSeriesStore"]["timeSeries"]["trailingPbRatio"][2]["asOfDate"])
    # ["trailingPbRatio"]
    # import json
    # print(json.dumps(state.url, indent=3))
    #
    # with open('data.txt', 'w') as outfile:
    #     json.dump(state.url, outfile, indent=3)
    return result

# QuoteTimeSeriesStore
# timeSeries
# quarterlyEnterprisesValueEBITDARatio
# trailingPbRatio
# 3
# reportedValue
# fmt