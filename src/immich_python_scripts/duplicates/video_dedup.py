from collections import defaultdict

import questionary
from rich.console import Console
from rich.markdown import Markdown

from .. import api
from . import common


def dedup_videos():
    console = Console()
    console.print(
        Markdown("""
# Video Deduplication

- Shows files with the same name with their exif data
- Prompts to delete the duplicates

---

Getting videos from server...

---
""")
    )

    videos = api.queries.get_all_videos()

    # Find videos with the exact same name
    name_to_videos = defaultdict(list)

    for video in videos:
        name_to_videos[video.originalFileName].append(video)

    for same_name_videos in name_to_videos.values():
        if len(same_name_videos) < 2:
            continue

        common.show_video_table(same_name_videos)

        videos_to_delete = questionary.checkbox(
            "Select videos to delete",
            choices=[video.id for video in same_name_videos],
        ).ask()

        if videos_to_delete:
            if len(same_name_videos) == 2 and len(videos_to_delete) == 1:
                # If exactly one of two videos is being deleted, transfer its albums
                deleted_video = next(
                    v for v in same_name_videos if v.id in videos_to_delete
                )
                kept_video = next(
                    v for v in same_name_videos if v.id not in videos_to_delete
                )

                deleted_albums = api.queries.get_albums(deleted_video.id)
                kept_albums = api.queries.get_albums(kept_video.id)

                # Add kept video to all albums of the deleted video
                for album in deleted_albums:
                    if album.id not in [a.id for a in kept_albums]:
                        print(
                            f"Adding {kept_video.originalFileName} to album {album.albumName}"
                        )
                        api.queries.add_asset_to_album(kept_video.id, album.id)

            api.queries.trash_assets(videos_to_delete)
