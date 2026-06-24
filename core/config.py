from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    llm_provider: str = "qianwen"
    qianwen_api_key: str = ""
    deepseek_api_key: str = ""
    encryption_key: str = "default_dev_key_change_in_production"
    database_url: str = "sqlite+aiosqlite:///./med_cabinet.db"
    api_base_url: str = "http://localhost:8000"
    
    # MySQL数据库配置 (用于medician药品知识库)
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "m"

    # 邮件提醒配置 (163邮箱)
    smtp_host: str = "smtp.163.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    default_from_email: str = ""

    # 上传文件目录
    @property
    def uploads_dir(self) -> str:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "uploads")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def mysql_sync_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
