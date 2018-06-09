import requests
from datetime import datetime

from pvpc.exceptions import DateError

AVAILABLE_RATES = [
    'GEN',
    'NOC',
    'VHC'
]

REE_URL = 'https://api.esios.ree.es/'


def get_day_prices(date, rate=None):
    """ Get PVPC prices for specific date.

    Args:
        date: Datetime obj of date to recover information for.
        rate:  Optional string. If None all available rates will be added to the
            answer. If one is selected just that will be return.

    Returns:
        Dict with process answer with prices for requests rates.
    """
    if rate is not None: check_requested_rate(rate)

    ans = requests.get(
        REE_URL + 'archives/70/download_json',
        params={
            'date': date.strftime('%Y-%m-%d')
        }
    )

    if ans.status_code == 200:
        return parse_answer_from_ree(ans.json(), rate)
    else:
        return False


def parse_answer_from_ree(answer, rate=None):
    """ Transform the answer from server in a short dict with price information.

    Args:
        answer: Dict from json's answer. Should contain information about
            the electricity price.
        rate: Optional string. If None all available rates will be added to the
            answer. If one is selected just that will be return.

    Returns:
        Dict with process answer with prices for requests rates.
    """

    def check_valid_answer(answer):
        """ Checks if the answer has valid information.

        Args:
            answer: Json parsed answer.

        Raises:
            DateError: If there is not valid information in the answer
                about prices.

        """
        try:
            answer['PVPC']
        except KeyError:
            raise DateError()

    def parsed_time_in_answer_from_ree(hour):
        """ Transform hour fields in answer to a int value.

        Args:
            hour: Dict with price information for one hour.

        Returns:
            Int value of the hour that the dict represents.

        """
        return int(hour['Hora'][:2])

    def price_from_ree_into_float(price_str):
        """ Transform the string prices into number prices for kW/h.

        Args:
            price_str: The price in string format that server returns.

        Returns:
            Float value for €kWh.

        """
        return float(price_str.replace(',','.')) / 1000

    check_valid_answer(answer)
    parsed_answer = {}

    for hour in answer['PVPC']:
        if rate is None:
            price = {
                a_rate: price_from_ree_into_float(hour[a_rate])
                for a_rate in AVAILABLE_RATES
            }
        else:
            price = price_from_ree_into_float(hour[rate])

        parsed_answer[parsed_time_in_answer_from_ree(hour)] = price

    return parsed_answer


def check_requested_rate(rate):
    """ Checks if the request rate is valid.

    Args:
        rate: string name of the rate.

    Raises:
        ValueError: If the name of the rate is not valid the exception is raise.

    """
    if rate not in AVAILABLE_RATES:
        raise ValueError(
            'The rate {} is not valid'.format(rate)
        )


def get_today_prices(rate=None):
    """ Get dict with the electricity prices for today.

    Returns:
        Dict with electricity prices for today.

    """
    return get_day_prices(
        datetime.today(),
        rate=rate
    )