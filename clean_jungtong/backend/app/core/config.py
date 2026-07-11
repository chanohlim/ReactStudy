from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url:str; supabase_url:str; supabase_jwt_issuer:str; supabase_jwt_audience:str='authenticated'; supabase_jwks_url:str
    vapid_public_key:str=''; vapid_private_key:str=''; vapid_subject:str='mailto:admin@example.com'; cron_secret:str; frontend_origin:str='http://localhost:5173'; environment:str='development'; timezone:str='Asia/Seoul'
    model_config=SettingsConfigDict(env_file='.env',case_sensitive=False)
settings=Settings()  # type: ignore[call-arg]
