import requests
import logging
import base64
import hmac
import hashlib
import time
from typing import List, Dict, Any
from urllib.parse import urlencode
import os
from datetime import datetime
from connectors.base import ChannelConnector

logger = logging.getLogger(__name__)

class ShipStationClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://ssapi.shipstation.com"
    
    def _generate_auth_token(self) -> str:
        """Generate authentication token for ShipStation API."""
        timestamp = str(int(time.time()))
        data = f"{self.api_key}{self.api_secret}{timestamp}"
        signature = hmac.new(
            self.api_secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return base64.b64encode(
            f"{self.api_key}:{signature}:{timestamp}".encode()
        ).decode()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make HTTP request to ShipStation API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Basic {self._generate_auth_token()}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                if params:
                    url += '?' + urlencode(params)
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ShipStation API request failed: {str(e)}")
            raise
    
    def get_orders(self, 
                  start_date: str = None,
                  end_date: str = None,
                  status: str = None,
                  page: int = 1,
                  page_size: int = 100) -> List[Dict[str, Any]]:
        """Fetch orders from ShipStation."""
        params = {
            'page': page,
            'pageSize': page_size
        }
        
        if start_date:
            params['orderDateStart'] = start_date
        if end_date:
            params['orderDateEnd'] = end_date
        if status:
            params['orderStatus'] = status
        
        try:
            response = self._make_request('GET', '/orders', params=params)
            return response.get('orders', [])
            
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise
    
    def get_shipments(self,
                     start_date: str = None,
                     end_date: str = None,
                     page: int = 1,
                     page_size: int = 100) -> List[Dict[str, Any]]:
        """Fetch shipments from ShipStation."""
        params = {
            'page': page,
            'pageSize': page_size
        }
        
        if start_date:
            params['shipDateStart'] = start_date
        if end_date:
            params['shipDateEnd'] = end_date
        
        try:
            response = self._make_request('GET', '/shipments', params=params)
            return response.get('shipments', [])
            
        except Exception as e:
            logger.error(f"Error fetching shipments: {str(e)}")
            raise
    
    def get_warehouses(self) -> List[Dict[str, Any]]:
        """Fetch warehouses from ShipStation."""
        try:
            response = self._make_request('GET', '/warehouses')
            return response.get('warehouses', [])
            
        except Exception as e:
            logger.error(f"Error fetching warehouses: {str(e)}")
            raise
    
    def get_carriers(self) -> List[Dict[str, Any]]:
        """Fetch carriers from ShipStation."""
        try:
            response = self._make_request('GET', '/carriers')
            return response.get('carriers', [])
            
        except Exception as e:
            logger.error(f"Error fetching carriers: {str(e)}")
            raise

class ShipStationConnector(ChannelConnector):
    def __init__(self):
        self.key = os.getenv("SS_KEY")
        self.secret = os.getenv("SS_SECRET")
        self.base = "https://ssapi.shipstation.com"
        self.log = logging.getLogger("shipstation")

    def _get(self, path, params=None):
        r = requests.get(self.base + path, auth=(self.key, self.secret), params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def fetch_orders(self, since: datetime) -> list[dict]:
        # ShipStation expects ISO8601 string
        since_str = since.isoformat()
        resp = self._get("/orders", {"createDateStart": since_str})
        return resp.get("orders", [])

    def identifier(self) -> str:
        return "shipstation"
