from typing import Type, TypeVar

import PIL
import PIL.IcnsImagePlugin
import PIL.Image
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


def get_albums(asset_id: str) -> list[model.AlbumResponseDto]:
    return get("albums", model.AlbumResponseDto, params={"assetId": asset_id})


def add_asset_to_album(asset_id: str, album_id: str) -> None:
    headers = {"Accept": "application/json", "x-api-key": settings.api_key}

    response = requests.put(
        f"{settings.server_url}/api/albums/{album_id}/assets",
        headers=headers,
        json={"ids": [asset_id]},
    )

    response.raise_for_status()


def trash_assets(asset_ids: list[str]) -> None:
    headers = {"Accept": "application/json", "x-api-key": settings.api_key}

    response = requests.delete(
        f"{settings.server_url}/api/assets",
        headers=headers,
        json={"ids": asset_ids, "force": True},
    )

    response.raise_for_status()


def get_asset(asset_id: str) -> model.AssetResponseDto:
    headers = {"Accept": "application/json", "x-api-key": settings.api_key}

    response = requests.get(
        f"{settings.server_url}/api/assets/{asset_id}",
        headers=headers,
        data={},
        params={},
    )

    response.raise_for_status()

    return model.AssetResponseDto.model_validate(response.json())


def get_thumbnail(asset_id: str) -> PIL.Image.Image:
    headers = {
        "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
        "x-api-key": settings.api_key,
    }

    response = requests.get(
        f"{settings.server_url}/api/assets/{asset_id}/thumbnail",
        headers=headers,
        data={},
        params={},
        stream=True,
    )

    response.raise_for_status()

    response.raw.decode_content = True  # handle spurious Content-Encoding

    return PIL.Image.open(response.raw)  # type: ignore
