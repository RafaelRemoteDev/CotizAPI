import unittest
import requests


class TestAssetPrice(unittest.TestCase):
    API_URL = "http://127.0.0.1:8032/assets"  # Endpoint para consultar precios

    def test_bitcoin_price(self):
        """Verifica que se devuelva un precio para Bitcoin"""
        response = requests.get(self.API_URL)

        # Comprobar que la respuesta tiene un código 200
        self.assertEqual(response.status_code, 200, "La consulta de precio falló")

        # Verificar que se devuelven datos y buscar Bitcoin
        data = response.json()
        self.assertIn("assets", data, "La clave 'assets' no se encontró en la respuesta")

        # Buscar Bitcoin (BTC-USD) en la lista de activos
        bitcoin = next((asset for asset in data["assets"] if asset["symbol"] == "BTC-USD"), None)
        self.assertIsNotNone(bitcoin, "No se encontró Bitcoin (BTC-USD) en la respuesta")

        # Verificar que el precio de Bitcoin es válido
        self.assertIn("price", bitcoin, "No se encontró el precio para Bitcoin (BTC-USD)")
        self.assertGreater(bitcoin["price"], 0, "El precio de Bitcoin debe ser mayor a 0")


if __name__ == "__main__":
    unittest.main()
