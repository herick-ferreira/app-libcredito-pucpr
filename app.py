import os
import json
import logging
import requests
import urllib.parse
import unicodedata
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from dotenv import load_dotenv
# from sqlalchemy import create_engine, text


# apt-get remove g++  
# && apt-get install g++ && apt-get update &&
# apt-get install -y unixodbc-dev  
# ACCEPT_EULA=Y && apt-get install msodbcsql17  && pip install -r requirements.txt && gunicorn --bind=0.0.0.0:$PORT wsgi:app

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')

# Configurações do Azure SQL Database
AZURE_SQL_CONFIG = {
    'server': os.environ.get('AZURE_SQL_SERVER'),
    'database': os.environ.get('AZURE_SQL_DATABASE'),
    'username': os.environ.get('AZURE_SQL_USERNAME'),
    'password': os.environ.get('AZURE_SQL_PASSWORD')
}

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# # URL do Logic App
# LOGIC_APP_URL = os.environ.get('LOGIC_APP_URL')

# def normalize_email(email):
#     """Normaliza email removendo acentos, convertendo para minúsculas e validando formato"""
#     if not email:
#         return None
    
#     # Remover espaços
#     email = email.strip()
    
#     # Converter para minúsculas
#     email = email.lower()
    
#     # Remover acentos
#     email = unicodedata.normalize('NFD', email)
#     email = ''.join(c for c in email if unicodedata.category(c) != 'Mn')
    
#     # Validar formato básico de email
#     email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     if not re.match(email_pattern, email):
#         logger.error(f"Email inválido detectado: {email}")
#         return None
    
#     # Verificar se não tem domínios duplicados
#     if email.count('@') > 1:
#         logger.error(f"Email com múltiplos @ detectado: {email}")
#         return None
    
#     # Garantir que é do domínio correto
#     if not email.endswith('@pucpr.edu.br'):
#         logger.warning(f"Email fora do domínio PUCPR: {email}")
#         # Corrigir domínio se necessário
#         username = email.split('@')[0]
#         email = f"{username}@pucpr.edu.br"
    
#     return email

# def normalize_cpf(cpf):
#     """Normaliza CPF removendo pontos e traços"""
#     if not cpf:
#         return None
    
#     # Remover caracteres não numéricos
#     cpf = re.sub(r'[^0-9]', '', cpf)
    
#     # Verificar se tem 11 dígitos
#     if len(cpf) != 11:
#         return None
    
#     return cpf

# class DatabaseManager:
#     """Gerenciador de conexão com Azure SQL Database"""
    
#     def __init__(self):
#         self.config = AZURE_SQL_CONFIG.copy()
    
#     def create_engine(self):
#         """Criar engine SQLAlchemy para conectar ao Azure SQL Database"""
#         try:
#             password_encoded = urllib.parse.quote_plus(self.config['password'])
#             connection_string = (
#                 f"mssql+pymssql://{self.config['username']}:{password_encoded}"
#                 f"@{self.config['server']}/{self.config['database']}"
#             )
            
#             engine = create_engine(connection_string)
#             logger.info("Engine do Azure SQL Database criada com sucesso")
#             return engine
#         except Exception as e:
#             logger.error(f"Erro ao criar engine: {e}")
#             return None
    
#     def get_connection(self):
#         """Estabelece conexão com Azure SQL Database"""
#         try:
#             engine = self.create_engine()
#             if not engine:
#                 return None
            
#             connection = engine.connect()
#             logger.info("Conexão com Azure SQL Database estabelecida com sucesso")
#             return connection
#         except Exception as e:
#             logger.error(f"Erro na conexão com banco: {e}")
#             return None
    
#     def init_database(self):
#         """Inicializa as tabelas do banco se não existirem"""
#         try:
#             conn = self.get_connection()
#             if not conn:
#                 return False
            
