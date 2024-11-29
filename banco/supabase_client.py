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

class StorageBucket:
    def __init__(self, client, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def upload(self, file_path: str, file_bytes: bytes) -> dict:
        try:
            response = requests.post(
                f"{self.client.url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers={
                    "Authorization": f"Bearer {self.client.key}",
                    "Content-Type": "application/octet-stream"
                },
                data=file_bytes
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro no upload do arquivo: {str(e)}")
            return {}

    def remove(self, file_paths: list) -> dict:
        try:
            file_path = file_paths[0] if isinstance(file_paths, list) else file_paths
            response = requests.delete(
                f"{self.client.url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers={
                    "Authorization": f"Bearer {self.client.key}"
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Erro ao remover arquivo(s): {str(e)}")
            return False

class Storage:
    def __init__(self, client):
        self.client = client

    def from_(self, bucket_name: str) -> StorageBucket:
        return StorageBucket(self.client, bucket_name)

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
        self._filters[column] = str(value)
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
        headers = {
            "apikey": self.client.key,
            "Authorization": f"Bearer {self.client.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        params = {}
        if self._select_query:
            params["select"] = self._select_query
        if self._filters:
            for k, v in self._filters.items():
                params[k] = f"eq.{v}"
        if self._limit:
            params["limit"] = self._limit
        if self._order:
            direction = "desc" if not self._ascending else "asc"
            params["order"] = f"{self._order}.{direction}"

        try:
            if hasattr(self, '_operation'):
                if self._operation == 'insert':
                    response = requests.post(
                        f"{self.client.url}/rest/v1/{self.table_name}",
                        headers=headers,
                        json=self._data
                    )
                elif self._operation == 'update':
                    filters = "&".join(f"{k}=eq.{v}" for k, v in self._filters.items())
                    response = requests.patch(
                        f"{self.client.url}/rest/v1/{self.table_name}?{filters}",
                        headers=headers,
                        json=self._data
                    )
                elif self._operation == 'delete':
                    filters = "&".join(f"{k}=eq.{v}" for k, v in self._filters.items())
                    response = requests.delete(
                        f"{self.client.url}/rest/v1/{self.table_name}?{filters}",
                        headers=headers
                    )
            else:
                query_parts = "&".join(f"{k}={v}" for k, v in params.items())
                response = requests.get(
                    f"{self.client.url}/rest/v1/{self.table_name}?{query_parts}",
                    headers=headers
                )

            response.raise_for_status()
            return SupabaseResponse.from_response(response.json())
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
        self.storage = Storage(self)

    def table(self, name: str) -> Table:
        return Table(self, name)

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