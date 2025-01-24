from typing import Type, TypeVar

import pydantic
import requests

from .. import settings
from . import model

T = TypeVar("T", bound=pydantic.BaseModel)


def get(path: str, _model: Type[T], params: dict | None = None) -> list[T]:
    headers = {"Accept": "application/json", "x-api-key": settings.api_key}

    response = requests.get(
        f"{settings.server_url}/api/{path}", headers=headers, data={}, params=params
    )

    response.raise_for_status()

    return [_model.model_validate(item) for item in response.json()]


def get_duplicates() -> list[model.DuplicateResponseDto]:
    return get("duplicates", model.DuplicateResponseDto)


def get_albums(photo_id: str) -> list[model.AlbumResponseDto]:
    return get("albums", model.AlbumResponseDto, params={"assetId": photo_id})
