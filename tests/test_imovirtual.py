import unittest
from unittest.mock import patch
import requests_mock
import pandas as pd
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))

print(sys.path)
from src.api.imovirtual_api import ImovirtualAPI 




# set PYTHONPATH=%cd%\src
# python -m unittest discover tests

class TestImovirtualAPI(unittest.TestCase):

    @patch('imovirtual_api.logger')
    def setUp(self, mock_logger):
        self.api = ImovirtualAPI()

    @requests_mock.Mocker()
    def test_query_imovirtual_single_page(self, m):
        mock_response = {
            "pageProps": {
                "data": {
                    "searchAds": {
                        "items": [
                            {"id": 1, "name": "Test Property 1"},
                            {"id": 2, "name": "Test Property 2"}
                        ]
                    }
                },
                "tracking": {
                    "listing": {
                        "page_count": 1
                    }
                }
            }
        }
        
        url = self.api._ImovirtualAPI__construct_url('comprar', 'apartamento', 'lisboa')
        m.get(url, json=mock_response)

        result = self.api.query_imovirtual(transaction_type='comprar', location='lisboa')
        
        expected_result = pd.DataFrame([
            {"id": 1, "name": "Test Property 1"},
            {"id": 2, "name": "Test Property 2"}
        ])

        pd.testing.assert_frame_equal(result, expected_result)

    @requests_mock.Mocker()
    def test_query_imovirtual_multiple_pages(self, m):
        mock_response_page_1 = {
            "pageProps": {
                "data": {
                    "searchAds": {
                        "items": [
                            {"id": 1, "name": "Test Property 1"},
                            {"id": 2, "name": "Test Property 2"}
                        ]
                    }
                },
                "tracking": {
                    "listing": {
                        "page_count": 2
                    }
                }
            }
        }
        mock_response_page_2 = {
            "pageProps": {
                "data": {
                    "searchAds": {
                        "items": [
                            {"id": 3, "name": "Test Property 3"},
                            {"id": 4, "name": "Test Property 4"}
                        ]
                    }
                }
            }
        }

        url_page_1 = self.api._ImovirtualAPI__construct_url('comprar', 'apartamento', 'lisboa')
        url_page_2 = f"{url_page_1}&page=2"
        
        m.get(url_page_1, json=mock_response_page_1)
        m.get(url_page_2, json=mock_response_page_2)

        result = self.api.query_imovirtual(transaction_type='comprar', location='lisboa')

        expected_result = pd.DataFrame([
            {"id": 1, "name": "Test Property 1"},
            {"id": 2, "name": "Test Property 2"},
            {"id": 3, "name": "Test Property 3"},
            {"id": 4, "name": "Test Property 4"}
        ])

        pd.testing.assert_frame_equal(result, expected_result)

    @requests_mock.Mocker()
    def test_query_imovirtual_json_response(self, m):
        mock_response = {
            "pageProps": {
                "data": {
                    "searchAds": {
                        "items": [
                            {"id": 1, "name": "Test Property 1"},
                            {"id": 2, "name": "Test Property 2"}
                        ]
                    }
                },
                "tracking": {
                    "listing": {
                        "page_count": 1
                    }
                }
            }
        }

        url = self.api._ImovirtualAPI__construct_url('comprar', 'apartamento', 'lisboa')
        m.get(url, json=mock_response)

        result = self.api.query_imovirtual(transaction_type='comprar', location='lisboa', json=True)
        
        expected_result = [
            {"id": 1, "name": "Test Property 1"},
            {"id": 2, "name": "Test Property 2"}
        ]

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
