from datetime import datetime
from math import log, sqrt, exp
from scipy.stats import norm


"""

TODO:

    Implement the below methods `get_price` & `get_delta`.

    

    They should calculate and return the Black76 option price (as given by equations [1] & [2]) and delta 

    (as given by equations [5] & [10]) in

     https://www.glynholton.com/notes/black_1976/

    Further info at https://en.wikipedia.org/wiki/Black_model

    (NB - pay close attention to the sign of call and put deltas)



    Feel free to use scipy.stats.norm (already imported) in order to calc CDF where appropriate.

    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html

    

    Other than scipy.stats.norm, you may only use modules available in the Python Standard Library for version 3.7.

    

    You may edit the __init__ & _calc_maturity methods if needed.

"""


class EuropeanOptionOnFuture:
    """

    A class used to represent a European Option on a Futures contract and to calculate price and risk measures,

    as given by the Black76 model



    Methods

    _______

    get_price(futures_price: float, current_time: datetime) -> float

        Returns the discounted option price

    get_delta(futures_price: float, current_time: datetime) -> float

        Returns the discounted option delta

    """

    def __init__(
        self,
        strike_price: float,
        expiry_date: datetime,
        vol: float,
        discount_rate: float,
        option_type: str,
    ):
        """

        :param strike_price: the strike price of the option (x)

        :param expiry_date: the expiration date of the option

        :param vol: the implied volatility with which the option is to be priced (sigma)

        :param discount_rate: the interest rate

        :param option_type: either 'c' or 'p' to represent whether the option is a call or put

        """

        self._strike_price = strike_price

        self._expiry_date = expiry_date

        self._vol = vol

        self._discount_rate = discount_rate

        if option_type not in ('c','p'):
            raise ValueError("Option type must be 'c' or 'p'")

        self._option_type = option_type

    def get_price(self, futures_price: float, current_time: datetime) -> float:
        """

        Returns the discounted Black76 option price



        :param futures_price: reference price for the option's underlying futures contract

        :param current_time: the time at which to calculate the option's price

        :return: the option price at the input futures price & time

        """

        # Calculate d1 and d2
        time_to_maturity = self._calc_maturity(current_time)
        d1 = self._calc_d1(futures_price, time_to_maturity)
        d2 = d1 - self._vol * sqrt(time_to_maturity)

        # Price the option based on its type (call or put)
        if self._option_type == "c":
            option_price = exp(-self._discount_rate * time_to_maturity) * (
                futures_price * norm.cdf(d1) - self._strike_price * norm.cdf(d2)
            )
        elif self._option_type == "p":
            option_price = exp(-self._discount_rate * time_to_maturity) * (
                self._strike_price * norm.cdf(-d2) - futures_price * norm.cdf(-d1)
            )
        else:
            raise ValueError("Option type must be 'c' or 'p'")

        return option_price

    def get_delta(self, futures_price: float, current_time: datetime) -> float:
        """

        Returns the discounted Black76 analytic option delta



        :param futures_price: reference price for the option's underlying futures contract

        :param current_time: the time at which to calculate the option's delta

        :return: the option delta at the input futures price & time

        """

        time_to_maturity = self._calc_maturity(current_time)
        d1 = self._calc_d1(futures_price, time_to_maturity)

        # Calculate delta based on option type
        if self._option_type == "c":
            delta = exp(-self._discount_rate * time_to_maturity) * norm.cdf(d1)
        elif self._option_type == "p":
            delta = exp(-self._discount_rate * time_to_maturity) * (norm.cdf(d1) - 1)
        else:
            raise ValueError("Option type must be 'c' or 'p'")

        return delta

    def _calc_maturity(self, current_time: datetime) -> float:
        """Returns the time to maturity (in years) of the option, using a calendar days / 365 model



        :param current_time: the time at which to calculate the option's maturity

        :return: the time remaining until the expiration of the option

        """

        return (self._expiry_date - current_time).days / 365

    def _calc_d1(self, futures_price: float, time_to_maturity: float) -> float:
        """

        Returns the discounted Black76 analytic option d1 value



        :param futures_price: reference price for the option's underlying futures contract

        :param time_to_maturity: the time to maturity/expiry of the option in years

        :return: the option d1 value at the input futures price & time

        """

        # Calculate d1
        d1 = (
            log(futures_price / self._strike_price)
            + 0.5 * self._vol**2 * time_to_maturity
        ) / (self._vol * sqrt(time_to_maturity))

        return d1


if __name__ == "__main__":

    # Simple test case.

    # Feel free to add a few more.

    x = 100  # Strike price

    sig = 0.5  # Volatility

    expiry = datetime(2022, 11, 1, 12, 0, 0)  # Expiration date

    r = 0.01  # Discount rate

    opt_type = "c"  # Option type

    opt = EuropeanOptionOnFuture(x, expiry, sig, r, opt_type)

    f = 100  # Test case underlying price

    curr_time = datetime(2021, 11, 1, 12, 0, 0)  # Test case current time

    price = opt.get_price(f, curr_time)

    delta = opt.get_delta(f, curr_time)

    # Check price & delta

    print(f"Test price = {price}")

    assert abs(price - 19.544836) <= 0.0001

    print(f"Test delta = {delta}")

    assert abs(delta - 0.59273) <= 0.0001

    # Call/put delta simple check

    assert EuropeanOptionOnFuture(x, expiry, sig, r, "c").get_delta(f, curr_time) > 0

    assert EuropeanOptionOnFuture(x, expiry, sig, r, "p").get_delta(f, curr_time) < 0
