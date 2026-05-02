"""
hash_password.py
Gera o hash bcrypt de uma senha para usar no USERS_JSON do .env

Uso:
    uv run hash_password.py
    uv run hash_password.py minhasenha
"""
import sys, bcrypt

def main():
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        import getpass
        password = getpass.getpass("Digite a senha: ")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    print(f"\nHash gerado:\n{hashed}\n")
    print("Cole no USERS_JSON do seu .env:")
    print(f'[{{"username":"admin","password_hash":"{hashed}","role":"admin"}}]')

if __name__ == "__main__":
    main()