#             # Criar tabela de solicitações de crédito
#             conn.execute(text("""
#                 IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='solicitacoes_credito' AND xtype='U')
#                 CREATE TABLE solicitacoes_credito (
#                     id INT IDENTITY(1,1) PRIMARY KEY,
#                     email VARCHAR(200) NOT NULL,
#                     nome VARCHAR(200) NOT NULL,
#                     cpf VARCHAR(14) NOT NULL,
#                     curso VARCHAR(100) NOT NULL,
#                     semestre INT NOT NULL,
#                     valor_solicitado DECIMAL(10,2) NOT NULL,
#                     renda_mensal DECIMAL(10,2) NOT NULL,
#                     score_credito INT DEFAULT 400,
#                     pendencias_academicas BIT DEFAULT 0,
#                     aprovado BIT NOT NULL,
#                     motivo_reprovacao NVARCHAR(MAX),
#                     data_solicitacao DATETIME2 DEFAULT GETDATE(),
#                     processed_by_logic_app BIT DEFAULT 0,
#                     fora_padrao BIT DEFAULT 0
#                 )
#             """))
            
#             # Criar índices
#             conn.execute(text("""
#                 IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_email')
#                 CREATE INDEX idx_email ON solicitacoes_credito(email)
#             """))
            
#             conn.execute(text("""
#                 IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_data_solicitacao')
#                 CREATE INDEX idx_data_solicitacao ON solicitacoes_credito(data_solicitacao)
#             """))
            
#             conn.commit()
#             conn.close()
            
#             logger.info("Banco de dados inicializado com sucesso")
#             return True
            
#         except Exception as e:
#             logger.error(f"Erro ao inicializar banco: {e}")
#             return False
    
#     def save_solicitacao(self, cliente_data, resultado_analise):
#         """Salva solicitação de crédito no banco"""
#         try:
#             conn = self.get_connection()
#             if not conn:
#                 return False
            
#             # Normalizar email antes de salvar
#             email_normalizado = normalize_email(cliente_data['email'])
#             if not email_normalizado:
#                 logger.error(f"Não foi possível normalizar email: {cliente_data['email']}")
#                 return False
            
#             # Gerar cliente_id baseado no email normalizado
#             cliente_id = email_normalizado.split('@')[0].replace('.', '_').upper()
            
#             # Log da normalização
#             if email_normalizado != cliente_data['email']:
#                 logger.info(f"Email normalizado: {cliente_data['email']} -> {email_normalizado}")
            
#             result = conn.execute(text("""
#                 INSERT INTO solicitacoes_credito 
#                 (cliente_id, email, nome, cpf, curso, semestre, valor_solicitado, 
#                  renda_mensal, score_credito, pendencias_academicas, 
#                  aprovado, motivo_reprovacao, fora_padrao)
#                 OUTPUT INSERTED.id
#                 VALUES (:cliente_id, :email, :nome, :cpf, :curso, :semestre, :valor_solicitado, 
#                         :renda_mensal, :score_credito, :pendencias_academicas, 
#                         :aprovado, :motivo_reprovacao, :fora_padrao)
#             """), {
#                 'cliente_id': cliente_id,
#                 'email': email_normalizado,  # Usar email normalizado
#                 'nome': cliente_data['nome'],
#                 'cpf': cliente_data['cpf'],
#                 'curso': cliente_data['curso'],
#                 'semestre': cliente_data['semestre'],
#                 'valor_solicitado': cliente_data['valor_solicitado'],
#                 'renda_mensal': cliente_data['renda_mensal'],
#                 'score_credito': cliente_data['score_credito'],
#                 'pendencias_academicas': cliente_data['pendencias_academicas'],
#                 'aprovado': resultado_analise['aprovado'],
#                 'motivo_reprovacao': json.dumps(resultado_analise.get('motivo_reprovacao')),
#                 'fora_padrao': resultado_analise.get('fora_padrao', False)
#             })
            
#             solicitacao_id = result.fetchone()[0]
#             conn.commit()
#             conn.close()
            
#             logger.info(f"Solicitação salva com ID: {solicitacao_id} para email: {email_normalizado}")
#             return solicitacao_id
            
