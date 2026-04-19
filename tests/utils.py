
from typing import Literal
_REST = Literal['get', 'post']

def fast_test(router, status: list, method: str = 'post'):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if isinstance(result, tuple) and len(result) == 2:
                client, data = result
            else:
                client = result
                data = {}
            
            if method == 'post':
                response = await client.post(router, json=data)
            elif method == 'get':
                response = await client.get(router, params=data)
            elif method == 'delete':
                response = await client.delete(router)
            elif method == 'put':
                response = await client.put(router, json=data)
            else:
                response = await client.request(method, router, json=data)
            
            assert response.status_code in status
        return wrapper
    return decorator

async def loop_request(client, 
                       endpoint: str,
                       base_data: dict,
                       test_cases: dict,
                       parametr: str,  
                       method: str = 'POST',
                       check_dublicate: bool = True):
    """
    Автоматическая проверка серии запросов с разными значениями параметра.
    
    Parameters
    ----------
    method : str
        HTTP метод: 'POST', 'PATCH', 'PUT'.
    """
    responses = []
    for value, expected in test_cases.items():
        data = base_data.copy()
        data[parametr] = value
        
        if method == 'POST':
            response = await client.post(endpoint, json=data)
        elif method == 'PATCH':
            response = await client.patch(endpoint, json=data)
        elif method == 'PUT':
            response = await client.put(endpoint, json=data)
        elif method == 'DELETE':
            response = await client.delete(f"{endpoint}{value}")
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        assert response.status_code == expected, \
            f"{method} {parametr}='{value}': ожидался {expected}, получен {response.status_code}"
        responses.append(response)
        
        if check_dublicate and expected == 201 and method == 'POST':
            dup_response = await client.post(endpoint, json=data)
            assert dup_response.status_code in [409, 400], \
                f"Дубликат {value}: ожидался 409, получен {dup_response.status_code}"
            responses.append(dup_response)
    return responses

async def loop_request_get(client, 
                           endpoint: str,
                           base_params: dict,
                           test_cases: dict,
                           parametr: str,
                           skip_data_check: bool = False,
                           ):
    """
    Автоматическая проверка серии GET запросов.
    
    Parameters
    ----------
    skip_data_check : bool
        Если True, пропускает проверку содержимого data.
        Использовать для параметров пагинации (limit, offset).
    """
    responses = []
    for value, expected in test_cases.items():
        params = base_params.copy()
        params[parametr] = value
        
        response = await client.get(endpoint, params=params)
        assert response.status_code == expected, \
            f"GET {parametr}='{value}': ожидался {expected}, получен {response.status_code}"
        
        if not skip_data_check and expected in [200, 201] and response.status_code in [200, 201]:
            data = response.json()['data']
            if isinstance(data, list) and len(data) > 0:
                normalized_value = str(value).lower().strip()
                for item in data:
                    item_value = str(item.get(parametr, '')).lower()
                    assert normalized_value in item_value, \
                        f"GET {parametr}='{value}': значение '{normalized_value}' не найдено в поле '{parametr}' элемента {item}"
        responses.append(response)
    return responses