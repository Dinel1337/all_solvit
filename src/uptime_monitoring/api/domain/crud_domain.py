from fastapi import APIRouter, Depends, status
from src._core.response import API_response, construct_meta
from src.uptime_monitoring.config import DOMAINS_PREFIX, DOMAINS_TAGS
from src.uptime_monitoring.local_core.schemas import DomainCreate


router = APIRouter(prefix=DOMAINS_PREFIX, tags=DOMAINS_TAGS)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_domain(
    data: DomainCreate,
): ...
    
    # return API_response(
    #     status_code=status.HTTP_201_CREATED,
    #     success=True,
    #     data={"id": domain.id, "url": domain.url, "name": domain.name},
    #     meta=construct_meta(reason="Домен добавлен в мониторинг")
    # )