#         except Exception as e:
#             logger.error(f"Erro ao salvar solicitação: {e}")
#             return False
    
#     def get_statistics(self):
#         """Obtém estatísticas das solicitações"""
#         try:
#             conn = self.get_connection()
#             if not conn:
#                 return None
            
#             result = conn.execute(text("""
#                 SELECT 
#                     COUNT(*) as total_solicitacoes,
#                     SUM(CASE WHEN aprovado = 1 THEN 1 ELSE 0 END) as aprovados,
#                     SUM(CASE WHEN aprovado = 0 THEN 1 ELSE 0 END) as reprovados,
#                     COALESCE(SUM(CASE WHEN aprovado = 1 THEN valor_solicitado ELSE 0 END), 0) as valor_total_liberado
#                 FROM solicitacoes_credito
#                 WHERE data_solicitacao >= DATEADD(day, -30, GETDATE())
#             """))
            
#             row = result.fetchone()
#             conn.close()
            
#             return {
#                 'total_solicitacoes': row[0],
#                 'aprovados': row[1],
#                 'reprovados': row[2],
#                 'valor_total_liberado': float(row[3])
#             }
            
#         except Exception as e:
#             logger.error(f"Erro ao obter estatísticas: {e}")
#             return None
    
#     def check_monthly_limit(self, email, cpf=None):
#         """Verifica se o cliente já fez uma solicitação no mês atual (por email E por CPF)"""
#         try:
#             conn = self.get_connection()
#             if not conn:
#                 logger.error("Erro: Não foi possível conectar ao banco para verificar limite")
#                 return True  # Em caso de erro, bloquear por segurança
            
#             # Normalizar email
#             email_normalizado = normalize_email(email)
#             if not email_normalizado:
#                 logger.error(f"Email inválido fornecido: {email}")
#                 return True  # Bloquear email inválido
            
#             # Normalizar CPF se fornecido
#             cpf_normalizado = normalize_cpf(cpf) if cpf else None
            
#             logger.info(f"Verificando limite mensal para email: {email_normalizado}")
#             if cpf_normalizado:
#                 logger.info(f"Verificando também por CPF: {cpf_normalizado}")
            
#             # Verificar por email normalizado
#             result_email = conn.execute(text("""
#                 SELECT COUNT(*) as total, MAX(data_solicitacao) as ultima_solicitacao
#                 FROM solicitacoes_credito 
#                 WHERE email = :email 
#                 AND YEAR(data_solicitacao) = YEAR(GETDATE())
#                 AND MONTH(data_solicitacao) = MONTH(GETDATE())
#             """), {'email': email_normalizado})
            
#             row_email = result_email.fetchone()
#             count_email = row_email[0]
#             ultima_email = row_email[1]
            
#             # Verificar por CPF se fornecido
#             count_cpf = 0
#             ultima_cpf = None
#             emails_cpf = []
            
#             if cpf_normalizado:
#                 result_cpf = conn.execute(text("""
#                     SELECT COUNT(*) as total, MAX(data_solicitacao) as ultima_solicitacao,
#                            STRING_AGG(email, ', ') as emails
#                     FROM solicitacoes_credito 
#                     WHERE REPLACE(REPLACE(REPLACE(cpf, '.', ''), '-', ''), ' ', '') = :cpf
#                     AND YEAR(data_solicitacao) = YEAR(GETDATE())
#                     AND MONTH(data_solicitacao) = MONTH(GETDATE())
#                 """), {'cpf': cpf_normalizado})
                
#                 row_cpf = result_cpf.fetchone()
#                 count_cpf = row_cpf[0]
#                 ultima_cpf = row_cpf[1]
#                 emails_cpf_str = row_cpf[2] or ""
#                 emails_cpf = [e.strip() for e in emails_cpf_str.split(',') if e.strip()]
            
#             conn.close()
            
#             # Log detalhado
#             logger.info(f"Encontradas {count_email} solicitações por EMAIL no mês atual")
#             if count_cpf > 0:
#                 logger.info(f"Encontradas {count_cpf} solicitações por CPF no mês atual")
#                 logger.info(f"Emails associados ao CPF: {emails_cpf}")
            
