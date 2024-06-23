from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    postgres_db: str = 'test'
    postgres_user: str = 'test'
    postgres_password: str = 'test'
    postgres_port: str = '5432'
    postgres_host: str = 'localhost'

    redis_host: str = 'localhost'
    redis_port: int = 6379

    redis_cache_time: int = 900

    secret_key: str = 'secret'
    algorithm: str = 'HS256'

    mail_username: str = 'username'
    mail_password: str = 'password'
    mail_from: str = 'test@example.com'
    mail_port: int = 587
    mail_server: str = 'smtp.example.com'
    mail_validate_cert: bool = True

    origins: list[str] = ['http://localhost', 'http://localhost:8080']

    cloudinary_name: str = 'name'
    cloudinary_api_key: str = 'key'
    cloudinary_api_secret: str = 'secret'

    def postgres_url(self) -> str:
        # return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}"
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}"


settings = Settings()



# from pydantic_settings import BaseSettings, SettingsConfigDict
# from dotenv import load_dotenv

# load_dotenv()


# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file='.env',
#         env_file_encoding='utf-8'
#     )

#     postgres_db: str
#     postgres_user: str
#     postgres_password: str
#     postgres_port: str
#     postgres_host: str

#     redis_host: str
#     redis_port: int

#     redis_cache_time: int

#     secret_key: str
#     algorithm: str

#     mail_username: str
#     mail_password: str
#     mail_from: str
#     mail_port: int
#     mail_server: str
#     mail_validate_cert: bool

#     origins: list[str] = ['http://localhost', 'http://localhost:8080']

#     cloudinary_name: str
#     cloudinary_api_key: str
#     cloudinary_api_secret: str = 'secret'

#     def postgres_url(self) -> str:
#         # return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}"
#         return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}"



# settings = Settings()

# if __name__ == "__main__":
#     print(settings.model_dump())