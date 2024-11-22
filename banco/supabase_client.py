import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class SupabaseResponse:
    data: List[Dict]
    
    @classmethod
    def from_response(cls, response_data):
        if isinstance(response_data, list):
            return cls(data=response_data)
        elif isinstance(response_data, dict):
            return cls(data=[response_data])
        return cls(data=[])

class Table:
    def __init__(self, client, table_name: str):
        self.client = client
        self.table_name = table_name
        self._select_query = "*"
        self._filters = {}
        self._limit = None
        self._order = None
        self._ascending = True

    def select(self, columns: str) -> 'Table':
        self._select_query = columns
        return self

    def eq(self, column: str, value: Any) -> 'Table':
        self._filters[column] = f"eq.{value}"
        return self

    def gt(self, column: str, value: Any) -> 'Table':
        self._filters[column] = f"gt.{value}"
        return self

    def limit(self, num: int) -> 'Table':
        self._limit = num
        return self

    def order(self, column: str, desc: bool = False) -> 'Table':
        self._order = column
        self._ascending = not desc
        return self

    def insert(self, data: Dict) -> 'Table':
        self._operation = 'insert'
        self._data = data
        return self

    def update(self, data: Dict) -> 'Table':
        self._operation = 'update'
        self._data = data
        return self

    def delete(self) -> 'Table':
        self._operation = 'delete'
        return self

    def execute(self) -> SupabaseResponse:
        params = {}
        if self._select_query:
            params["select"] = self._select_query
        if self._filters:
            for k, v in self._filters.items():
                params[k] = v
        if self._limit:
            params["limit"] = self._limit
        if self._order:
            direction = "desc" if not self._ascending else "asc"
            params["order"] = f"{self._order}.{direction}"

        try:
            if hasattr(self, '_operation'):
                if self._operation == 'insert':
                    response = self.client._post(f"/{self.table_name}", self._data)
                elif self._operation == 'update':
                    query_string = "&".join(f"{k}={v}" for k, v in self._filters.items())
                    response = self.client._patch(f"/{self.table_name}?{query_string}", self._data)
                elif self._operation == 'delete':
                    query_string = "&".join(f"{k}={v}" for k, v in self._filters.items())
                    response = self.client._delete(f"/{self.table_name}?{query_string}")
            else:
                query_parts = []
                for k, v in params.items():
                    if k == "select":
                        query_parts.append(f"select={v}")
                    elif k == "order":
                        query_parts.append(f"order={v}")
                    elif k == "limit":
                        query_parts.append(f"limit={v}")
                    else:
                        query_parts.append(f"{k}={v}")
                
                query_string = "&".join(query_parts)
                response = self.client._get(f"/{self.table_name}?{query_string}")

            return SupabaseResponse.from_response(response)
        except Exception as e:
            print(f"Erro na execução: {str(e)}")
            return SupabaseResponse(data=[])

class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def table(self, name: str) -> Table:
        return Table(self, name)

    def _get(self, endpoint: str) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1{endpoint}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro na requisição GET: {str(e)}")
            return []

    def _post(self, endpoint: str, data: Dict) -> List[Dict]:
        try:
            response = requests.post(
                f"{self.url}/rest/v1{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro na requisição POST: {str(e)}")
            return []

    def _patch(self, endpoint: str, data: Dict) -> List[Dict]:
        try:
            response = requests.patch(
                f"{self.url}/rest/v1{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro na requisição PATCH: {str(e)}")
            return []

    def _delete(self, endpoint: str) -> List[Dict]:
        try:
            response = requests.delete(
                f"{self.url}/rest/v1{endpoint}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro na requisição DELETE: {str(e)}")
            return []

    def rpc(self, function_name: str, params: Dict = None) -> Dict:
        try:
            response = requests.post(
                f"{self.url}/rest/v1/rpc/{function_name}",
                headers=self.headers,
                json=params or {}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro na chamada RPC: {str(e)}")
            return {}