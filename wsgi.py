import os
import sys

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app import app
    
    # Configuração para Azure App Service
    application = app
    
    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 8000))
        app.run(host='0.0.0.0', port=port, debug=False)
        
except Exception as e:
    print(f"Erro crítico ao importar aplicação: {e}")
    sys.exit(1)