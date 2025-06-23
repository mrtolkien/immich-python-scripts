"""
Favorites Download Module for Immich Python Scripts

This module provides functionality to download all favorite pictures
from an Immich server to a local directory.

Features:
- Fetches all favorite picture assets from Immich (IMAGE type only)
- Downloads original files with their original names
- Shows progress during download
- Handles duplicate filenames gracefully
- Creates output directory if it doesn't exist

Usage:
    Run the main application and select "Download favorite pictures" from the menu.
    You'll be prompted to specify an output directory (defaults to ~/Downloads/immich_favorites).
    The module will then fetch all favorite pictures and download them with a progress bar.

API Requirements:
    - Requires valid Immich server URL and API key in .env file
    - API key must have read access to assets
"""

from pathlib import Path
from typing import List

import requests
from rich.console import Console
from tqdm import tqdm

from .. import settings
from ..api import model, queries


def get_favorites() -> List[model.AssetResponseDto]:
    """Get all favorite picture assets from Immich (IMAGE type only)."""
    search = queries.query_api_single(
        "POST",
        "search/metadata",
        model.SearchResponseDto,
        body={"type": "IMAGE", "isFavorite": True, "withExif": True},
    )

    favorites = search.assets.items

    # Handle pagination if there are more favorites
    while search.assets.nextPage:
        search = queries.query_api_single(
            "POST",
            "search/metadata",
            model.SearchResponseDto,
            body={
                "type": "IMAGE",
                "isFavorite": True,
                "withExif": True,
                "page": search.assets.nextPage,
            },
        )
        favorites += search.assets.items

    return favorites


def download_asset(asset: model.AssetResponseDto, output_dir: Path) -> str:
    """Download a single picture asset to the output directory.

    Returns:
        'success' if downloaded successfully
        'skipped' if file already exists
        'failed' if download failed
    """
    try:
        # Create filename based on original filename and ID to avoid conflicts
        filename = f"{asset.originalFileName}"
        if not filename:
            # Fallback to ID with extension based on mime type
            ext = ""
            if asset.originalMimeType:
                if "jpeg" in asset.originalMimeType or "jpg" in asset.originalMimeType:
                    ext = ".jpg"
                elif "png" in asset.originalMimeType:
                    ext = ".png"
                elif "heic" in asset.originalMimeType:
                    ext = ".heic"
                elif "mp4" in asset.originalMimeType:
                    ext = ".mp4"
            filename = f"{asset.id}{ext}"

        output_path = output_dir / filename

        # Skip if file already exists
        if output_path.exists():
            return "skipped"

        # Download the original asset
        headers = {"x-api-key": settings.api_key}
        response = requests.get(
            f"{settings.server_url}/api/assets/{asset.id}/original",
            headers=headers,
            stream=True,
        )
        response.raise_for_status()

        # Write to file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return "success"

    except Exception as e:
        Console().print(f"[red]Error downloading {asset.originalFileName}: {e}[/red]")
        return "failed"


def download_favorites_handler():
    """Handle the favorites download process."""
    console = Console()

    console.print("[bold blue]Downloading Favorite Pictures[/bold blue]")

    # Get output directory from user
    default_dir = Path.home() / "Pictures" / "Immich Favorites"

    while True:
        output_dir_str = input(
            f"Enter output directory (default: {default_dir}): "
        ).strip()
        if not output_dir_str:
            output_dir = default_dir
        else:
            output_dir = Path(output_dir_str)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            break
        except Exception as e:
            console.print(f"[red]Error creating directory: {e}[/red]")
            continue

    console.print(f"[green]Output directory: {output_dir}[/green]")

    # Get favorites
    console.print("[yellow]Fetching favorite assets...[/yellow]")
    try:
        favorites = get_favorites()
    except Exception as e:
        console.print(f"[red]Error fetching favorites: {e}[/red]")
        return

    if not favorites:
        console.print("[yellow]No favorite assets found.[/yellow]")
        return

    console.print(f"[green]Found {len(favorites)} favorite pictures[/green]")

    if not favorites:
        console.print("[yellow]No favorite pictures found.[/yellow]")
        return

    console.print(f"[green]Downloading {len(favorites)} favorite pictures...[/green]")

    # Download with progress bar
    successful = 0
    skipped = 0
    failed = 0

    with tqdm(total=len(favorites), desc="Processing") as pbar:
        for asset in favorites:
            result = download_asset(asset, output_dir)
            if result == "success":
                successful += 1
                pbar.set_description("Downloading")
            elif result == "skipped":
                skipped += 1
                pbar.set_description("Skipping existing")
            else:  # failed
                failed += 1
                pbar.set_description("Processing")
            pbar.update(1)

    console.print("[green]Processing complete![/green]")
    console.print(f"[green]Successfully downloaded: {successful}[/green]")
    if skipped > 0:
        console.print(f"[yellow]Files already existed (skipped): {skipped}[/yellow]")
    if failed > 0:
        console.print(f"[red]Failed downloads: {failed}[/red]")
    console.print(f"[blue]Files saved to: {output_dir}[/blue]")
