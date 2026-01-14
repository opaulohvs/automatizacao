"""
Sistema de banco de dados para armazenar informações de compra
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class Database:
    def __init__(self, db_path='compras.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Cria conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de compras/consultas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL,
                nome TEXT,
                bin TEXT,
                numero TEXT,
                operadora TEXT,
                is_target INTEGER DEFAULT 0,
                disponivel INTEGER DEFAULT 0,
                comprado INTEGER DEFAULT 0,
                status TEXT DEFAULT 'concluido',
                data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_compra TIMESTAMP,
                do_cache INTEGER DEFAULT 0,
                observacoes TEXT,
                UNIQUE(cpf, numero)
            )
        ''')
        
        # Adicionar coluna comprado se não existir (para bancos já criados)
        try:
            cursor.execute('ALTER TABLE compras ADD COLUMN comprado INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Adicionar coluna data_compra se não existir
        try:
            cursor.execute('ALTER TABLE compras ADD COLUMN data_compra TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Tabela de processamentos (histórico de execuções)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_fim TIMESTAMP,
                total_processado INTEGER DEFAULT 0,
                total_relevante INTEGER DEFAULT 0,
                status TEXT DEFAULT 'concluido',
                erro TEXT,
                bin_filtro TEXT
            )
        ''')
        
        # Tabela de estatísticas diárias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estatisticas_diarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE UNIQUE,
                total_consultas INTEGER DEFAULT 0,
                total_tim_algar INTEGER DEFAULT 0,
                total_disponiveis INTEGER DEFAULT 0,
                total_processamentos INTEGER DEFAULT 0
            )
        ''')
        
        # Índices para melhor performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cpf ON compras(cpf)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_numero ON compras(numero)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operadora ON compras(operadora)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_consulta ON compras(data_consulta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_target ON compras(is_target)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_disponivel ON compras(disponivel)')
        
        conn.commit()
        conn.close()
    
    def salvar_compra(self, dados: Dict) -> int:
        """
        Salva ou atualiza uma compra/consulta no banco
        Retorna o ID do registro
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verifica se já existe
        cursor.execute('''
            SELECT id FROM compras 
            WHERE cpf = ? AND (numero = ? OR (numero IS NULL AND ? IS NULL))
        ''', (dados.get('cpf'), dados.get('numero'), dados.get('numero')))
        
        existing = cursor.fetchone()
        
        if existing:
            # Atualiza registro existente (não altera comprado se já estiver marcado)
            cursor.execute('''
                UPDATE compras SET
                    nome = ?,
                    bin = ?,
                    numero = ?,
                    operadora = ?,
                    is_target = ?,
                    disponivel = ?,
                    status = ?,
                    data_atualizacao = CURRENT_TIMESTAMP,
                    do_cache = ?
                WHERE id = ?
            ''', (
                dados.get('nome'),
                dados.get('bin'),
                dados.get('numero'),
                dados.get('operadora'),
                1 if dados.get('is_target') else 0,
                1 if dados.get('disponivel') else 0,
                dados.get('status', 'concluido'),
                1 if dados.get('do_cache') else 0,
                existing['id']
            ))
            compra_id = existing['id']
        else:
            # Insere novo registro (comprado = 0 por padrão, pois é apenas consulta)
            cursor.execute('''
                INSERT INTO compras (
                    cpf, nome, bin, numero, operadora, 
                    is_target, disponivel, comprado, status, do_cache
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados.get('cpf'),
                dados.get('nome'),
                dados.get('bin'),
                dados.get('numero'),
                dados.get('operadora'),
                1 if dados.get('is_target') else 0,
                1 if dados.get('disponivel') else 0,
                1 if dados.get('comprado') else 0,  # Por padrão, não é compra real
                dados.get('status', 'concluido'),
                1 if dados.get('do_cache') else 0
            ))
            compra_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return compra_id
    
    def salvar_processamento(self, dados: Dict) -> int:
        """
        Salva um registro de processamento
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO processamentos (
                data_fim, total_processado, total_relevante, 
                status, erro, bin_filtro
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('data_fim', datetime.now().isoformat()),
            dados.get('total_processado', 0),
            dados.get('total_relevante', 0),
            dados.get('status', 'concluido'),
            dados.get('erro'),
            dados.get('bin_filtro')
        ))
        
        processamento_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return processamento_id
    
    def buscar_compras(self, 
                     filtros: Optional[Dict] = None,
                     limit: int = 100,
                     offset: int = 0,
                     order_by: str = 'data_consulta DESC') -> List[Dict]:
        """
        Busca compras com filtros opcionais
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Por padrão, mostrar apenas compras reais (comprado = 1)
        # Se não especificar filtro de comprado, filtra apenas compras reais
        query = 'SELECT * FROM compras WHERE comprado = 1'
        params = []
        
        if filtros:
            # Se especificar explicitamente comprado, usar o filtro
            if 'comprado' in filtros:
                query = 'SELECT * FROM compras WHERE comprado = ?'
                params.append(1 if filtros['comprado'] else 0)
            # Se especificar mostrar_todos ou incluir_consultas, mostrar tudo
            if filtros.get('mostrar_todos') or filtros.get('incluir_consultas'):
                query = 'SELECT * FROM compras WHERE 1=1'
                params = []
            if filtros.get('id'):
                query += ' AND id = ?'
                params.append(filtros['id'])
            
            if filtros.get('cpf'):
                query += ' AND cpf LIKE ?'
                params.append(f"%{filtros['cpf']}%")
            
            if filtros.get('nome'):
                query += ' AND nome LIKE ?'
                params.append(f"%{filtros['nome']}%")
            
            if filtros.get('numero'):
                query += ' AND numero LIKE ?'
                params.append(f"%{filtros['numero']}%")
            
            if filtros.get('operadora'):
                query += ' AND operadora = ?'
                params.append(filtros['operadora'])
            
            if filtros.get('is_target') is not None:
                query += ' AND is_target = ?'
                params.append(1 if filtros['is_target'] else 0)
            
            if filtros.get('disponivel') is not None:
                query += ' AND disponivel = ?'
                params.append(1 if filtros['disponivel'] else 0)
            
            if filtros.get('data_inicio'):
                query += ' AND DATE(data_consulta) >= ?'
                params.append(filtros['data_inicio'])
            
            if filtros.get('data_fim'):
                query += ' AND DATE(data_consulta) <= ?'
                params.append(filtros['data_fim'])
        
        query += f' ORDER BY {order_by} LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        compras = []
        for row in rows:
            compras.append({
                'id': row['id'],
                'cpf': row['cpf'],
                'nome': row['nome'],
                'bin': row['bin'],
                'numero': row['numero'],
                'operadora': row['operadora'],
                'is_target': bool(row['is_target']),
                'disponivel': bool(row['disponivel']),
                'comprado': bool(row.get('comprado', 0)),
                'status': row['status'],
                'data_consulta': row['data_consulta'],
                'data_atualizacao': row['data_atualizacao'],
                'data_compra': row.get('data_compra'),
                'do_cache': bool(row['do_cache']),
                'observacoes': row['observacoes']
            })
        
        conn.close()
        return compras
    
    def contar_compras(self, filtros: Optional[Dict] = None) -> int:
        """Conta total de compras com filtros"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Por padrão, contar apenas compras reais
        query = 'SELECT COUNT(*) as total FROM compras WHERE comprado = 1'
        params = []
        
        if filtros:
            # Se especificar mostrar_todos ou incluir_consultas, contar tudo
            if filtros.get('mostrar_todos') or filtros.get('incluir_consultas'):
                query = 'SELECT COUNT(*) as total FROM compras WHERE 1=1'
                params = []
            elif 'comprado' in filtros:
                query = 'SELECT COUNT(*) as total FROM compras WHERE comprado = ?'
                params = [1 if filtros['comprado'] else 0]
            
            if filtros.get('id'):
                query += ' AND id = ?'
                params.append(filtros['id'])
            
            if filtros.get('cpf'):
                query += ' AND cpf LIKE ?'
                params.append(f"%{filtros['cpf']}%")
            
            if filtros.get('nome'):
                query += ' AND nome LIKE ?'
                params.append(f"%{filtros['nome']}%")
            
            if filtros.get('numero'):
                query += ' AND numero LIKE ?'
                params.append(f"%{filtros['numero']}%")
            
            if filtros.get('operadora'):
                query += ' AND operadora = ?'
                params.append(filtros['operadora'])
            
            if filtros.get('is_target') is not None:
                query += ' AND is_target = ?'
                params.append(1 if filtros['is_target'] else 0)
            
            if filtros.get('disponivel') is not None:
                query += ' AND disponivel = ?'
                params.append(1 if filtros['disponivel'] else 0)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result['total'] if result else 0
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas gerais"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de compras (apenas compras reais, comprado = 1)
        cursor.execute('SELECT COUNT(*) as total FROM compras WHERE comprado = 1')
        stats['total_compras'] = cursor.fetchone()['total']
        
        # Total com número (apenas compras reais)
        cursor.execute('SELECT COUNT(*) as total FROM compras WHERE comprado = 1 AND numero IS NOT NULL')
        stats['total_com_numero'] = cursor.fetchone()['total']
        
        # Total TIM/Algar (apenas compras reais)
        cursor.execute('SELECT COUNT(*) as total FROM compras WHERE comprado = 1 AND is_target = 1')
        stats['total_tim_algar'] = cursor.fetchone()['total']
        
        # Total disponíveis (apenas compras reais)
        cursor.execute('SELECT COUNT(*) as total FROM compras WHERE comprado = 1 AND disponivel = 1')
        stats['total_disponiveis'] = cursor.fetchone()['total']
        
        # Por operadora (apenas compras reais)
        cursor.execute('''
            SELECT operadora, COUNT(*) as total 
            FROM compras 
            WHERE comprado = 1 AND operadora IS NOT NULL 
            GROUP BY operadora 
            ORDER BY total DESC
        ''')
        stats['por_operadora'] = {row['operadora']: row['total'] for row in cursor.fetchall()}
        
        # Últimos 7 dias (apenas compras reais, usar data_compra se disponível, senão data_consulta)
        cursor.execute('''
            SELECT DATE(COALESCE(data_compra, data_consulta)) as data, COUNT(*) as total
            FROM compras
            WHERE comprado = 1 AND (data_compra >= datetime('now', '-7 days') OR (data_compra IS NULL AND data_consulta >= datetime('now', '-7 days')))
            GROUP BY DATE(COALESCE(data_compra, data_consulta))
            ORDER BY data DESC
        ''')
        stats['ultimos_7_dias'] = [
            {'data': row['data'], 'total': row['total']} 
            for row in cursor.fetchall()
        ]
        
        # Processamentos
        cursor.execute('SELECT COUNT(*) as total FROM processamentos')
        stats['total_processamentos'] = cursor.fetchone()['total']
        
        conn.close()
        return stats
    
    def buscar_processamentos(self, limit: int = 50) -> List[Dict]:
        """Busca histórico de processamentos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM processamentos 
            ORDER BY data_inicio DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        processamentos = []
        for row in rows:
            processamentos.append({
                'id': row['id'],
                'data_inicio': row['data_inicio'],
                'data_fim': row['data_fim'],
                'total_processado': row['total_processado'],
                'total_relevante': row['total_relevante'],
                'status': row['status'],
                'erro': row['erro'],
                'bin_filtro': row['bin_filtro']
            })
        
        conn.close()
        return processamentos
    
    def atualizar_observacoes(self, compra_id: int, observacoes: str):
        """Atualiza observações de uma compra"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE compras SET observacoes = ? WHERE id = ?
        ''', (observacoes, compra_id))
        
        conn.commit()
        conn.close()
    
    def deletar_compra(self, compra_id: int):
        """Deleta uma compra"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM compras WHERE id = ?', (compra_id,))
        
        conn.commit()
        conn.close()
    
    def marcar_como_comprado(self, compra_id: int):
        """Marca uma compra como realmente comprada"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE compras SET 
                comprado = 1,
                data_compra = CURRENT_TIMESTAMP,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (compra_id,))
        
        conn.commit()
        conn.close()

