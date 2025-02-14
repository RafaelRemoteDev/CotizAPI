import unittest
import yfinance as yf
from typing import Optional


class TestWheatPriceRetrieval(unittest.TestCase):
    """
    Test case to verify if the wheat futures price (ZW=F) is successfully retrieved from Yahoo Finance.
    """

    def test_wheat_price_retrieval(self) -> None:
        """
        Ensures that historical price data is available for wheat futures (ZW=F).
        """
        wheat = yf.Ticker("ZW=F")
        data = wheat.history(period="1d")

        # Verify that data is returned
        self.assertFalse(data.empty, "No price data retrieved for wheat futures (ZW=F)")

        # Ensure the closing price is available
        closing_price: Optional[float] = data["Close"].iloc[-1] if not data.empty else None
        self.assertIsNotNone(closing_price, "Closing price data is missing for wheat futures")
        self.assertGreater(closing_price, 0, "Closing price must be greater than 0")


if __name__ == "__main__":
    unittest.main()

