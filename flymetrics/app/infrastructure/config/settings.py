from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "FlymetricsOS"
    APP_VERSION: str = "1.0.0"
    
    # Base de Datos
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "flymetrics_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "miguepro"
    
    # JWT
    JWT_SECRET: str = "flymetrics_super_secret_key_2025_prod_local_key_hash"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    
    # Servidor
    PORT: int = 3000
    
    # APIS Externas Mocks / Reales
    GOOGLE_MAPS_API_KEY: str = "miguepro_maps_api_key_mock_local"
    WHATSAPP_VERIFY_TOKEN: str = "flymetrics_whatsapp_verification_token_local"
    WHATSAPP_ACCESS_TOKEN: str = "mock_whatsapp_access_token_from_meta_developer_portal"
    WHATSAPP_PHONE_NUMBER_ID: str = "1234567890"
    
    # AWS S3
    AWS_S3_BUCKET: str = "flymetrics-deliverables-bucket"
    AWS_REGION: str = "us-east-1"
    
    # Configuración de Pydantic
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
