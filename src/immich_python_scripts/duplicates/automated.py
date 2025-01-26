import questionary
from rich.console import Console
from rich.markdown import Markdown

from immich_python_scripts.duplicates.common import (
    format_file_size,
    get_duplicate_data,
    pick_asset,
    show_table,
)

from .. import api, settings


def automated_handler():
    console = Console()
    console.print(
        Markdown("""
# Semi-Automated Duplicate Management

- If all assets have the same type, pick the biggest one
- If assets have different types, ask the user

---

Getting duplicates from server...

---
""")
    )

    duplicates = api.queries.get_duplicates()

    print(f"Found {len(duplicates)} duplicate groups")

    for duplicate in duplicates:
        handle_duplicate_group(duplicate)


def handle_duplicate_group(duplicate):
    assets, albums = get_duplicate_data(duplicate)

    # Create a table to display duplicate assets
    largest_asset_index = show_table(assets, albums)

    types = set(a.originalMimeType for a in assets)

    if len(types) == 1:
        print("All assets have the same type, pick the largest one")
        return pick_asset(assets, albums, largest_asset_index)

    elif types == {"image/jpeg", "image/heic"} and settings.pick_heic:
        print("Picking HEIC file over JPG file")

        # Pick the biggest HEIC file
        largest_asset_index = -1
        largest_asset_size = 0

        for idx, asset in enumerate(assets):
            if asset.originalMimeType != "image/heic":
                continue

            if (
                asset.exifInfo
                and (asset.exifInfo.fileSizeInByte or -1) > largest_asset_size
            ):
                largest_asset_index = idx
                largest_asset_size = asset.exifInfo.fileSizeInByte or -1

        if largest_asset_index != -1:
            return pick_asset(assets, albums, largest_asset_index)

    # Select asset to keep
    choices = [
        {
            "name": f"{assets[i].originalFileName} ({format_file_size(d.exifInfo.fileSizeInByte if d.exifInfo else 0)})",
            "value": i,
        }
        for i, d in enumerate(assets)
    ]

    picked_asset_index = questionary.select(
        "Which asset do you want to keep?",
        choices=choices,
        default=choices[largest_asset_index],
    ).ask()

    pick_asset(assets, albums, picked_asset_index)
