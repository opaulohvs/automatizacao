"""
Gerenciador de cache para evitar consultas repetidas
"""
import json
import os
from datetime import datetime
from pathlib import Path


class CacheManager:
    def __init__(self, cache_file='cache_consultas.json'):
        self.cache_file = cache_file
        self.cache = self._carregar_cache()
    
    def _carregar_cache(self):
        """Carrega cache do arquivo"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    print(f"Cache carregado: {len(cache)} registros encontrados")
                    return cache
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")
                return {}
        return {}
    
    def _salvar_cache(self):
        """Salva cache no arquivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def tem_cpf(self, cpf):
        """Verifica se CPF já está no cache"""
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        return cpf_limpo in self.cache
    
    def obter_resultado(self, cpf):
        """Obtém resultado do cache"""
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        if cpf_limpo in self.cache:
            resultado = self.cache[cpf_limpo].copy()
            resultado['do_cache'] = True
            resultado['data_cache'] = self.cache[cpf_limpo].get('data_consulta', 'N/A')
            return resultado
        return None
    
    def salvar_resultado(self, cpf, resultado):
        """Salva resultado no cache"""
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        
        resultado_cache = {
            'cpf': cpf_limpo,
            'numero': resultado.get('numero'),
            'operadora': resultado.get('operadora'),
            'is_target': resultado.get('is_target', False),
            'disponivel': resultado.get('disponivel', False),
            'nome': resultado.get('nome'),
            'data_consulta': datetime.now().isoformat(),
            'bin': resultado.get('bin')
        }
        
        self.cache[cpf_limpo] = resultado_cache
        self._salvar_cache()
    
    def limpar_cache(self):
        """Limpa todo o cache"""
        self.cache = {}
        self._salvar_cache()
        print("Cache limpo!")
    
    def estatisticas(self):
        """Retorna estatísticas do cache"""
        total = len(self.cache)
        com_numero = sum(1 for r in self.cache.values() if r.get('numero'))
        tim_algar = sum(1 for r in self.cache.values() 
                       if r.get('is_target') and r.get('disponivel'))
        
        return {
            'total': total,
            'com_numero': com_numero,
            'tim_algar_disponivel': tim_algar
        }
    
    def exportar_cache(self, arquivo='cache_backup.json'):
        """Exporta cache para backup"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            print(f"Cache exportado para: {arquivo}")
            return True
        except Exception as e:
            print(f"Erro ao exportar cache: {e}")
            return False


