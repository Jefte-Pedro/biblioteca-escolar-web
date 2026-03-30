"""
book_covers.py
==============
Busca capas de livros no banco MySQL/MariaDB e salva a URL da imagem.

Fluxo:
  1. Conecta ao banco e garante que as colunas `isbn` e `capa_url` existem.
  2. Para cada livro SEM capa cadastrada:
       a. Busca o ISBN via Google Books API (título + autor).
       b. Com o ISBN, busca a capa na Open Library.
       c. Se não encontrar, usa a capa da própria Google Books como fallback.
       d. Salva a URL e o ISBN no banco.
  3. Exibe um relatório final.

Dependências:
    pip install mysql-connector-python requests

Configuração:
    Edite o bloco DB_CONFIG e, opcionalmente, GOOGLE_BOOKS_API_KEY abaixo.
"""

import time
import requests
import mysql.connector
from mysql.connector import Error

# ──────────────────────────────────────────────
# CONFIGURAÇÃO — edite aqui
# ──────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",       # ex: "127.0.0.1" ou IP do servidor
    "port":     3306,
    "database": "nome_do_banco",   # ← altere
    "user":     "seu_usuario",     # ← altere
    "password": "sua_senha",       # ← altere
}

TABLE_NAME = "livros"              # nome da sua tabela
COL_ID     = "id"                  # coluna PK
COL_TITULO = "titulo"              # coluna título
COL_AUTOR  = "autor"               # coluna autor
COL_ISBN   = "isbn"                # será criada se não existir
COL_CAPA   = "capa_url"            # será criada se não existir

# Opcional: adicione sua chave da Google Books API para evitar limites
# Obtenha gratuitamente em: https://console.cloud.google.com/
GOOGLE_BOOKS_API_KEY = ""          # deixe "" para usar sem chave (limite menor)

DELAY_ENTRE_REQUESTS = 0.5         # segundos entre chamadas à API (evitar bloqueio)
# ──────────────────────────────────────────────


def conectar():
    """Retorna uma conexão ativa com o banco."""
    conn = mysql.connector.connect(**DB_CONFIG)
    print(f"✅ Conectado ao banco '{DB_CONFIG['database']}' em {DB_CONFIG['host']}")
    return conn


def garantir_colunas(cursor):
    """Adiciona as colunas isbn e capa_url se ainda não existirem."""
    cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}` LIKE '{COL_ISBN}'")
    if not cursor.fetchone():
        cursor.execute(f"ALTER TABLE `{TABLE_NAME}` ADD COLUMN `{COL_ISBN}` VARCHAR(20) DEFAULT NULL")
        print(f"  + Coluna `{COL_ISBN}` adicionada à tabela `{TABLE_NAME}`.")

    cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}` LIKE '{COL_CAPA}'")
    if not cursor.fetchone():
        cursor.execute(f"ALTER TABLE `{TABLE_NAME}` ADD COLUMN `{COL_CAPA}` TEXT DEFAULT NULL")
        print(f"  + Coluna `{COL_CAPA}` adicionada à tabela `{TABLE_NAME}`.")


def buscar_isbn_google(titulo: str, autor: str) -> tuple[str | None, str | None]:
    """
    Consulta a Google Books API e retorna (isbn, url_capa_google).
    Retorna (None, None) se não encontrar.
    """
    query = f"intitle:{titulo}"
    if autor:
        query += f"+inauthor:{autor}"

    params = {"q": query, "maxResults": 1, "printType": "books"}
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    try:
        resp = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=params, timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        items = data.get("volumeInfo") if "volumeInfo" in data else \
                data.get("items", [{}])[0].get("volumeInfo", {}) if data.get("totalItems", 0) > 0 else {}

        if not items and data.get("totalItems", 0) > 0:
            items = data["items"][0].get("volumeInfo", {})

        # ISBN
        isbn = None
        for id_info in items.get("industryIdentifiers", []):
            if id_info.get("type") in ("ISBN_13", "ISBN_10"):
                isbn = id_info["identifier"]
                if id_info["type"] == "ISBN_13":
                    break  # prefere ISBN-13

        # Capa do Google Books (fallback)
        thumbnail = items.get("imageLinks", {}).get("thumbnail") or \
                    items.get("imageLinks", {}).get("smallThumbnail")

        return isbn, thumbnail

    except Exception as e:
        print(f"    ⚠ Google Books API erro: {e}")
        return None, None


def buscar_capa_open_library(isbn: str) -> str | None:
    """
    Busca a URL da capa na Open Library usando o ISBN.
    Retorna None se não encontrar.
    """
    if not isbn:
        return None

    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        if resp.status_code == 200 and "image" in resp.headers.get("Content-Type", ""):
            return url
    except Exception as e:
        print(f"    ⚠ Open Library erro: {e}")

    return None


