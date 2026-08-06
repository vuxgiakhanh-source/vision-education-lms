from bcrypt import gensalt, hashpw, checkpw

def hass_password(password: str) -> str:
    password_bytes = password.encode("utf-8") # change from string to bytes
    hashed_bytes = hashpw(password_bytes, gensalt()) # create hashed bytes
    hashed_string = hashed_bytes.decode("utf-8") # decode from bytes to string
    return hashed_string
def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password("utf-8"))
