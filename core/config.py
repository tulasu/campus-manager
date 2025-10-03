from pydantic_settings import BaseSettings


class Config(BaseSettings):
    google_service_account: str
    google_sheet_id: str
    db_connection_url: str

    class Config:
        env_file = ".env"


config = Config()
