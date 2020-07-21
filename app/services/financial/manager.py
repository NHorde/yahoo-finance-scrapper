from bs4 import BeautifulSoup
import requests
import re
from json import loads

from libs.state import State
from libs.logger import BASE_LOGGER

LOGGER = BASE_LOGGER.getChild(__name__)

def get_html(state: State):
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

    return crawler_quote_summary(state=state)


def crawler_quote_summary(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.quote_summary_store = state.url['QuoteSummaryStore']
        LOGGER.info(f"{state.ticker.symbol} | Successfully retrieving QuoteSummaryStore list")
    except ValueError:
        state.quote_summary_store = None
    return crawler_financial_data(state=state)


def crawler_financial_data(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.financial_data = state.quote_summary_store['financialData']
        LOGGER.info(f"{state.ticker.symbol} | Successfully retrieving financialData")
    except ValueError:
        state.financial_data = None
    return get_current_price(state=state)


def get_current_price(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.current_price = state.financial_data['currentPrice']['fmt']
        LOGGER.info(f"{state.ticker.symbol} | Current company price: {state.current_price}")
    except ValueError:
        state.current_price = None
    return crawler_default_key_statistics(state=state)


def crawler_default_key_statistics(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.default_key_statistics = state.quote_summary_store['defaultKeyStatistics']

    except ValueError:
        state.default_key_statistics = None
    return get_price_to_book(state=state)


def get_price_to_book(state: State):
    """
    :param state:
    :type state: State
    :rtype: dict
    :return: object
    """
    try:
        state.price_to_book = state.default_key_statistics['priceToBook']['fmt']
        LOGGER.info(f"{state.ticker.symbol} | Price to book: {state.price_to_book}")
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
    state.status = 100
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
        result = get_html(state)
    except:
        result = state
    return result
