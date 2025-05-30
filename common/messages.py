import json
from enum import Enum, auto

class MsgType(Enum):
    JOIN   = auto()   # gracz dołącza
    MOVE   = auto()   # przesłanie nowej pozycji i rozmiaru
    UPDATE = auto()   # serwer przesyła stan wszystkich graczy

def encode(msg_type: MsgType, payload: dict) -> str:
    return json.dumps({
        "type": msg_type.name.lower(),
        "data": payload
    })

def decode(raw: str) -> dict:
    obj = json.loads(raw)
    return {"type": obj["type"], "data": obj["data"]}