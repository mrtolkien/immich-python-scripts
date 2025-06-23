from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pytest

from immich_python_scripts.api.model import (
    AssetResponseDto,
    AssetTypeEnum,
    SearchAssetResponseDto,
    SearchResponseDto,
)
from immich_python_scripts.favorites import (
    download_asset,
    download_favorites_handler,
    get_favorites,
)


@pytest.fixture
def mock_asset():
    """Create a mock asset for testing."""
    test_datetime = datetime(2023, 1, 1, 0, 0, 0)
    return AssetResponseDto(
        id="test-asset-id",
        checksum="test-checksum",
        deviceAssetId="test-device-asset-id",
        deviceId="test-device-id",
        duration="00:00:00",
        fileCreatedAt=test_datetime,
        fileModifiedAt=test_datetime,
        hasMetadata=True,
        isArchived=False,
        isFavorite=True,
        isOffline=False,
        isTrashed=False,
        libraryId=None,
        localDateTime=test_datetime,
        originalFileName="test-image.jpg",
        originalMimeType="image/jpeg",
        originalPath="/path/to/test-image.jpg",
        ownerId="test-owner-id",
        resized=None,
        thumbhash="test-thumbhash",
        type=AssetTypeEnum.IMAGE,
        updatedAt=test_datetime,
    )


@patch("immich_python_scripts.favorites.queries.query_api_single")
def test_get_favorites(mock_query):
    """Test getting favorites from API."""
    # Mock response
    mock_search_response = Mock(spec=SearchResponseDto)
    mock_assets = Mock(spec=SearchAssetResponseDto)
    mock_assets.items = [Mock(spec=AssetResponseDto)]
    mock_assets.nextPage = None
    mock_search_response.assets = mock_assets

    mock_query.return_value = mock_search_response

    result = get_favorites()

    assert len(result) == 1
    mock_query.assert_called_once()


@patch("immich_python_scripts.favorites.requests.get")
@patch("builtins.open", new_callable=mock_open)
def test_download_asset_success(mock_file, mock_get, mock_asset, tmp_path):
    """Test successful asset download."""
    # Mock successful HTTP response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.iter_content.return_value = [b"test content"]
    mock_get.return_value = mock_response

    output_dir = tmp_path / "downloads"
    output_dir.mkdir()

    result = download_asset(mock_asset, output_dir)

    assert result is True
    mock_get.assert_called_once()
    mock_file.assert_called_once()


@patch("immich_python_scripts.favorites.requests.get")
def test_download_asset_failure(mock_get, mock_asset, tmp_path):
    """Test asset download failure."""
    # Mock failed HTTP response
    mock_get.side_effect = Exception("Network error")

    output_dir = tmp_path / "downloads"
    output_dir.mkdir()

    result = download_asset(mock_asset, output_dir)

    assert result is False


@patch("immich_python_scripts.favorites.get_favorites")
@patch("immich_python_scripts.favorites.download_asset")
@patch("builtins.input")
@patch("immich_python_scripts.favorites.Console")
def test_download_favorites_handler_no_favorites(
    mock_console, mock_input, mock_download, mock_get_favorites
):
    """Test handler when no favorites are found."""
    mock_input.return_value = ""  # Use default directory
    mock_get_favorites.return_value = []

    download_favorites_handler()

    mock_get_favorites.assert_called_once()
    mock_download.assert_not_called()


@patch("immich_python_scripts.favorites.get_favorites")
@patch("immich_python_scripts.favorites.download_asset")
@patch("builtins.input")
@patch("immich_python_scripts.favorites.Console")
@patch("immich_python_scripts.favorites.Path.mkdir")
def test_download_favorites_handler_with_favorites(
    mock_mkdir, mock_console, mock_input, mock_download, mock_get_favorites, mock_asset
):
    """Test handler with favorites to download."""
    mock_input.return_value = ""  # Use default directory
    mock_get_favorites.return_value = [mock_asset]
    mock_download.return_value = True
    mock_mkdir.return_value = None  # Mock directory creation

    download_favorites_handler()

    mock_get_favorites.assert_called_once()
    mock_download.assert_called_once()
