import uuid
import hashlib

### NO LONGER IN USE. INCLUDED FOR EXAMPLE ###

class hash_pass:
    def obf_pass(password):
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
    def check_pass(hashed_pass, user_pass):
        password, salt = hashed_pass.split(':')
        return password == hashlib.sha256(salt.encode() + user_pass.encode()).hexdigest()
    
