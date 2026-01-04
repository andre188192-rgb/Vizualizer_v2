from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./cnc_pulse.db"
    api_key: str = "changeme"
    basic_user: str = "admin"
    basic_pass: str = "admin"
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    model_config = SettingsConfigDict(env_prefix="CNC_", env_file=".env", env_file_encoding="utf-8")
