import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    server_url: str
    api_key: str

    # Whether to pick HEIC files over JPG files if present
    pick_heic: bool = True


settings = Config()  # type: ignore
