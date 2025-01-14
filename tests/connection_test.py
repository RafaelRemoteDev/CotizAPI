import unittest
import requests

class TestAPIConnection(unittest.TestCase):
    API_URL = "http://127.0.0.1:8032/docs"  # Reemplaza con la URL de tu API

    def test_connection(self):
        """Verifica que la API responde con un código 200"""
        response = requests.get(self.API_URL)
        self.assertEqual(response.status_code, 200, "La API no está respondiendo correctamente")

if __name__ == "__main__":
    unittest.main()
