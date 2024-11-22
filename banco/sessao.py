import uuid
from datetime import datetime, timedelta
from banco.supabase_client import SupabaseClient

SUPABASE_URL = "https://xagqlcyceoxyghihtzru.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhZ3FsY3ljZW94eWdoaWh0enJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MzY2NzcsImV4cCI6MjA0NjQxMjY3N30._nBRoD4m-RzhTtB8fFrmsIykVeTLT2wz5uYVLm44E3A"

supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)

from functools import lru_cache
import requests
from typing import Optional, Literal, Dict, Any

TipoUsuario = Literal["usuario", "profissional"]

async def registrar_acesso(id_usuario: int, tipo_usuario: TipoUsuario, ip_usuario: Optional[str] = None) -> Optional[int]:
    try:
        if not ip_usuario:
            ip_usuario = "Não disponível"

        dados_acesso = {
            "data_acesso": datetime.now().isoformat(),
            "ip_usuario": ip_usuario
        }

        if tipo_usuario == "usuario":
            dados_acesso["id_pessoa"] = id_usuario
            resultado = supabase.table('logs_acessos_pessoas').insert(dados_acesso).execute()
        else:
            dados_acesso["id_profissional"] = id_usuario
            resultado = supabase.table('logs_acessos_profissionais').insert(dados_acesso).execute()

        return resultado.data[0]['id_log'] if resultado.data else None

    except Exception as e:
        print(f"Erro ao registrar acesso: {str(e)}")
        return None

@lru_cache(maxsize=128)
async def verificar_sessao_ativa(id_usuario: int, tipo_usuario: TipoUsuario) -> bool:
    try:
        limite_tempo = (datetime.now() - timedelta(hours=24)).isoformat()
        
        if tipo_usuario == "usuario":
            tabela = 'logs_acessos_pessoas'
            campo_id = 'id_pessoa'
        else:
            tabela = 'logs_acessos_profissionais'
            campo_id = 'id_profissional'

        resultado = supabase.table(tabela)\
            .select('id_log')\
            .eq(campo_id, id_usuario)\
            .gt('data_acesso', limite_tempo)\
            .limit(1)\
            .execute()
        
        return len(resultado.data) > 0

    except Exception as e:
        print(f"Erro ao verificar sessão: {str(e)}")
        return False

async def obter_tipo_usuario(id_usuario: int) -> Optional[TipoUsuario]:
    try:
        resultado = supabase.table('pessoas')\
            .select('id_pessoa')\
            .eq('id_pessoa', id_usuario)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            return "usuario"
        
        resultado = supabase.table('profissionais')\
            .select('id_profissional')\
            .eq('id_profissional', id_usuario)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            return "profissional"
        
        return None

    except Exception as e:
        print(f"Erro ao obter tipo de usuário: {str(e)}")
        return None

def criar_token_sessao() -> str:
    return str(uuid.uuid4())

async def obter_ipv6() -> Optional[str]:
    try:
        response = requests.get('https://api64.ipify.org', timeout=5)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao obter IPv6: {str(e)}")
        try:
            response = requests.get('https://v6.ident.me', timeout=5)
            return response.text.strip()
        except Exception as e:
            print(f"Erro ao obter IPv6 (método alternativo): {str(e)}")
            return None

async def obter_dados_usuario(id_usuario: int, tipo_usuario: TipoUsuario) -> Optional[Dict[str, Any]]:
    try:
        if tipo_usuario == "usuario":
            resultado = supabase.table('pessoas')\
                .select('*')\
                .eq('id_pessoa', id_usuario)\
                .limit(1)\
                .execute()
        else:
            resultado = supabase.table('profissionais')\
                .select('*')\
                .eq('id_profissional', id_usuario)\
                .limit(1)\
                .execute()

        return resultado.data[0] if resultado.data else None

    except Exception as e:
        print(f"Erro ao obter dados do usuário: {str(e)}")
        return None

async def verificar_credenciais(telefone: str, senha: str) -> Optional[tuple[int, TipoUsuario]]:
    try:
        resultado = supabase.table('pessoas')\
            .select('id_pessoa, senha')\
            .eq('telefone', telefone)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            usuario = resultado.data[0]
            if usuario['senha'] == senha:
                return (usuario['id_pessoa'], "usuario")
        
        resultado = supabase.table('profissionais')\
            .select('id_profissional, senha')\
            .eq('telefone', telefone)\
            .limit(1)\
            .execute()
        
        if resultado.data:
            profissional = resultado.data[0]
            if profissional['senha'] == senha:
                return (profissional['id_profissional'], "profissional")
        
        return None

    except Exception as e:
        print(f"Erro ao verificar credenciais: {str(e)}")
        return None