#             if ultima_email:
#                 logger.info(f"Última solicitação por email: {ultima_email}")
#             if ultima_cpf:
#                 logger.info(f"Última solicitação por CPF: {ultima_cpf}")
            
#             # Se encontrou qualquer solicitação (por email OU por CPF), bloquear
#             limite_atingido = (count_email > 0) or (count_cpf > 0)
            
#             if limite_atingido:
#                 if count_email > 0 and count_cpf > 0:
#                     logger.warning(f"LIMITE MENSAL ATINGIDO - Bloqueando por EMAIL e CPF para {email_normalizado}")
#                 elif count_email > 0:
#                     logger.warning(f"LIMITE MENSAL ATINGIDO - Bloqueando por EMAIL para {email_normalizado}")
#                 else:
#                     logger.warning(f"LIMITE MENSAL ATINGIDO - Bloqueando por CPF {cpf_normalizado} (emails: {emails_cpf})")
#             else:
#                 logger.info(f"LIMITE OK - Permitindo solicitação para {email_normalizado}")
            
#             return limite_atingido
            
#         except Exception as e:
#             logger.error(f"Erro ao verificar limite mensal: {e}")
#             # Em caso de erro, bloquear por segurança
#             return True

# class CreditAnalyzer:
#     """Classe para análise de crédito baseada em critérios universitários"""
    
#     @staticmethod
#     def analyze_credit(cliente_data, allow_out_of_pattern=True):
#         """
#         Analisa o crédito baseado em critérios universitários
        
#         Critérios de aprovação padrão:
#         - Valor solicitado <= R$ 5000 (limite para matrículas)
#         - Score de crédito >= 300 (simulado)
#         - Renda mínima = 2x o valor solicitado
#         - Sem pendências acadêmicas
        
#         Se allow_out_of_pattern=True, aprova mesmo fora do padrão com alerta
#         """
#         valor_solicitado = float(cliente_data.get('valor_solicitado', 0))
#         renda_mensal = float(cliente_data.get('renda_mensal', 0))
#         score_credito = int(cliente_data.get('score_credito', 0))
#         pendencias_academicas = cliente_data.get('pendencias_academicas', False)
        
#         # Critérios de aprovação
#         criterios = {
#             'valor_limite': valor_solicitado <= 5000,
#             'score_minimo': score_credito >= 300,
#             'renda_suficiente': renda_mensal >= (valor_solicitado * 2),
#             'sem_pendencias': not pendencias_academicas
#         }
        
#         # Verificar se está dentro do padrão
#         dentro_padrao = all(criterios.values())
        
#         # Se não está no padrão mas permite fora do padrão
#         if not dentro_padrao and allow_out_of_pattern:
#             return {
#                 'aprovado': True,
#                 'criterios_atendidos': criterios,
#                 'motivo_reprovacao': None,
#                 'fora_padrao': True,
#                 'alertas': [k for k, v in criterios.items() if not v]
#             }
        
#         # Aprovação normal (dentro do padrão)
#         return {
#             'aprovado': dentro_padrao,
#             'criterios_atendidos': criterios,
#             'motivo_reprovacao': [k for k, v in criterios.items() if not v] if not dentro_padrao else None,
#             'fora_padrao': False,
#             'alertas': []
#         }

# # Inicializar gerenciador de banco
# db_manager = DatabaseManager()

# def simple_auth_required(f):
#     """Decorador para autenticação simples baseada em sessão"""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get("authenticated"):
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# @app.route('/')
# def index():
#     if not session.get("authenticated"):
#         return redirect(url_for('login'))
    
#     # Obter estatísticas do banco
#     stats = db_manager.get_statistics() or {
#         'total_solicitacoes': 0, 'aprovados': 0, 'reprovados': 0, 'valor_total_liberado': 0
#     }
    
#     return render_template('index_simple.html', user=session.get("user"), stats=stats)

