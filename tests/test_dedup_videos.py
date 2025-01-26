from immich_python_scripts.duplicates import video_dedup


def test_dedup_videos():
    assert video_dedup.dedup_videos()
