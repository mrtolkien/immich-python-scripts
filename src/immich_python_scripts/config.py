import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    server_url: str
    api_key: str


settings = Config()  # type: ignore
