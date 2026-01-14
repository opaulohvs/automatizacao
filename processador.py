"""
Processador principal que orquestra todo o fluxo de automação
"""
import config
from dbfusion_client import DBFusionClient
from spyhub_client import SpyHubClient
from operadora_checker import OperadoraChecker
from cache_manager import CacheManager
import json
import re
from datetime import datetime


class ProcessadorAutomatizacao:
    def __init__(self):
        self.dbfusion = DBFusionClient()
        self.spyhub = SpyHubClient()
        self.operadora_checker = OperadoraChecker()
        self.cache = CacheManager()
        self.resultados = []
    
    def __del__(self):
        """Garante que os drivers sejam fechados"""
        try:
            if hasattr(self, 'dbfusion'):
                self.dbfusion.close()
            if hasattr(self, 'spyhub'):
                self.spyhub.close()
            if hasattr(self, 'operadora_checker'):
                self.operadora_checker.close()
        except:
            pass
    
    def close(self):
        """Fecha todas as conexões"""
        try:
            self.dbfusion.close()
            self.spyhub.close()
            self.operadora_checker.close()
        except:
            pass
    
    def processar(self):
        """
        Processa todas as pessoas da base de dados filtradas por BIN
        """
        print("Iniciando processamento...")
        print(f"Buscando pessoas com BIN: {config.TARGET_BIN}")
        
        # 1. Buscar pessoas da base de dados (limite de 10 para teste)
        pessoas = self.dbfusion.get_pessoas_by_bin(config.TARGET_BIN, limit=10)
        
        if not pessoas:
            print("Nenhuma pessoa encontrada com o BIN especificado.")
            return []
        
        print(f"Encontradas {len(pessoas)} pessoas. Iniciando processamento...")
        
        # 2. Para cada pessoa, consultar número e operadora
        resultados = []
        for idx, pessoa in enumerate(pessoas, 1):
            cpf = pessoa.get('cpf') or pessoa.get('CPF')
            if not cpf:
                print(f"Pessoa {idx}: CPF não encontrado, pulando...")
                continue
            
            print(f"\nProcessando pessoa {idx}/{len(pessoas)} - CPF: {cpf}")
            
            # Verifica se já está no cache
            resultado_cache = self.cache.obter_resultado(cpf)
            if resultado_cache:
                print(f"  ✓ CPF encontrado no cache (consultado em: {resultado_cache.get('data_cache', 'N/A')})")
                resultado = resultado_cache.copy()
                resultado['status'] = 'concluido'
                resultado['timestamp'] = datetime.now().isoformat()
                resultados.append(resultado)
                continue
            
            resultado = {
                'cpf': cpf,
                'nome': pessoa.get('nome') or pessoa.get('NOME', 'N/A'),
                'bin': pessoa.get('bin') or config.TARGET_BIN,
                'numero': None,
                'operadora': None,
                'is_target': False,
                'disponivel': False,
                'status': 'processando',
                'timestamp': datetime.now().isoformat(),
                'do_cache': False
            }
            
            # 3. Consultar números via SpyHub (CONSULTA TRACKER)
            print(f"  Consultando números no SpyHub (CONSULTA TRACKER)...")
            numeros_movels = self.spyhub.consultar_numeros_por_cpf(cpf)
            
            if numeros_movels and len(numeros_movels) > 0:
                print(f"  {len(numeros_movels)} número(s) móvel(is) encontrado(s)")
                
                # 4. Para cada número móvel, consultar operadora no consultaoperadora.com.br
                for idx_numero, numero in enumerate(numeros_movels, 1):
                    print(f"\n  Processando número {idx_numero}/{len(numeros_movels)}: {numero}")
                    
                    # Remove formatação para consulta
                    numero_limpo = re.sub(r'[^\d]', '', numero) if numero else ''
                    
                    if not numero_limpo or len(numero_limpo) != 11:
                        print(f"    ⚠ Número inválido: {numero}")
                        continue
                    
                    # Verifica se é número móvel (começa com 9 após DDD)
                    if numero_limpo[2] != '9':
                        print(f"    ⚠ Número não é móvel (não começa com 9 após DDD)")
                        continue
                    
                    # Consulta operadora no site consultaoperadora.com.br
                    print(f"    Consultando operadora no site consultaoperadora.com.br...")
                    operadora = self.operadora_checker.verificar_operadora(numero_limpo)
                    
                    if operadora:
                        print(f"    ✓ Operadora encontrada: {operadora}")
                        resultado['operadora'] = operadora
                        resultado['is_target'] = self.operadora_checker.is_target_operadora(operadora)
                        print(f"    Operadora: {operadora} {'(TARGET)' if resultado['is_target'] else ''}")
                        
                        # 5. Verificar disponibilidade
                        if resultado['is_target']:
                            resultado['disponivel'] = self.operadora_checker.verificar_disponibilidade(numero_limpo, operadora)
                            print(f"    Disponível para compra: {resultado['disponivel']}")
                        
                        # Salva informações do número no resultado
                        resultado['numero'] = numero_limpo
                        resultado['status'] = 'concluido'
                        
                        # Se encontrou operadora TIM ou ALGAR, marca como resultado relevante
                        if resultado['is_target']:
                            print(f"    ✓ Número {numero} ({operadora}) é TIM/ALGAR!")
                            # Adiciona aos resultados e para de processar (encontrou um TIM/Algar)
                            resultados.append(resultado.copy())
                            # Salva no cache
                            self.cache.salvar_resultado(cpf, resultado.copy())
                            break
                        else:
                            # Se não é TIM/Algar, continua procurando nos outros números
                            print(f"    Número {numero} ({operadora}) não é TIM/ALGAR, continuando...")
                            continue
                    else:
                        print(f"    ⚠ Operadora não identificada para número {numero}")
                
                # Se nenhum número TIM/Algar foi encontrado, salva o primeiro número encontrado (para histórico)
                if not any(r.get('is_target') and r.get('cpf') == cpf for r in resultados):
                    primeiro_numero = re.sub(r'[^\d]', '', numeros_movels[0]) if numeros_movels else None
                    if primeiro_numero:
                        resultado['numero'] = primeiro_numero
                        resultado['status'] = 'concluido'
                        resultados.append(resultado.copy())
                        print(f"  Nenhum TIM/Algar encontrado. Salvando primeiro número encontrado para histórico.")
                        # Salva no cache
                        self.cache.salvar_resultado(cpf, resultado.copy())
            else:
                print(f"  Nenhum número móvel encontrado")
                resultado['status'] = 'concluido'
                resultados.append(resultado)
                # Salva no cache
                self.cache.salvar_resultado(cpf, resultado)
        
        self.resultados = resultados
        return resultados
    
    def gerar_relatorio_bm(self, resultados=None):
        """
        Gera relatório formatado para BM
        """
        if resultados is None:
            resultados = self.resultados
        
        if not resultados:
            return None
        
        # Filtra apenas resultados relevantes (TIM ou Algar disponíveis)
        resultados_filtrados = [
            r for r in resultados 
            if r.get('is_target') and r.get('disponivel') and r.get('numero')
        ]
        
        relatorio = {
            'data_geracao': datetime.now().isoformat(),
            'bin_filtro': config.TARGET_BIN,
            'total_processado': len(resultados),
            'total_relevante': len(resultados_filtrados),
            'resultados': resultados_filtrados
        }
        
        return relatorio
    
    def salvar_relatorio(self, formato='json', arquivo=None):
        """
        Salva relatório em arquivo
        """
        relatorio = self.gerar_relatorio_bm()
        
        if not relatorio:
            print("Nenhum resultado para salvar.")
            return None
        
        if not arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"relatorio_bm_{timestamp}.{formato}"
        
        if formato == 'json':
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, ensure_ascii=False, indent=2)
        elif formato == 'csv':
            import csv
            with open(arquivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['cpf', 'nome', 'numero', 'operadora', 'disponivel'])
                writer.writeheader()
                for r in relatorio['resultados']:
                    writer.writerow({
                        'cpf': r['cpf'],
                        'nome': r['nome'],
                        'numero': r['numero'],
                        'operadora': r['operadora'],
                        'disponivel': r['disponivel']
                    })
        
        print(f"Relatório salvo em: {arquivo}")
        return arquivo

