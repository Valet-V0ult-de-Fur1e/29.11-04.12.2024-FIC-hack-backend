import hashlib

def get_hash(input_string: str) -> str:
    """
    Возвращает SHA-256 хэш строки.
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()
