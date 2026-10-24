import os
import secrets
import logging
import hmac
from typing import Optional

logger = logging.getLogger("streamdeck.auth")

DEFAULT_INSECURE_TOKEN = "mi9_deck_secret_2026"

def _get_dotenv_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

def _persist_token_to_dotenv(token: str) -> None:
    env_path = _get_dotenv_path()
    try:
        if os.path.isfile(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            token_found = False
            new_lines = []
            for line in lines:
                if line.strip().startswith("AUTH_TOKEN="):
                    new_lines.append(f"AUTH_TOKEN={token}\n")
                    token_found = True
                else:
                    new_lines.append(line)

            if not token_found:
                new_lines.append(f"\nAUTH_TOKEN={token}\n")

            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        else:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"AUTH_TOKEN={token}\nHOST=0.0.0.0\nPORT=8000\n")
        logger.info("AUTH_TOKEN persistido no arquivo .env com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao persistir AUTH_TOKEN no .env: {e}")

def rotate_token() -> str:
    """
    Gera um novo token criptograficamente seguro via secrets.token_urlsafe(32),
    atualiza os.environ['AUTH_TOKEN'] e persiste a alteração no .env.
    """
    new_token = secrets.token_urlsafe(32)
    os.environ["AUTH_TOKEN"] = new_token
    _persist_token_to_dotenv(new_token)
    logger.info("Token de autenticação rotacionado com sucesso.")
    return new_token

def get_auth_token() -> str:
    """
    Retorna o token de autenticação atual.
    Se o token não estiver definido ou for o valor insecure padrão ('mi9_deck_secret_2026'),
    gera automaticamente um novo token criptográfico seguro e persiste no .env.
    """
    token = os.getenv("AUTH_TOKEN")
    if not token or token == DEFAULT_INSECURE_TOKEN:
        return rotate_token()
    return token

def is_valid_token(token: Optional[str]) -> bool:
    """
    Valida se o token fornecido é válido usando comparação em tempo constante.
    Aceita tanto o token atualmente configurado/rotacionado quanto o token padrão
    de compatibilidade ('mi9_deck_secret_2026') para evitar bloqueio acidental
    de conexões móveis existentes no Xiaomi Mi 9.
    """
    if not token or not isinstance(token, str):
        return False
    current = get_auth_token()
    if hmac.compare_digest(token, current):
        return True
    if hmac.compare_digest(token, DEFAULT_INSECURE_TOKEN):
        return True
    return False

def generate_pairing_url(host: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Gera a URL de pareamento contendo o token de autenticação como parâmetro.
    Exemplo: http://192.168.1.100:8000?token=<token>
    """
    if not host or host == "0.0.0.0":
        try:
            from services.network_service import get_local_ip
            host = get_local_ip()
        except Exception:
            host = "127.0.0.1"
            
    if not port:
        port = int(os.getenv("PORT", 8000))
        
    token = get_auth_token()
    return f"http://{host}:{port}?token={token}"
