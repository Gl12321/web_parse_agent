from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.config import get_settings
from src.core.logger import setup_logger

logger = setup_logger("POSTGRES_CLIENT")
settings = get_settings()

class PostgresClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = create_engine(settings.DB_URL, pool_size=10)
            cls._instance.Session = sessionmaker(bind=cls._instance.engine)
            logger.info("PostgresClient initialized")
        return cls._instance

    def get_session(self) -> Session:
        return self._instance.Session()
