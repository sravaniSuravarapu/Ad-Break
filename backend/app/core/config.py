from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str | None = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "adbreak"
    database_password: str = "adbreak"
    database_name: str = "adbreak"
    jwt_secret: str = "dev-only-change-me"
    jwt_expire_minutes: int = 60
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    seed_demo: bool = False

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            "postgresql+psycopg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


settings = Settings()
