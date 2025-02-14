import unittest
import requests


class TestAssetPrice(unittest.TestCase):
    """
    Test case for verifying the asset price retrieval via API.
    """
    API_URL = "http://127.0.0.1:8032/assets"  # Endpoint to fetch asset prices

    def test_bitcoin_price(self) -> None:
        """
        Ensures that a valid price is returned for Bitcoin (BTC-USD).
        """
        response = requests.get(self.API_URL)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200, "Price request failed")

        # Verify that the response contains data and the 'assets' key
        data = response.json()
        self.assertIn("assets", data, "The 'assets' key was not found in the response")

        # Look for Bitcoin (BTC-USD) in the asset list
        bitcoin = next((asset for asset in data["assets"] if asset["symbol"] == "BTC-USD"), None)
        self.assertIsNotNone(bitcoin, "Bitcoin (BTC-USD) was not found in the response")

        # Ensure that Bitcoin's price is valid
        self.assertIn("price", bitcoin, "Bitcoin (BTC-USD) price key is missing")
        self.assertGreater(bitcoin["price"], 0, "Bitcoin's price must be greater than 0")


if __name__ == "__main__":
    unittest.main()

