from typing import Any


text:str = "10"
num :int = 10

number : int | float  = 12

digits : list[int] = [1,2,3,4,5]

table_5 : tuple[int, ...]  = (1,2,3,4,5)

table_6 : tuple[str, int] = ("A", 1)

shipment: dict[str, Any] = {
    "id": 120,
    "weight": 1.2,
    "content": "wooden table",
    "status": "in transit"
}