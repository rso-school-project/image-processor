import time

from typing import List
from fastapi import APIRouter, Depends
from starlette.requests import Request
from func_timeout import func_set_timeout
from sqlalchemy.orm import Session


from image_processor import settings
from image_processor.utils import fallback

router = APIRouter()

@router.get('/settings')
async def test_configs(request: Request):
    return {"Config for X:": f"{settings.config_x}", "Config for Y:": f"{settings.config_y}"}


def test_fallback():
    return {'Detail': 'This is fallback function. Request timed-out'}


@router.get('/timeout/{seconds}')
@fallback(fallback_function=test_fallback)
@func_set_timeout(3)
def test_timeout_feature(seconds: str):
    time.sleep(float(seconds))
    return {'Timeout': seconds, 'Detail': 'Request did not time-out.'}
