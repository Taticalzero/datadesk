"""
manage_users.py
CLI para gerenciar usuarios do banco SQLite (substitui o antigo hash_password.py).

Uso:
    uv run manage_users.py create <username> [--role admin|user] [--password SENHA]
    uv run manage_users.py set-password <username> [--password SENHA]
    uv run manage_users.py delete <username>
    uv run manage_users.py list

Se --password nao for passado, a senha sera solicitada de forma oculta (getpass).
"""
from __future__ import annotations

import argparse
import getpass
import sys

from app.users_db import (
    USERS_DB_PATH,
    create_user,
    delete_user,
    init_users_db,
    list_users,
    set_password,
)


def _prompt_password(confirm: bool = True) -> str:
    pwd = getpass.getpass("Senha: ")
    if not pwd:
        sys.exit("Senha vazia. Abortado.")
    if confirm:
        again = getpass.getpass("Confirme a senha: ")
        if pwd != again:
            sys.exit("As senhas nao coincidem. Abortado.")
    return pwd


def cmd_create(args: argparse.Namespace) -> None:
    pwd = args.password or _prompt_password()
    try:
        create_user(args.username, pwd, role=args.role)
    except ValueError as e:
        sys.exit(str(e))
    print(f"Usuario '{args.username}' criado (role={args.role}).")


def cmd_set_password(args: argparse.Namespace) -> None:
    pwd = args.password or _prompt_password()
    if not set_password(args.username, pwd):
        sys.exit(f"Usuario '{args.username}' nao encontrado.")
    print(f"Senha do usuario '{args.username}' atualizada.")


def cmd_delete(args: argparse.Namespace) -> None:
    if not delete_user(args.username):
        sys.exit(f"Usuario '{args.username}' nao encontrado.")
    print(f"Usuario '{args.username}' removido.")


def cmd_list(_: argparse.Namespace) -> None:
    users = list_users()
    if not users:
        print("Nenhum usuario cadastrado.")
        return
    print(f"{'username':<20} {'role':<10} created_at")
    print("-" * 60)
    for u in users:
        print(f"{u['username']:<20} {u['role']:<10} {u['created_at']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Gerenciador de usuarios (SQLite em '{USERS_DB_PATH}')."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Cria um novo usuario")
    p_create.add_argument("username")
    p_create.add_argument("--role", default="user", choices=["admin", "user"])
    p_create.add_argument("--password", help="(opcional) senha em texto puro")
    p_create.set_defaults(func=cmd_create)

    p_set = sub.add_parser("set-password", help="Atualiza a senha de um usuario")
    p_set.add_argument("username")
    p_set.add_argument("--password", help="(opcional) senha em texto puro")
    p_set.set_defaults(func=cmd_set_password)

    p_del = sub.add_parser("delete", help="Remove um usuario")
    p_del.add_argument("username")
    p_del.set_defaults(func=cmd_delete)

    p_list = sub.add_parser("list", help="Lista todos os usuarios")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    init_users_db()
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
