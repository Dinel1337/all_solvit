from datetime import datetime, timezone
from typing import Optional

def construct_meta(reason: Optional[str | int] = None,
                   other: Optional[dict] = None) -> dict:
    """

    Конструктор для meta
    Входные данные:
    - reason: ответ пользователю
    - other: другие вспомогательные данные

    """
    meta = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            'reason': reason,
            'other' : other 
            }
    return meta