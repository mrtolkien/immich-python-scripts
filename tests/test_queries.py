from immich_python_scripts.api import queries


def test_get_duplicates():
    assert queries.get_duplicates()


def test_get_albums():
    assert queries.get_albums("e74e9b8d-ad73-4d4b-8332-d6028c8a6e26")


def test_get_thumbnail():
    assert queries.get_thumbnail("8448788b-e57b-424f-bd2e-4d910f0fd845")