# @app.route('/login')
# def login():
#     return render_template('login_simple.html')

# @app.route('/auth', methods=['POST'])
# def authenticate():
#     """Autenticação simples para demonstração"""
#     username = request.form.get('username')
#     password = request.form.get('password')
    
#     # Para demonstração, aceitar qualquer usuário com senha "123456"
#     if password == "123456":
#         # Verificar se o usuário já digitou um email completo ou apenas o nome de usuário
#         if '@' in username:
#             # Usuário digitou email completo
#             email_raw = username
#             # Extrair nome do usuário (parte antes do @)
#             nome_usuario = username.split('@')[0]
#         else:
#             # Usuário digitou apenas o nome, criar email
#             email_raw = f"{username}@pucpr.edu.br"
#             nome_usuario = username
        
#         # Normalizar email
#         email_normalizado = normalize_email(email_raw)
        
#         if not email_normalizado:
#             flash('Email inválido. Use o formato: nome@pucpr.edu.br ou apenas "nome".', 'error')
#             return redirect(url_for('login'))
        
#         session["authenticated"] = True
#         session["user"] = {"name": nome_usuario, "email": email_normalizado}
        
#         logger.info(f"Login realizado: {username} -> {email_normalizado}")
#         flash('Login realizado com sucesso!', 'success')
#         return redirect(url_for('index'))
#     else:
#         flash('Credenciais inválidas. Use senha: 123456', 'error')
#         return redirect(url_for('login'))

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('Logout realizado com sucesso!', 'info')
#     return redirect(url_for('login'))

# @app.route('/solicitar-credito')
# @simple_auth_required
# def solicitar_credito():
#     return render_template('solicitar_credito.html', user=session.get("user"))

# @app.route('/processar-credito', methods=['POST'])
# @simple_auth_required
# def processar_credito():
#     try:
#         # Garantir que sempre usamos o email do usuário logado (segurança)
#         user_email = session.get("user", {}).get("email")
#         if not user_email:
#             logger.error("Erro crítico: Usuário não está logado corretamente")
#             flash('Erro: Usuário não está logado corretamente.', 'error')
#             return redirect(url_for('login'))
        
#         # Normalizar email do usuário logado
#         user_email_normalizado = normalize_email(user_email)
#         if not user_email_normalizado:
#             logger.error(f"Email do usuário logado é inválido: {user_email}")
#             flash('Erro: Email do usuário inválido. Faça login novamente.', 'error')
#             return redirect(url_for('login'))
        
#         # Log detalhado dos dados recebidos
#         logger.info(f"=== PROCESSANDO SOLICITAÇÃO ===")
#         logger.info(f"Email do usuário logado: {user_email} -> {user_email_normalizado}")
        
#         # Coleta dados do formulário (NUNCA aceitar email do formulário)
#         cliente_data = {
#             'email': user_email_normalizado,  # SEMPRE usar email normalizado da sessão
#             'nome': request.form.get('nome'),
#             'cpf': request.form.get('cpf'),
#             'curso': request.form.get('curso'),
#             'semestre': int(request.form.get('semestre')),
#             'valor_solicitado': float(request.form.get('valor_solicitado', 0)),
#             'renda_mensal': float(request.form.get('renda_mensal', 0)),
#             'score_credito': int(request.form.get('score_credito', 400)),  # Simulado
#             'pendencias_academicas': request.form.get('pendencias_academicas') == 'sim'
#         }
        
#         # Log adicional para debug
#         logger.info(f"Nome: {cliente_data.get('nome')}")
#         logger.info(f"CPF: {cliente_data.get('cpf')}")
#         logger.info(f"Email final usado: {cliente_data['email']}")
        
#         # VERIFICAÇÃO CRÍTICA: Verificar limite mensal ANTES de qualquer processamento
#         # Agora verifica tanto por email quanto por CPF
#         logger.info(f"=== VERIFICAÇÃO DE LIMITE MENSAL ===")
#         logger.info(f"Verificando limite mensal para email: {cliente_data['email']} e CPF: {cliente_data['cpf']}")
#         limite_atingido = db_manager.check_monthly_limit(cliente_data['email'], cliente_data['cpf'])
#         logger.info(f"Resultado da verificação: {'BLOQUEADO' if limite_atingido else 'PERMITIDO'}")
        
