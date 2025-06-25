# Configurações de produção
import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-key-change-in-production'
    
    # Azure AD
    CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
    TENANT_ID = os.environ.get('AZURE_TENANT_ID')
    
    # Key Vault
    KEY_VAULT_URL = os.environ.get('AZURE_KEY_VAULT_URL')
    
    # Logic App
    LOGIC_APP_URL = os.environ.get('LOGIC_APP_URL')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
