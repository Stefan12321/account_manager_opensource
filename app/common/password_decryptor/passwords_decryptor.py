import os
import re
import json
import base64
import sqlite3
import pywintypes
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import csv

DST_DB = "Loginvault.db"
def get_secret_key_from_file(path):
    with open(fr'{path}\secret', "rb") as secret_file:
        secret_key = secret_file.read()
        secret_key = win32crypt.CryptProtectData(secret_key)
        secret_key = (base64.b64encode(b"DPAPI" + secret_key)).decode("utf-8")
        return secret_key


def write_secret_key_to_file(path, secret_key):
    CHROME_PATH_LOCAL_STATE = fr'{path}\Local State'
    with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
        testt = local_state["os_crypt"]["encrypted_key"]
        print(testt)
        local_state["os_crypt"]["encrypted_key"] = secret_key

    with open(CHROME_PATH_LOCAL_STATE, "w", encoding='utf-8') as f:
        json.dump(local_state, f)


def encrypt_secret_key(secret_key):
    encrypted_secret_key = win32crypt.CryptProtectData(secret_key)
    return encrypted_secret_key


def get_secret_key(path):
    CHROME_PATH_LOCAL_STATE = fr'{path}\Local State'

    try:
        # (1) Get secretkey from chrome local state
        with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        # print(f'secret_key: {secret_key}')
        # Remove suffix DPAPI
        secret_key = secret_key[5:]
        secret_key = win32crypt.CryptUnprotectData(secret_key)[1]
        return secret_key
    except pywintypes.error as e:
        if e.funcname == "CryptUnprotectData":
            return 'error'


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(ciphertext, secret_key):
    try:
        # (3-a) Initialisation vector for AES decryption
        initialisation_vector = ciphertext[3:15]
        # (3-b) Get encrypted password by removing suffix bytes (last 16 bits)
        # Encrypted password is 192 bits
        encrypted_password = ciphertext[15:-16]
        # (4) Build the cipher to decrypt the ciphertext
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()
        return decrypted_pass
    except Exception as e:
        print("%s" % str(e))
        print("[ERR] Unable to decrypt, Chrome version <80 not supported. Please check.")
        return ""


def get_db_connection(chrome_path_login_db):
    dst_db = DST_DB
    try:
        print(chrome_path_login_db)
        shutil.copy2(chrome_path_login_db, dst_db)
        return sqlite3.connect(dst_db)
    except Exception as e:
        print("%s" % str(e))
        print("[ERR] Chrome database cannot be found")
        return None


def do_decrypt(path: str) -> str:
    CHROME_PATH = path
    passwords = ''
    try:
        # Create Dataframe to store passwords
        secret_key = get_secret_key(path)
        if secret_key == 'error':
            print(path)
            key = get_secret_key_from_file(path)
            write_secret_key_to_file(path, key)
            secret_key = get_secret_key(path)

        with open(fr'{path}\secret', "wb") as secret_file:
            if secret_key != "":
                secret_file.write(secret_key)
            else:
                raise KeyError("empty secret_key")
        with open(fr'{path}\decrypted_password.csv', mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["index", "url", "username", "password"])
            # (1) Get secret key

            print(f"secret key: {secret_key}")
            # Search user profile or default folder (this is where the encrypted login password is stored)
            folders = [element for element in os.listdir(CHROME_PATH) if
                       re.search("^Profile*|^Default$", element) != None]
            for folder in folders:
                # (2) Get ciphertext from sqlite database
                chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data" % (CHROME_PATH, folder))
                conn = get_db_connection(chrome_path_login_db)
                if (secret_key and conn):
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for index, login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if (url != "" and username != "" and ciphertext != ""):
                            # (3) Filter the initialisation vector & encrypted password from ciphertext
                            # (4) Use AES algorithm to decrypt the password
                            decrypted_password = decrypt_password(ciphertext, secret_key)
                            passwords += f'Sequence: {index}\nURL: {url}\nUser Name: {username}\nPassword: {decrypted_password}\n{"*" * 50}\n'

                            # (5) Save into CSV
                            csv_writer.writerow([index, url, username, decrypted_password])
                    # Close database connection
                    cursor.close()
                    conn.close()
                    # Delete temp login db
                    os.remove(DST_DB)
                    return passwords
    except Exception as e:
        print(f"[ERR] {str(e)}")


def do_decrypt_dict(path: str) -> dict:
    CHROME_PATH = path
    passwords = {}
    try:
        # Create Dataframe to store passwords
        secret_key = get_secret_key(path)
        if secret_key == 'error':
            print(path)
            key = get_secret_key_from_file(path)
            write_secret_key_to_file(path, key)
            secret_key = get_secret_key(path)

        with open(fr'{path}\secret', "wb") as secret_file:
            if secret_key != "":
                secret_file.write(secret_key)
            else:
                raise KeyError("empty secret_key")
        with open(fr'{path}\decrypted_password.csv', mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["index", "url", "username", "password"])
            # (1) Get secret key

            print(f"secret key: {secret_key}")
            # Search user profile or default folder (this is where the encrypted login password is stored)
            folders = [element for element in os.listdir(CHROME_PATH) if
                       re.search("^Profile*|^Default$", element) != None]
            for folder in folders:
                # (2) Get ciphertext from sqlite database
                chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data" % (CHROME_PATH, folder))
                conn = get_db_connection(chrome_path_login_db)
                if (secret_key and conn):
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for index, login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if (url != "" and username != "" and ciphertext != ""):
                            # (3) Filter the initialisation vector & encrypted password from ciphertext
                            # (4) Use AES algorithm to decrypt the password
                            decrypted_password = decrypt_password(ciphertext, secret_key)
                            passwords.update({url: {"username": username, "password": decrypted_password}})

                            # (5) Save into CSV
                            csv_writer.writerow([index, url, username, decrypted_password])
                    # Close database connection
                    cursor.close()
                    conn.close()
                    # Delete temp login db
                    os.remove(DST_DB)
                    return passwords
    except Exception as e:
        print(f"[ERR] {str(e)}")


if __name__ == '__main__':
    print(do_decrypt(r"C:\Users\Stefan\PycharmProjects\accounts_manager\profiles\v2 - 146"))
