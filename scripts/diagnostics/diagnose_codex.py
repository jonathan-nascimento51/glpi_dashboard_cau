import datetime
import os
import subprocess


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar '{cmd}': {e.stderr.strip()}"


def diagnose_codex():
    print("== Diagnóstico do Ambiente Codex ==")
    print(f"Timestamp: {datetime.datetime.now()}\n")

    print("[1] Status do Git:")
    print(run_command("git status"))

    print("\n[2] Verificação de Branch Protegido:")
    print(run_command("git branch -vv"))

    print("\n[3] Teste de autenticação GitHub:")
    print(run_command("gh auth status"))

    print("\n[4] Confirmação do Token do Codex:")
    token_status = os.getenv("CODEX_TOKEN", None)
    print(
        f"Token Configurado: {token_status}"
        if token_status
        else "Token NÃO Configurado!"
    )

    print("\n[5] Permissões de Pastas do Projeto:")
    print(run_command("ls -la"))

    print("\n[6] Últimos Logs do Codex:")
    print(run_command("tail -n 20 codex.log"))

    print("\n[7] Teste de Escrita Temporária no Projeto:")
    try:
        with open("codex_diagnostic_test.txt", "w") as f:
            f.write("Teste de escrita executado em " + str(datetime.datetime.now()))
        print("✅ Escrita em arquivo permitida.")
    except Exception as e:
        print(f"❌ Falha ao escrever no diretório atual: {e}")


if __name__ == "__main__":
    diagnose_codex()
