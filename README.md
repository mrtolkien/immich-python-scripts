# immich-python-scripts

A few python scripts to manage my Immich library

## Features

- **Duplicate Photos Management**: Review and merge duplicate photos step by step or automatically
- **Video Deduplication**: Review videos with the same name and remove duplicates
- **Favorites Download**: Download all your favorite pictures to a local folder

## Run

```sh
git clone https://github.com/mrtolkien/immich-python-scripts.git
vi .env.example
cp .env.example .env
uv run immich_scripts
```

You need a kitty-compatible terminal to view the thumbnails. I use Ghostty.

## Demo

![Duplicate picker](image.png)

## TODO

- [x] Drop textualize for a simpler approach
- [x] Logging
- [x] Image display
- [x] Download favorites feature
- [ ] Automated full image deduplication with a few rules
- [ ] Video deduplication
