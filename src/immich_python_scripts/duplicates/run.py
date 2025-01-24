from .. import api


def run_duplicates():
    duplicates = api.queries.get_duplicates()

    for duplicate_assets in duplicates:
        albums = set()

        for asset in duplicate_assets.assets:
            albums.update(api.queries.get_albums(asset.id))

        print(albums)

        break
