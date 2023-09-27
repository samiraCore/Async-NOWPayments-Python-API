"""
A Python wrapper for the NOWPayments API ASYNC.
"""
import json
from typing import Any, Dict, Union
from re import match
import aiohttp

class NOWPayments:
    """
    Class to used for the NOWPayments API.
    """

    debug_mode = False

    key_regex = r"([A-z0-9]{7}-[A-z0-9]{7}-[A-z0-9]{7}-[A-z0-9]{7})"

    # Base URL
    NORMAL_URL = "https://api.nowpayments.io/v1/{}"
    SANDBOX_URL = "https://api-sandbox.nowpayments.io/v1/{}"

    api_url = ""

    endpoints = {
        "STATUS": "status",
        "CURRENCIES": "currencies",
        "MERCHANT_COINS": "merchant/coins",
        "ESTIMATE": "estimate?amount={}&currency_from={}&currency_to={}",
        "PAYMENT": "payment",
        "PAYMENT_STATUS": "payment/{}",
        "MIN_AMOUNT": "min-amount?currency_from={}&currency_to={}",
    }

    def __init__(self, key: str, sandbox: bool = False, debug_mode=False) -> None:
        """
        Class construct. Receives your api key as initial parameter.

        :param str key: API key
        :param bool sandbox: if True, sets api_url to the sandbox url (need sandbox api key)
        :param bool debug_mode: returns the url, instead of doing any requests when successful
        """
        self.debug_mode = debug_mode

        try:
            match(self.key_regex, key).group(0) == key
        except Exception as e:
            raise ValueError("Incorrect API Key format") from e

        self.key = key
        self.headers = {"x-api-key": key,
                        "User-Agent": "nowpay.py",
                        }

        if sandbox:
            self.api_url = self.SANDBOX_URL
        else:
            self.api_url = self.NORMAL_URL

    def create_url(self, endpoint: str) -> str:
        """
        Set the url to be used

        :param str endpoint: Endpoint to be used
        """
        return self.api_url.format(endpoint)

    async def get(self, endpoint: str, *args):
        """
        Make get requests with your header

        :param str url: URL to which the request is made
        """
        assert endpoint in self.endpoints
        url = self.create_url(self.endpoints[endpoint])
        if len(args) >= 1:
            url = url.format(*args)
        if self.debug_mode:
            return url
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url, headers=self.headers)
            print(await resp.text())
            if resp.status == 200:
                resp = await resp.text()
                return json.loads(resp)

    async def post(self, endpoint: str, data: Dict):
        """
        Make post requests with your header and data

        :param url: URL to which the request is made
        :param data: Data to which the request is made
        """
        assert endpoint in self.endpoints
        url = self.create_url(self.endpoints[endpoint])
        if self.debug_mode:
            return url
        async with aiohttp.ClientSession() as session:
            async with session.post(url,
                                    headers=self.headers,
                                    data=data,
                                    ) as resp:
                resp = await resp.text()
                return json.loads(resp)

    async def status(self) -> Dict:
        """
        This is a method to get information about the current state of the API. If everything
        is OK, you will receive an "OK" message. Otherwise, you'll see some error.
        """
        return await self.get("STATUS")

    async def currencies(self) -> Dict:
        """
        This is a method for obtaining information about all cryptocurrencies available for
        payments.
        """
        return await self.get("CURRENCIES")

    async def merchant_coins(self) -> Dict:
        """
        This is a method for obtaining information about the cryptocurrencies available
        for payments. Shows the coins you set as available for payments in the "coins settings"
        tab on your personal account.
        """
        return await self.get("MERCHANT_COINS")

    async def estimate(
        self, amount: float or int, currency_from: str, currency_to: str
    ) -> Dict:
        """This is a method for calculating the approximate price in cryptocurrency
        for a given value in Fiat currency. You will need to provide the initial cost
        in the Fiat currency (amount, currency_from) and the necessary cryptocurrency
        (currency_to) Currently following fiat currencies are available: usd, eur, nzd,
        brl, gbp.

         :param  float amount: Cost value.
         :param  str currency_from: Fiat currencies.
         :param  str currency_to: Cryptocurrency.
        """
        return await self.get("ESTIMATE", amount, currency_from, currency_to)

    async def create_payment(
        self,
        price_amount: float or int,
        price_currency: str,
        pay_currency: str,
        **kwargs: Union[str, float, bool, int],
    ) -> Dict:
        """
        With this method, your customer will be able to complete the payment without leaving
        your website.

        :param float price_amount: The fiat equivalent of the price to be paid in crypto.
        :param str price_currency: The fiat currency in which the price_amount is specified.
        :param str pay_currency: The crypto currency in which the pay_amount is specified.
        :param float pay_amount: The amount that users have to pay for the order stated in crypto.
        :param str ipn_callback_url: Url to receive callbacks, should contain "http" or "https".
        :param str order_id: Inner store order ID.
        :param str order_description: Inner store order description.
        :param int purchase_id: Id of purchase for which you want to create a other payment.
        :param str payout_address: Receive funds on another address.
        :param str payout_currency: Currency of your external payout_address.
        :param int payout_extra_id: Extra id or memo or tag for external payout_address.
        :param bool fixed_rate: Required for fixed-rate exchanges.
        :param str case: This only affects sandbox, which status the payment is desired
        """

        data = {
            "price_amount": price_amount,
            "price_currency": price_currency,
            "pay_currency": pay_currency,
        }
        data.update(**kwargs)
        # if len(data) != 13:
        #     raise TypeError("create_payment() got an unexpected keyword argument")

        return await self.post("PAYMENT", data)

    async def payment_status(self, payment_id: int) -> Any:
        """
        Get the actual information about the payment.

        :param int payment_id: ID of the payment in the request.
        """
        return await self.get("PAYMENT_STATUS", payment_id)

    async def min_amount(self, currency_from: str, currency_to: str) -> Any:
        """
        Get the minimum payment amount for a specific pair.

        :param currency_from: Currency from
        :param currency_to: Currency to
        """
        return await self.get("MIN_AMOUNT", currency_from, currency_to)

