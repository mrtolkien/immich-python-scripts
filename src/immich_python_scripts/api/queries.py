from typing import Type, TypeVar

import PIL
import PIL.IcnsImagePlugin
import PIL.Image
import pydantic
import requests

from .. import settings
from . import model

T = TypeVar("T", bound=pydantic.BaseModel)

HEADERS = {"Accept": "application/json", "x-api-key": settings.api_key}


def query_api_raw(
    verb: str,
    path: str,
    params: dict | None = None,
    body: dict | None = None,
) -> requests.Response:
    response = requests.request(
        verb,
        f"{settings.server_url}/api/{path}",
        headers=HEADERS,
        json=body or {},
        params=params or {},
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        print(response.text)
        raise e

    return response


def query_api_list(
    verb: str,
    path: str,
    _model: Type[T],
    params: dict | None = None,
    body: dict | None = None,
) -> list[T]:
    response = query_api_raw(verb, path, params, body)

    if _model is None:
        return response.json()

    return [_model.model_validate(item) for item in response.json()]


def query_api_single(
    verb: str,
    path: str,
    _model: Type[T],
    params: dict | None = None,
    body: dict | None = None,
) -> T:
    response = query_api_raw(verb, path, params, body)

    return _model.model_validate(response.json())


def get_duplicates() -> list[model.DuplicateResponseDto]:
    return query_api_list("GET", "duplicates", model.DuplicateResponseDto)


def get_albums(asset_id: str) -> list[model.AlbumResponseDto]:
    return query_api_list(
        "GET", "albums", model.AlbumResponseDto, params={"assetId": asset_id}
    )


def add_asset_to_album(asset_id: str, album_id: str) -> None:
    query_api_raw("PUT", f"/albums/{album_id}/assets", body={"ids": [asset_id]})


def trash_assets(asset_ids: list[str]) -> None:
    print(f"Trashing assets {asset_ids}")
    query_api_raw("DELETE", "assets", body={"ids": asset_ids})


def get_asset(asset_id: str) -> model.AssetResponseDto:
    return query_api_single("GET", f"assets/{asset_id}", model.AssetResponseDto)


def get_all_videos() -> list[model.AssetResponseDto]:
    search = query_api_single(
        "POST",
        "search/metadata",
        model.SearchResponseDto,
        body={"type": "VIDEO", "withExif": "true"},
    )

    videos = search.assets.items

    while search.assets.nextPage:
        search = query_api_single(
            "POST",
            "search/metadata",
            model.SearchResponseDto,
            body={"type": "VIDEO", "withExif": "true"}
            | {"page": search.assets.nextPage},
        )

        videos += search.assets.items

    return videos


def get_thumbnail(asset_id: str) -> PIL.Image.Image | None:
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

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None

    response.raw.decode_content = True  # handle spurious Content-Encoding

    return PIL.Image.open(response.raw)  # type: ignore