def processar_livros(conn):
    """Loop principal: percorre livros sem capa e preenche os dados."""
    cursor = conn.cursor(dictionary=True)

    # Conta situação atual
    cursor.execute(f"SELECT COUNT(*) AS total FROM `{TABLE_NAME}`")
    total = cursor.fetchone()["total"]

    cursor.execute(
        f"SELECT COUNT(*) AS com_capa FROM `{TABLE_NAME}` "
        f"WHERE `{COL_CAPA}` IS NOT NULL AND `{COL_CAPA}` != ''"
    )
    com_capa = cursor.fetchone()["com_capa"]
    sem_capa = total - com_capa

    print(f"\n📚 Total de livros  : {total}")
    print(f"   ✅ Com capa       : {com_capa}")
    print(f"   🔍 Sem capa       : {sem_capa}\n")

    if sem_capa == 0:
        print("Todos os livros já possuem capa cadastrada. Nada a fazer.")
        cursor.close()
        return

    # Busca apenas livros SEM capa
    cursor.execute(
        f"SELECT `{COL_ID}`, `{COL_TITULO}`, `{COL_AUTOR}` FROM `{TABLE_NAME}` "
        f"WHERE `{COL_CAPA}` IS NULL OR `{COL_CAPA}` = ''"
    )
    livros = cursor.fetchall()
    cursor.close()

    encontrados = 0
    nao_encontrados = []

    for i, livro in enumerate(livros, 1):
        lid    = livro[COL_ID]
        titulo = livro.get(COL_TITULO) or ""
        autor  = livro.get(COL_AUTOR)  or ""

        print(f"[{i}/{sem_capa}] 📖 {titulo[:50]} — {autor[:30]}")

        # 1. Buscar ISBN + capa fallback no Google Books
        isbn, capa_google = buscar_isbn_google(titulo, autor)
        time.sleep(DELAY_ENTRE_REQUESTS)

        # 2. Tentar capa na Open Library com o ISBN
        capa_url = buscar_capa_open_library(isbn) if isbn else None
        time.sleep(DELAY_ENTRE_REQUESTS)

        # 3. Fallback: usar capa do Google Books
        if not capa_url and capa_google:
            capa_url = capa_google
            print(f"    ↩ Usando capa do Google Books como fallback.")

        if capa_url:
            # Salva no banco
            upd = conn.cursor()
            upd.execute(
                f"UPDATE `{TABLE_NAME}` "
                f"SET `{COL_ISBN}` = %s, `{COL_CAPA}` = %s "
                f"WHERE `{COL_ID}` = %s",
                (isbn, capa_url, lid)
            )
            conn.commit()
            upd.close()
            encontrados += 1
            print(f"    ✅ Capa salva: {capa_url[:80]}...")
        else:
            nao_encontrados.append({"id": lid, "titulo": titulo, "autor": autor})
            print(f"    ❌ Capa não encontrada.")

    # ─── Relatório final ───────────────────────────────────────────────
    print("\n" + "═" * 55)
    print("📊 RELATÓRIO FINAL")
    print("═" * 55)
    print(f"  Livros processados : {sem_capa}")
    print(f"  Capas encontradas  : {encontrados}")
    print(f"  Não encontradas    : {len(nao_encontrados)}")

    if nao_encontrados:
        print("\n  Livros sem capa:")
        for l in nao_encontrados:
            print(f"    ID {l['id']}: {l['titulo']} / {l['autor']}")
    print("═" * 55)


def verificar_status(conn):
    """
    Exibe o status atual das capas no banco SEM fazer buscas.
    Útil para checar a situação antes/depois de rodar o script principal.
    """
    cursor = conn.cursor(dictionary=True)

    # Verifica se a coluna capa_url já existe
    cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}` LIKE '{COL_CAPA}'")
    if not cursor.fetchone():
        print(f"ℹ️  A coluna `{COL_CAPA}` ainda não existe. Execute o script principal primeiro.")
        cursor.close()
        return

    cursor.execute(f"SELECT COUNT(*) AS total FROM `{TABLE_NAME}`")
    total = cursor.fetchone()["total"]

    cursor.execute(
        f"SELECT COUNT(*) AS c FROM `{TABLE_NAME}` "
        f"WHERE `{COL_CAPA}` IS NOT NULL AND `{COL_CAPA}` != ''"
    )
    com_capa = cursor.fetchone()["c"]
    sem_capa = total - com_capa
    pct = (com_capa / total * 100) if total else 0

    print("\n" + "═" * 45)
    print("📊 STATUS DAS CAPAS NO BANCO")
    print("═" * 45)
    print(f"  Total de livros  : {total}")
    print(f"  ✅ Com capa      : {com_capa}  ({pct:.1f}%)")
    print(f"  ❌ Sem capa      : {sem_capa}")
    print("═" * 45)

    cursor.close()


# ──────────────────────────────────────────────
# PONTO DE ENTRADA
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    # Modo: "status" apenas verifica, qualquer outro argumento (ou nenhum) executa
    modo = sys.argv[1] if len(sys.argv) > 1 else "executar"

    try:
        conn = conectar()

        if modo == "status":
            verificar_status(conn)
        else:
            cursor = conn.cursor()
            garantir_colunas(cursor)
            conn.commit()
            cursor.close()
            processar_livros(conn)

    except Error as e:
        print(f"\n❌ Erro de banco de dados: {e}")
    except KeyboardInterrupt:
        print("\n⚠  Interrompido pelo usuário. Progresso salvo até aqui.")
    finally:
        try:
            conn.close()
            print("\n🔒 Conexão com o banco encerrada.")
        except Exception:
            pass
