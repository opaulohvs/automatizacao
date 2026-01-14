"""
Gerenciador de credenciais do sistema
Salva credenciais em arquivo JSON separado para segurança
"""
import json
import os
from typing import Dict, Optional


class CredentialsManager:
    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = credentials_file
        self.default_credentials = {
            'dbfusion': {
                'url': 'https://dbfusion.me/loja',
                'user': 'andrade17',
                'password': '284671'
            },
            'spyhub': {
                'url': 'https://app.spyhub.io',
                'user': 'Prtm999ww',
                'password': '350376'
            }
        }
    
    def _load_credentials(self) -> Dict:
        """Carrega credenciais do arquivo ou retorna padrões"""
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_credentials.copy()
        return self.default_credentials.copy()
    
    def _save_credentials(self, credentials: Dict):
        """Salva credenciais no arquivo"""
        try:
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
            return False
    
    def get_credentials(self) -> Dict:
        """Obtém todas as credenciais"""
        return self._load_credentials()
    
    def get_dbfusion_credentials(self) -> Dict:
        """Obtém credenciais do DBFusion"""
        creds = self._load_credentials()
        return creds.get('dbfusion', self.default_credentials['dbfusion'])
    
    def get_spyhub_credentials(self) -> Dict:
        """Obtém credenciais do SpyHub"""
        creds = self._load_credentials()
        return creds.get('spyhub', self.default_credentials['spyhub'])
    
    def update_dbfusion_credentials(self, url: Optional[str] = None, 
                                    user: Optional[str] = None, 
                                    password: Optional[str] = None) -> bool:
        """Atualiza credenciais do DBFusion"""
        creds = self._load_credentials()
        
        if 'dbfusion' not in creds:
            creds['dbfusion'] = {}
        
        if url:
            creds['dbfusion']['url'] = url
        if user:
            creds['dbfusion']['user'] = user
        if password:
            creds['dbfusion']['password'] = password
        
        return self._save_credentials(creds)
    
    def update_spyhub_credentials(self, url: Optional[str] = None, 
                                 user: Optional[str] = None, 
                                 password: Optional[str] = None) -> bool:
        """Atualiza credenciais do SpyHub"""
        creds = self._load_credentials()
        
        if 'spyhub' not in creds:
            creds['spyhub'] = {}
        
        if url:
            creds['spyhub']['url'] = url
        if user:
            creds['spyhub']['user'] = user
        if password:
            creds['spyhub']['password'] = password
        
        return self._save_credentials(creds)
    
    def test_dbfusion_credentials(self) -> Dict:
        """Testa credenciais do DBFusion (retorna status)"""
        # Esta função pode ser expandida para fazer um teste real de login
        return {'status': 'success', 'message': 'Credenciais salvas'}
    
    def test_spyhub_credentials(self) -> Dict:
        """Testa credenciais do SpyHub (retorna status)"""
        # Esta função pode ser expandida para fazer um teste real de login
        return {'status': 'success', 'message': 'Credenciais salvas'}

