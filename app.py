"""
Aplicação web Flask para interface SaaS
"""
from flask import Flask, render_template, request, jsonify, send_file
from processador import ProcessadorAutomatizacao
from database import Database
import config
import os
import threading
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

# Inicializa banco de dados
try:
    db = Database()
except Exception as e:
    print(f"Erro ao inicializar banco de dados: {e}")
    db = None

# Armazena status do processamento
processamento_status = {
    'em_andamento': False,
    'progresso': 0,
    'total': 0,
    'resultados': [],
    'erro': None
}

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Página do dashboard"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"Erro ao carregar dashboard: {str(e)}", 500

@app.route('/credenciais')
def credenciais():
    """Página de gerenciamento de credenciais"""
    return render_template('credenciais.html')

@app.route('/api/processar', methods=['POST'])
def processar():
    """Endpoint para processar automação"""
    global processamento_status
    
    if processamento_status['em_andamento']:
        return jsonify({
            'success': False,
            'error': 'Processamento já em andamento'
        }), 400
    
    try:
        # Reseta status
        processamento_status = {
            'em_andamento': True,
            'progresso': 0,
            'total': 0,
            'resultados': [],
            'erro': None
        }
        
        # Processa em thread separada para não bloquear
        def processar_async():
            try:
                processador = ProcessadorAutomatizacao()
                resultados = processador.processar()
                
                relatorio = processador.gerar_relatorio_bm()
                
                # Salva todas as compras no banco de dados
                if db:
                    try:
                        for resultado in resultados:
                            db.salvar_compra(resultado)
                        
                        # Salva registro do processamento
                        db.salvar_processamento({
                            'total_processado': len(resultados),
                            'total_relevante': len(relatorio['resultados']) if relatorio else 0,
                            'status': 'concluido',
                            'bin_filtro': config.TARGET_BIN
                        })
                    except Exception as db_error:
                        print(f"Erro ao salvar no banco: {db_error}")
                
                processamento_status['resultados'] = resultados
                processamento_status['total'] = len(resultados)
                processamento_status['progresso'] = len(resultados)
                processamento_status['em_andamento'] = False
                
                processador.close()
            except Exception as e:
                processamento_status['erro'] = str(e)
                processamento_status['em_andamento'] = False
                # Salva processamento com erro
                if db:
                    try:
                        db.salvar_processamento({
                            'total_processado': processamento_status.get('progresso', 0),
                            'total_relevante': 0,
                            'status': 'erro',
                            'erro': str(e),
                            'bin_filtro': config.TARGET_BIN
                        })
                    except:
                        pass
        
        thread = threading.Thread(target=processar_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Processamento iniciado'
        })
    except Exception as e:
        processamento_status['em_andamento'] = False
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint para verificar status do processamento"""
    return jsonify(processamento_status)

@app.route('/api/resultados', methods=['GET'])
def resultados():
    """Endpoint para obter resultados"""
    relatorio = None
    if processamento_status['resultados']:
        processador = ProcessadorAutomatizacao()
        relatorio = processador.gerar_relatorio_bm(processamento_status['resultados'])
    
    return jsonify({
        'success': True,
        'total_processado': len(processamento_status['resultados']),
        'total_relevante': len(relatorio['resultados']) if relatorio else 0,
        'resultados': processamento_status['resultados'],
        'relatorio': relatorio
    })

@app.route('/api/relatorio', methods=['GET'])
def obter_relatorio():
    """Endpoint para obter relatório formatado"""
    try:
        formato = request.args.get('formato', 'json')
        
        if not processamento_status['resultados']:
            return jsonify({'error': 'Nenhum resultado disponível. Execute o processamento primeiro.'}), 400
        
        processador = ProcessadorAutomatizacao()
        relatorio = processador.gerar_relatorio_bm(processamento_status['resultados'])
        
        if not relatorio:
            return jsonify({'error': 'Nenhum resultado relevante para gerar relatório'}), 400
        
        arquivo = processador.salvar_relatorio(formato=formato)
        
        if arquivo and os.path.exists(arquivo):
            return send_file(arquivo, as_attachment=True)
        else:
            return jsonify({'error': 'Erro ao gerar relatório'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/estatisticas', methods=['GET'])
def cache_estatisticas():
    """Endpoint para obter estatísticas do cache"""
    try:
        from cache_manager import CacheManager
        cache = CacheManager()
        stats = cache.estatisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/limpar', methods=['POST'])
def limpar_cache():
    """Endpoint para limpar o cache"""
    try:
        from cache_manager import CacheManager
        cache = CacheManager()
        cache.limpar_cache()
        return jsonify({'success': True, 'message': 'Cache limpo com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DO DASHBOARD ==========

@app.route('/api/dashboard/estatisticas', methods=['GET'])
def dashboard_estatisticas():
    """Endpoint para obter estatísticas do dashboard"""
    try:
        if db is None:
            return jsonify({'error': 'Banco de dados não inicializado'}), 500
        stats = db.obter_estatisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/compras', methods=['GET'])
def dashboard_compras():
    """Endpoint para buscar compras com filtros e paginação"""
    try:
        if db is None:
            return jsonify({'error': 'Banco de dados não inicializado'}), 500
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        # Constrói filtros
        filtros = {}
        if request.args.get('cpf'):
            filtros['cpf'] = request.args.get('cpf')
        if request.args.get('nome'):
            filtros['nome'] = request.args.get('nome')
        if request.args.get('numero'):
            filtros['numero'] = request.args.get('numero')
        if request.args.get('operadora'):
            filtros['operadora'] = request.args.get('operadora')
        if request.args.get('is_target') == 'true':
            filtros['is_target'] = True
        if request.args.get('disponivel') == 'true':
            filtros['disponivel'] = True
        
        compras = db.buscar_compras(filtros=filtros, limit=limit, offset=offset)
        total = db.contar_compras(filtros=filtros)
        
        return jsonify({
            'success': True,
            'compras': compras,
            'total': total,
            'page': page,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/exportar', methods=['GET'])
def dashboard_exportar():
    """Endpoint para exportar compras em CSV"""
    try:
        # Constrói filtros
        filtros = {}
        if request.args.get('cpf'):
            filtros['cpf'] = request.args.get('cpf')
        if request.args.get('nome'):
            filtros['nome'] = request.args.get('nome')
        if request.args.get('numero'):
            filtros['numero'] = request.args.get('numero')
        if request.args.get('operadora'):
            filtros['operadora'] = request.args.get('operadora')
        if request.args.get('is_target') == 'true':
            filtros['is_target'] = True
        if request.args.get('disponivel') == 'true':
            filtros['disponivel'] = True
        
        # Busca todas as compras (sem limite)
        compras = db.buscar_compras(filtros=filtros, limit=10000, offset=0)
        
        # Cria CSV em memória
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'id', 'cpf', 'nome', 'bin', 'numero', 'operadora', 
            'is_target', 'disponivel', 'status', 'data_consulta', 'data_atualizacao'
        ])
        writer.writeheader()
        
        for compra in compras:
            writer.writerow({
                'id': compra['id'],
                'cpf': compra['cpf'],
                'nome': compra['nome'],
                'bin': compra['bin'],
                'numero': compra['numero'] or '',
                'operadora': compra['operadora'] or '',
                'is_target': 'Sim' if compra['is_target'] else 'Não',
                'disponivel': 'Sim' if compra['disponivel'] else 'Não',
                'status': compra['status'],
                'data_consulta': compra['data_consulta'],
                'data_atualizacao': compra['data_atualizacao']
            })
        
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compras_export_{timestamp}.csv"
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/compras/<int:compra_id>', methods=['GET'])
def dashboard_compra_detalhes(compra_id):
    """Endpoint para obter detalhes de uma compra específica"""
    try:
        compras = db.buscar_compras(filtros={'id': compra_id}, limit=1)
        if compras:
            return jsonify({'success': True, 'compra': compras[0]})
        else:
            return jsonify({'error': 'Compra não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/compras/<int:compra_id>/observacoes', methods=['POST'])
def dashboard_compra_observacoes(compra_id):
    """Endpoint para atualizar observações de uma compra"""
    try:
        data = request.get_json()
        observacoes = data.get('observacoes', '')
        db.atualizar_observacoes(compra_id, observacoes)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/processamentos', methods=['GET'])
def dashboard_processamentos():
    """Endpoint para obter histórico de processamentos"""
    try:
        limit = int(request.args.get('limit', 50))
        processamentos = db.buscar_processamentos(limit=limit)
        return jsonify({'success': True, 'processamentos': processamentos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE CREDENCIAIS ==========

@app.route('/api/credenciais', methods=['GET'])
def obter_credenciais():
    """Endpoint para obter todas as credenciais"""
    try:
        from credentials_manager import CredentialsManager
        cred_manager = CredentialsManager()
        creds = cred_manager.get_credentials()
        return jsonify({'success': True, 'credentials': creds})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/credenciais/dbfusion', methods=['POST'])
def atualizar_dbfusion():
    """Endpoint para atualizar credenciais do DBFusion"""
    try:
        from credentials_manager import CredentialsManager
        data = request.get_json()
        
        cred_manager = CredentialsManager()
        success = cred_manager.update_dbfusion_credentials(
            url=data.get('url'),
            user=data.get('user'),
            password=data.get('password')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Credenciais do DBFusion atualizadas'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar credenciais'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/credenciais/spyhub', methods=['POST'])
def atualizar_spyhub():
    """Endpoint para atualizar credenciais do SpyHub"""
    try:
        from credentials_manager import CredentialsManager
        data = request.get_json()
        
        cred_manager = CredentialsManager()
        success = cred_manager.update_spyhub_credentials(
            url=data.get('url'),
            user=data.get('user'),
            password=data.get('password')
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Credenciais do SpyHub atualizadas'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar credenciais'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/credenciais/dbfusion/test', methods=['POST'])
def testar_dbfusion():
    """Endpoint para testar credenciais do DBFusion"""
    try:
        from credentials_manager import CredentialsManager
        cred_manager = CredentialsManager()
        result = cred_manager.test_dbfusion_credentials()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/credenciais/spyhub/test', methods=['POST'])
def testar_spyhub():
    """Endpoint para testar credenciais do SpyHub"""
    try:
        from credentials_manager import CredentialsManager
        cred_manager = CredentialsManager()
        result = cred_manager.test_spyhub_credentials()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

