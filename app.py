import os
import json
import logging
import requests
import subprocess
import psycopg2
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')

# Configurações do banco
DB_CONFIG = {
    'host': os.environ.get('PGHOST'),
    'user': os.environ.get('PGUSER'),
    'port': os.environ.get('PGPORT', 5432),
    'database': os.environ.get('PGDATABASE')
}



# URL do Logic App
LOGIC_APP_URL = os.environ.get('LOGIC_APP_URL')

class DatabaseManager:
    """Gerenciador de conexão com PostgreSQL usando autenticação Azure"""
    
    def __init__(self):
        self.db_config = DB_CONFIG.copy()
    
    def get_azure_token(self):
        """Obtém token de acesso do Azure para PostgreSQL"""
        try:
            result = subprocess.run([
                'az', 'account', 'get-access-token',
                '--resource', 'https://ossrdbms-aad.database.windows.net',
                '--query', 'accessToken',
                '--output', 'tsv'
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao obter token A: {e}")
            return None
    
    def get_connection(self):
        """Estabelece conexão com PostgreSQL usando token Azure"""
        try:
            token = self.get_azure_token()
            if not token:
                raise Exception("Não foi possível obter token de acesso")
            
            # Configurar conexão com token
            config = self.db_config.copy()
            config['password'] = token
            
            conn = psycopg2.connect(**config)
            return conn
        except Exception as e:
            logger.error(f"Erro na conexão com banco: {e}")
            return None
    
    def init_database(self):
        """Inicializa as tabelas do banco se não existirem"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Criar tabela de solicitações de crédito
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solicitacoes_credito (
                    id SERIAL PRIMARY KEY,
                    cliente_id VARCHAR(50) NOT NULL,
                    nome VARCHAR(200) NOT NULL,
                    cpf VARCHAR(14) NOT NULL,
                    curso VARCHAR(100) NOT NULL,
                    semestre INTEGER NOT NULL,
                    valor_solicitado DECIMAL(10,2) NOT NULL,
                    renda_mensal DECIMAL(10,2) NOT NULL,
                    score_credito INTEGER DEFAULT 400,
                    pendencias_academicas BOOLEAN DEFAULT FALSE,
                    aprovado BOOLEAN NOT NULL,
                    motivo_reprovacao TEXT,
                    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_by_logic_app BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Criar índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_id ON solicitacoes_credito(cliente_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_solicitacao ON solicitacoes_credito(data_solicitacao)")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Banco de dados inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco: {e}")
            return False
    
    def save_solicitacao(self, cliente_data, resultado_analise):
        """Salva solicitação de crédito no banco"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO solicitacoes_credito 
                (cliente_id, nome, cpf, curso, semestre, valor_solicitado, 
                 renda_mensal, score_credito, pendencias_academicas, 
                 aprovado, motivo_reprovacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                cliente_data['cliente_id'],
                cliente_data['nome'],
                cliente_data['cpf'],
                cliente_data['curso'],
                cliente_data['semestre'],
                cliente_data['valor_solicitado'],
                cliente_data['renda_mensal'],
                cliente_data['score_credito'],
                cliente_data['pendencias_academicas'],
                resultado_analise['aprovado'],
                json.dumps(resultado_analise.get('motivo_reprovacao'))
            ))
            
            solicitacao_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Solicitação salva com ID: {solicitacao_id}")
            return solicitacao_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar solicitação: {e}")
            return False
    
    def get_statistics(self):
        """Obtém estatísticas das solicitações"""
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_solicitacoes,
                    COUNT(*) FILTER (WHERE aprovado = true) as aprovados,
                    COUNT(*) FILTER (WHERE aprovado = false) as reprovados,
                    COALESCE(SUM(valor_solicitado) FILTER (WHERE aprovado = true), 0) as valor_total_liberado
                FROM solicitacoes_credito
                WHERE data_solicitacao >= CURRENT_DATE - INTERVAL '30 days'
            """)
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return {
                'total_solicitacoes': result[0],
                'aprovados': result[1],
                'reprovados': result[2],
                'valor_total_liberado': float(result[3])
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return None

class CreditAnalyzer:
    """Classe para análise de crédito baseada em critérios universitários"""
    
    @staticmethod
    def analyze_credit(cliente_data):
        """
        Analisa o crédito baseado em critérios universitários
        
        Critérios de aprovação:
        - Valor solicitado <= R$ 5000 (limite para matrículas)
        - Score de crédito >= 300 (simulado)
        - Renda mínima = 2x o valor solicitado
        - Sem pendências acadêmicas
        """
        valor_solicitado = float(cliente_data.get('valor_solicitado', 0))
        renda_mensal = float(cliente_data.get('renda_mensal', 0))
        score_credito = int(cliente_data.get('score_credito', 0))
        pendencias_academicas = cliente_data.get('pendencias_academicas', False)
        
        # Critérios de aprovação
        criterios = {
            'valor_limite': valor_solicitado <= 5000,
            'score_minimo': score_credito >= 300,
            'renda_suficiente': renda_mensal >= (valor_solicitado * 2),
            'sem_pendencias': not pendencias_academicas
        }
        
        # Aprovado se todos os critérios forem atendidos
        aprovado = all(criterios.values())
        
        return {
            'aprovado': aprovado,
            'criterios_atendidos': criterios,
            'motivo_reprovacao': [k for k, v in criterios.items() if not v] if not aprovado else None
        }

# Inicializar gerenciador de banco
db_manager = DatabaseManager()

def simple_auth_required(f):
    """Decorador para autenticação simples baseada em sessão"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if not session.get("authenticated"):
        return redirect(url_for('login'))
    
    # Obter estatísticas do banco
    stats = db_manager.get_statistics() or {
        'total_solicitacoes': 0, 'aprovados': 0, 'reprovados': 0, 'valor_total_liberado': 0
    }
    
    return render_template('index_simple.html', user=session.get("user"), stats=stats)

@app.route('/login')
def login():
    return render_template('login_simple.html')

@app.route('/auth', methods=['POST'])
def authenticate():
    """Autenticação simples para demonstração"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Para demonstração, aceitar qualquer usuário com senha "123456"
    if password == "123456":
        session["authenticated"] = True
        session["user"] = {"name": username, "email": f"{username}@universidade.edu.br"}
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Credenciais inválidas. Use senha: 123456', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/solicitar-credito')
@simple_auth_required
def solicitar_credito():
    return render_template('solicitar_credito.html')

@app.route('/processar-credito', methods=['POST'])
@simple_auth_required
def processar_credito():
    try:
        # Coleta dados do formulário
        cliente_data = {
            'cliente_id': request.form.get('cliente_id'),
            'nome': request.form.get('nome'),
            'cpf': request.form.get('cpf'),
            'curso': request.form.get('curso'),
            'semestre': int(request.form.get('semestre')),
            'valor_solicitado': float(request.form.get('valor_solicitado', 0)),
            'renda_mensal': float(request.form.get('renda_mensal', 0)),
            'score_credito': int(request.form.get('score_credito', 400)),  # Simulado
            'pendencias_academicas': request.form.get('pendencias_academicas') == 'sim'
        }
        
        # Análise de crédito
        analyzer = CreditAnalyzer()
        resultado_analise = analyzer.analyze_credit(cliente_data)
        
        # Salvar no banco de dados
        solicitacao_id = db_manager.save_solicitacao(cliente_data, resultado_analise)
        
        if not solicitacao_id:
            flash('Erro ao salvar dados no banco. Tente novamente.', 'error')
            return redirect(url_for('solicitar_credito'))
        
        # Prepara dados para o Logic App
        logic_app_payload = {
            "clienteId": cliente_data['cliente_id'],
            "valorSolicitado": cliente_data['valor_solicitado'],
            "aprovado": resultado_analise['aprovado'],
            "dadosCliente": cliente_data,
            "resultadoAnalise": resultado_analise,
            "solicitacaoId": solicitacao_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Envia para Logic App
        try:
            response = requests.post(
                LOGIC_APP_URL,
                json=logic_app_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Dados enviados para Logic App com sucesso - Cliente: {cliente_data['cliente_id']}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar dados para Logic App: {str(e)}")
            flash('Erro na comunicação com o sistema. Dados salvos no banco.', 'warning')
        
        # Retorna resultado
        if resultado_analise['aprovado']:
            flash(f'Parabéns! Seu crédito de R$ {cliente_data["valor_solicitado"]:.2f} foi aprovado!', 'success')
            return render_template('resultado_aprovado.html', 
                                 cliente=cliente_data, 
                                 resultado=resultado_analise)
        else:
            motivos = resultado_analise['motivo_reprovacao']
            flash(f'Crédito não aprovado. Motivos: {", ".join(motivos)}', 'error')
            return render_template('resultado_reprovado.html', 
                                 cliente=cliente_data, 
                                 resultado=resultado_analise)
                                 
    except Exception as e:
        logger.error(f"Erro no processamento de crédito: {str(e)}")
        flash('Erro interno do sistema. Contate o suporte.', 'error')
        return redirect(url_for('solicitar_credito'))

@app.route('/health')
def health_check():
    """Endpoint para health check do Azure App Service"""
    # Verificar conexão com banco
    db_status = "ok" if db_manager.get_connection() else "error"
    
    return jsonify({
        'status': 'healthy' if db_status == 'ok' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database': db_status
    })

@app.route('/api/statistics')
@simple_auth_required
def get_statistics():
    """Endpoint para estatísticas"""
    stats = db_manager.get_statistics()
    return jsonify(stats or {
        'total_solicitacoes': 0,
        'aprovados': 0,
        'reprovados': 0,
        'valor_total_liberado': 0
    })

@app.route('/init-db')
def init_db():
    """Endpoint para inicializar banco (apenas para desenvolvimento)"""
    if db_manager.init_database():
        return jsonify({'status': 'success', 'message': 'Banco inicializado com sucesso'})
    else:
        return jsonify({'status': 'error', 'message': 'Erro ao inicializar banco'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Inicializar banco de dados
    db_manager.init_database()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
