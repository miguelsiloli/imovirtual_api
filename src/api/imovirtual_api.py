import urllib.parse
import requests
import logging
from bs4 import BeautifulSoup
import json
from imovirtual_exceptions import *
import time
import pandas as pd
from typing import List, Optional, Union, Dict, Any
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
    }

HEADERS_IMV={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "multipart/mixed, application/graphql-response+json, application/graphql+json, application/json",
    "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "baggage": "sentry-environment=imovirtualpt2-prd,sentry-release=frontend-platform%40v20240603T121501-imovirtualpt2,sentry-public_key=feffe528c390ea66992a4a05131c3c68,sentry-trace_id=cc8c6f78b99b4e959c670ca3a2b379bd,sentry-transaction=%2Fpt%2Fresultados%2F%5B%5B...searchingCriteria%5D%5D,sentry-sampled=false",
    "Origin": "https://www.imovirtual.com",
    "Alt-Used": "www.imovirtual.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=1",
    "TE": "trailers"
}


class ImovirtualAPI:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
        }
    
    def __init__(self) -> None:
        """
        Initializes the ImovirtualAPI with the base URL and default parameters.
        """
        super().__init__()
        self.session = requests.Session()
        self.session.headers = HEADERS_IMV
        self.buildId = self.__get_buildId(HEADERS)
        self.base_url = f"https://www.imovirtual.com/_next/data/{self.buildId}/pt/resultados/"

    def __get_buildId(self, headers):
        url = "https://www.imovirtual.com/pt"

        # Fetch the HTML content
        response = self.session.get(url, headers=headers)     

        html_content = response.text           

        try:
            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            if script_tag is None:
                raise BuildIdNotFoundException("Script tag with id '__NEXT_DATA__' not found")

            json_content = script_tag.string
            data = json.loads(json_content)

            if 'buildId' not in data:
                raise BuildIdNotFoundException()

            build_id = data['buildId']
            return build_id

        except requests.RequestException as e:
            raise BuildIdNotFoundException(f"Request failed: {e}")
        
        except json.JSONDecodeError as e:
            raise BuildIdNotFoundException(f"Failed to parse JSON: {e}")

    def __construct_url(self, transaction_type: str, property_type: str, location: Union[str, List[str]], 
                        distance_radius: Optional[int] = None, limit: Optional[int] = 36, 
                        price_min: Optional[int] = None, price_max: Optional[int] = None, 
                        area_min: Optional[int] = None, area_max: Optional[int] = None, 
                        rooms_number: Optional[List[str]] = None, sort_by: Optional[str] = "DEFAULT", 
                        sort_direction: Optional[str] = "DESC", view_type: Optional[str] = "listing", 
                        owner_type: Optional[str] = "ALL") -> str:
        """
        Constructs the URL for querying the Imovirtual API with the given parameters.

        Parameters:
            transaction_type (str): Type of transaction (e.g., 'arrendar' or 'comprar').
            property_type (str): Type of property (e.g., 'apartamento', 'estudio').
            location (Union[str, List[str]]): Location(s) for the query.
            distance_radius (Optional[int]): Radius for distance-based searches.
            limit (Optional[int]): Limit for the number of results.
            price_min (Optional[int]): Minimum price filter.
            price_max (Optional[int]): Maximum price filter.
            area_min (Optional[int]): Minimum area filter.
            area_max (Optional[int]): Maximum area filter.
            rooms_number (Optional[List[str]]): List of number of rooms.
            sort_by (Optional[str]): Sort criteria.
            sort_direction (Optional[str]): Sort direction (ASC or DESC).
            view_type (Optional[str]): View type of the results.
            owner_type (Optional[str]): Type of owner.

        Returns:
            str: Constructed URL.
        """
        if isinstance(location, list) and len(location) > 1:
            multiple_locations = location
            location = "muitas-localizacoes"
        else:
            multiple_locations = None
        
        url = f"{self.base_url}{transaction_type}/{property_type}/{location}.json"
        params = []

        if distance_radius is not None:
            params.append(f"distanceRadius={distance_radius}")
        if limit is not None:
            params.append(f"limit={limit}")
        if price_min is not None:
            params.append(f"priceMin={price_min}")
        if price_max is not None:
            params.append(f"priceMax={price_max}")
        if area_min is not None:
            params.append(f"areaMin={area_min}")
        if area_max is not None:
            params.append(f"areaMax={area_max}")
        if rooms_number:
            encoded_rooms_number = urllib.parse.quote(f"[{','.join(rooms_number)}]")
            params.append(f"roomsNumber={encoded_rooms_number}")
        if sort_by is not None:
            params.append(f"by={sort_by}")
        if sort_direction is not None:
            params.append(f"direction={sort_direction}")
        if view_type is not None:
            params.append(f"viewType={view_type}")
        if owner_type is not None:
            params.append(f"ownerTypeSingleSelect={owner_type}")
        
        searching_criteria = [transaction_type, property_type] + (multiple_locations if multiple_locations else [location])
        for criteria in searching_criteria:
            params.append(f"searchingCriteria={urllib.parse.quote(criteria)}")

        query_string = "&".join(params)
        full_url = f"{url}?{query_string}"

        return full_url

    def query_imovirtual(self, transaction_type: str, property_type: str = "apartamento", location: str = "todo-o-pais", 
                         distance_radius: Optional[int] = None, limit: Optional[int] = 36, price_min: Optional[int] = None, 
                         price_max: Optional[int] = None, area_min: Optional[int] = None, area_max: Optional[int] = None, 
                         rooms_number: Optional[List[str]] = None, sort_by: Optional[str] = "DEFAULT", 
                         sort_direction: Optional[str] = "DESC", view_type: Optional[str] = "listing", 
                         owner_type: Optional[str] = "ALL", json: bool = False) -> Union[Dict[str, Any], pd.DataFrame]:
        """
        Queries the Imovirtual API with the specified parameters and returns the data.

        Parameters:
            transaction_type (str): Type of transaction (e.g., 'arrendar' or 'comprar').
            property_type (str): Type of property (e.g., 'apartamento', 'estudio').
            location (str): Location for the query.
            distance_radius (Optional[int]): Radius for distance-based searches.
            limit (Optional[int]): Limit for the number of results.
            price_min (Optional[int]): Minimum price filter.
            price_max (Optional[int]): Maximum price filter.
            area_min (Optional[int]): Minimum area filter.
            area_max (Optional[int]): Maximum area filter.
            rooms_number (Optional[List[str]]): List of number of rooms.
            sort_by (Optional[str]): Sort criteria.
            sort_direction (Optional[str]): Sort direction (ASC or DESC).
            view_type (Optional[str]): View type of the results.
            owner_type (Optional[str]): Type of owner.
            json (bool): Whether to return the data in JSON format.

        Returns:
            Union[Dict[str, Any], pd.DataFrame]: The queried data, either in JSON format or as a DataFrame.
        """
        logger.info("Querying Imovirtual")

        full_url = self.__construct_url(transaction_type, property_type, location, distance_radius, limit, price_min, price_max, area_min, area_max, rooms_number, sort_by, sort_direction, view_type, owner_type)
        logger.debug(f"Full URL with parameters: {full_url}")

        response = self.session.get(full_url)
        response.raise_for_status()

        data = response.json()
        all_data = data["pageProps"]['data']['searchAds']['items']
        num_pages = data["pageProps"]['tracking']['listing']['page_count']
        logger.info(f"Found {num_pages} pages")

        for page in tqdm(range(2, num_pages + 1)):
            logger.info(f"Going to the next pages... {page}/{num_pages}")
            paged_url = f"{full_url}&page={page}"
            paged_response = self.session.get(paged_url)
            paged_response.raise_for_status()
            paged_data = paged_response.json()
            all_data.extend(paged_data["pageProps"]['data']['searchAds']['items'])
            time.sleep(5)

        if json:
            return all_data
        else:
            return self.__flatten_json(all_data)
    
    def __flatten_json(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts a list of JSON data into a flattened DataFrame.

        Parameters:
            data (List[Dict[str, Any]]): The data to flatten.

        Returns:
            pd.DataFrame: The flattened DataFrame.
        """
        logger.info("Converting JSON to DataFrame")
        all_data = []
        for item in data:
            flat_item = pd.json_normalize(item, sep='_')
            all_data.append(flat_item)
        return pd.concat(all_data, axis=0, ignore_index=True)

    
# https://www.imovirtual.com/_next/data/3SK-RzE2TAgnlsoKK1twB/pt/resultados/comprar/apartamento/muitas-localizacoes.json?limit=36&by=DEFAULT&direction=DESC&viewType=listing&searchingCriteria=comprar&searchingCriteria=apartamento&searchingCriteria=porto&searchingCriteria=porto%2Fporto&ownerTypeSingleSelect=ALL&priceMin=100&priceMax=1000000&areaMin=20&areaMax=2000&roomsNumber=ONE&roomsNumber=TWO&roomsNumber=THREE&roomsNumber=FOUR&roomsNumber=FIVE
# https://www.imovirtual.com/_next/data/3SK-RzE2TAgnlsoKK1twB/pt/resultados/arrendar/apartamento/porto/porto.json?distanceRadius=0&limit=36&priceMin=20&priceMax=1000&areaMin=20&areaMax=200&roomsNumber=%5BONE%2CTWO%2CTHREE%2CFOUR%2CFIVE%5D&by=DEFAULT&direction=DESC&viewType=listing&searchingCriteria=arrendar&searchingCriteria=apartamento&searchingCriteria=porto&searchingCriteria=porto
# https://www.imovirtual.com/_next/data/3SK-RzE2TAgnlsoKK1twB/pt/resultados/comprar/apartamento/todo-o-pais.json?ownerTypeSingleSelect=ALL&by=DEFAULT&direction=DESC&viewType=listing&searchingCriteria=comprar&searchingCriteria=apartamento&searchingCriteria=todo-o-pais
# https://www.imovirtual.com/_next/data/3SK-RzE2TAgnlsoKK1twB/pt/resultados/comprar/apartamento/beja.json?ownerTypeSingleSelect=ALL&distanceRadius=0&roomsNumber=%5BONE%2CTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&priceMin=100&priceMax=1000000&areaMin=20&areaMax=2000&by=DEFAULT&direction=DESC&viewType=listing&searchingCriteria=comprar&searchingCriteria=apartamento&searchingCriteria=beja
# https://www.imovirtual.com/_next/data/3SK-RzE2TAgnlsoKK1twB/pt/resultados/comprar/apartamento/muitas-localizacoes.json?limit=36&priceMin=100&priceMax=1000000&areaMin=20&areaMax=2000&roomsNumber=%5BONE%2CTWO%2CTHREE%2CFOUR%2CFIVE%5D&by=DEFAULT&direction=DESC&viewType=listing&ownerTypeSingleSelect=ALL&searchingCriteria=comprar&searchingCriteria=apartamento&searchingCriteria=porto


if __name__ == "__main__":
    imv = ImovirtualAPI()
    # Example usage
    try:
        data = imv.query_imovirtual(
            transaction_type="comprar",
            location="porto",  # Multiple locations
            price_min=100,
            price_max=100000,
            area_min=100,
            area_max=200,
            rooms_number=["ONE", "TWO", "THREE"]
        )
        data.to_csv("data.csv")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