#         if limite_atingido:
#             logger.warning(f"SOLICITAÇÃO BLOQUEADA - Usuário {cliente_data['email']} / CPF {cliente_data['cpf']} já possui solicitação no mês atual")
#             flash('Você já possui uma solicitação de crédito neste mês. Aguarde o próximo mês para fazer nova solicitação.', 'error')
            
#             resultado_analise = {
#                 "aprovado": False,
#                     "criterios_atendidos": {
#                     "valor_limite": True,
#                     "score_minimo": True,
#                     "renda_suficiente": True,
#                     "sem_pendencias": True
#                 }
#             }
        
#             # Salvar no banco de dados
#             solicitacao_id = db_manager.save_solicitacao(cliente_data, resultado_analise)
            
#             if not solicitacao_id:
#                 flash('Erro ao salvar dados no banco. Tente novamente.', 'error')
#                 return redirect(url_for('solicitar_credito'))
            
#             # Prepara dados para o Logic App (usando clientName em vez de clienteId)
#             # SEMPRE enviar para Logic App, tanto para aprovados quanto reprovados (para alertas por email)
#             logic_app_payload = {
#                 "clientName": cliente_data['nome'],  # Alterado de clienteId para clientName
#                 "clientEmail": cliente_data['email'],
#                 "valorSolicitado": cliente_data['valor_solicitado'],
#                 "aprovado": resultado_analise['aprovado'],
#                 "dadosCliente": cliente_data,
#                 "resultadoAnalise": resultado_analise,
#                 "solicitacaoId": solicitacao_id,
#                 "timestamp": datetime.now().isoformat(),
#                 "tipoNotificacao": "aprovacao" if resultado_analise['aprovado'] else "reprovacao"
#             }
            
#             # Envia para Logic App (SEMPRE, independente de aprovação)
#             try:
#                 response = requests.post(
#                     LOGIC_APP_URL,
#                     json=logic_app_payload,
#                     headers={'Content-Type': 'application/json'},
#                     timeout=30
#                 )
#                 response.raise_for_status()
#                 status_msg = "aprovação" if resultado_analise['aprovado'] else "reprovação"
#                 logger.info(f"Dados de {status_msg} enviados para Logic App com sucesso - Cliente: {cliente_data['nome']} ({cliente_data['email']})")
#             except requests.exceptions.RequestException as e:
#                 logger.error(f"Erro ao enviar dados para Logic App: {str(e)}")
#                 flash('Erro na comunicação com o sistema de notificações. Dados salvos no banco.', 'warning')

#             return redirect(url_for('solicitar_credito'))
        

        
#         # Análise de crédito (permitindo fora do padrão)
#         analyzer = CreditAnalyzer()
#         resultado_analise = analyzer.analyze_credit(cliente_data, allow_out_of_pattern=True)
        
#         # Salvar no banco de dados
#         solicitacao_id = db_manager.save_solicitacao(cliente_data, resultado_analise)
        
#         if not solicitacao_id:
#             flash('Erro ao salvar dados no banco. Tente novamente.', 'error')
#             return redirect(url_for('solicitar_credito'))
        
#         # Prepara dados para o Logic App (usando clientName em vez de clienteId)
#         # SEMPRE enviar para Logic App, tanto para aprovados quanto reprovados (para alertas por email)
#         logic_app_payload = {
#             "clientName": cliente_data['nome'],  # Alterado de clienteId para clientName
#             "clientEmail": cliente_data['email'],
#             "valorSolicitado": cliente_data['valor_solicitado'],
#             "aprovado": resultado_analise['aprovado'],
#             "dadosCliente": cliente_data,
#             "resultadoAnalise": resultado_analise,
#             "solicitacaoId": solicitacao_id,
#             "timestamp": datetime.now().isoformat(),
#             "tipoNotificacao": "aprovacao" if resultado_analise['aprovado'] else "reprovacao"
#         }
        
