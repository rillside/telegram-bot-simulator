import secrets
import string

def generate_bot_token(bot_id: int) -> str:
    alphabet = string.ascii_letters + string.digits + "_-"
    secret = "".join(secrets.choice(alphabet) for _ in range(35))
    return f"{bot_id}:{secret}"

def validate_token_format(token: str) -> bool:
    if not token or ":" not in token:
        return False
    parts = token.split(":", 1)
    return parts[0].isdigit() and len(parts[1]) > 5
