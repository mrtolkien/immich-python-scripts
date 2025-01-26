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
            api.queries.trash_assets(videos_to_delete)