#         # Envia para Logic App (SEMPRE, independente de aprovação)
#         try:
#             response = requests.post(
#                 LOGIC_APP_URL,
#                 json=logic_app_payload,
#                 headers={'Content-Type': 'application/json'},
#                 timeout=30
#             )
#             response.raise_for_status()
#             status_msg = "aprovação" if resultado_analise['aprovado'] else "reprovação"
#             logger.info(f"Dados de {status_msg} enviados para Logic App com sucesso - Cliente: {cliente_data['nome']} ({cliente_data['email']})")
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Erro ao enviar dados para Logic App: {str(e)}")
#             flash('Erro na comunicação com o sistema de notificações. Dados salvos no banco.', 'warning')
        
#         # Retorna resultado
#         if resultado_analise['aprovado']:
#             if resultado_analise.get('fora_padrao', False):
#                 # Aprovado mas fora do padrão - mostrar alerta
#                 alertas = resultado_analise.get('alertas', [])
#                 alertas_texto = {
#                     'valor_limite': 'Valor solicitado acima do limite padrão (R$ 5.000)',
#                     'score_minimo': 'Score de crédito abaixo do mínimo recomendado (300)',
#                     'renda_suficiente': 'Renda inferior ao dobro do valor solicitado',
#                     'sem_pendencias': 'Possui pendências acadêmicas'
#                 }
#                 mensagens_alerta = [alertas_texto.get(alerta, alerta) for alerta in alertas]
                
#                 flash(f'✅ Crédito aprovado! ⚠️ ATENÇÃO: Solicitação fora do padrão. Critérios não atendidos: {"; ".join(mensagens_alerta)}', 'warning')
#             else:
#                 flash(f'🎉 Parabéns! Seu crédito de R$ {cliente_data["valor_solicitado"]:.2f} foi aprovado!', 'success')
            
#             return render_template('resultado_aprovado.html', 
#                                  cliente=cliente_data, 
#                                  resultado=resultado_analise)
#         else:
#             motivos = resultado_analise['motivo_reprovacao']
#             flash(f'❌ Crédito não aprovado. Motivos: {", ".join(motivos)}', 'error')
#             return render_template('resultado_reprovado.html', 
#                                  cliente=cliente_data, 
#                                  resultado=resultado_analise)
                                 
#     except Exception as e:
#         logger.error(f"Erro no processamento de crédito: {str(e)}")
#         flash('Erro interno do sistema. Contate o suporte.', 'error')
#         return redirect(url_for('solicitar_credito'))

# @app.route('/health')
# def health_check():
#     """Endpoint para health check do Azure App Service"""
#     # Verificar conexão com banco
#     db_status = "ok" if db_manager.get_connection() else "error"
    
#     return jsonify({
#         'status': 'healthy' if db_status == 'ok' else 'degraded',
#         'timestamp': datetime.now().isoformat(),
#         'version': '1.0.0',
#         'database': db_status
#     })

# @app.route('/api/statistics')
# @simple_auth_required
# def get_statistics():
#     """Endpoint para estatísticas"""
#     stats = db_manager.get_statistics()
#     return jsonify(stats or {
#         'total_solicitacoes': 0,
#         'aprovados': 0,
#         'reprovados': 0,
#         'valor_total_liberado': 0
#     })

# @app.route('/init-db')
# def init_db():
#     """Endpoint para inicializar banco (apenas para desenvolvimento)"""
#     if db_manager.init_database():
#         return jsonify({'status': 'success', 'message': 'Banco inicializado com sucesso'})
#     else:
#         return jsonify({'status': 'error', 'message': 'Erro ao inicializar banco'}), 500

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     logger.error(f"Erro interno: {str(error)}")
#     return render_template('500.html'), 500

# if __name__ == '__main__':
#     # Inicializar banco de dados
#     db_manager.init_database()
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
