from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt_token(encryption_key, token_to_encrypt):
    cipher = AES.new(encryption_key, AES.MODE_CBC)
    iv = cipher.iv # Get the initialization vector (IV)
    
    token_to_byte = token_to_encrypt.encode('utf-8')
    
    encrypted_data = cipher.encrypt(pad(token_to_byte, AES.block_size))
    return iv + encrypted_data # Return both IV and encrypted data

def decrypt_token(encryption_key, token_to_decrypt):
    iv = token_to_decrypt[:16] # First 16 bytes will be IV
    encrypted_data = token_to_decrypt[16:] # Encrypted token
    
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    
    byte_to_token = decrypted_data.decode('utf-8')
    return byte_to_token