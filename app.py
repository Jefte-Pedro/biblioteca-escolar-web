from flask import Flask, request, jsonify
from datetime import datetime
import random
import re

from database import engine, Base, SessionLocal
from models import Aluno, Livro, Emprestimo
from scheduler import iniciar_agendador
from whatsapp import enviar_whatsapp


app = Flask(__name__)
codigos = {}


def validar_email(email):
    if not isinstance(email, str):
        return False

    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()) is not None


def normalizar_numero(numero):
    if not isinstance(numero, str):
        return None

    digitos = re.sub(r"\D", "", numero)

    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]

    if len(digitos) in (10, 11):
        return digitos

    return None


def validar_numero(numero):
    return normalizar_numero(numero) is not None


def normalizar_contato(contato):
    if validar_email(contato):
        return "email", contato.strip().lower()

    numero = normalizar_numero(contato)

    if numero:
        return "numero", numero

    return None, None


def converter_data(valor):
    if not isinstance(valor, str):
        return None

    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return None


def gerar_codigo():
    return str(random.randint(100000, 999999))


Base.metadata.create_all(engine)
iniciar_agendador()


@app.route("/aluno", methods=["POST"])
def criar_aluno():
    data = request.get_json(silent=True) or {}
    telefone = normalizar_numero(data.get("telefone") or data.get("whatsapp"))

    if not data.get("nome") or not telefone:
        return jsonify({"erro": "Nome e telefone valido sao obrigatorios"}), 400

    db = SessionLocal()

    try:
        aluno = Aluno(
            nome=data["nome"],
            telefone=telefone
        )

        if data.get("matricula") is not None:
            aluno.matricula = data["matricula"]

        db.add(aluno)
        db.flush()
        matricula = aluno.matricula
        db.commit()

        return jsonify({"msg": "Aluno criado", "matricula": matricula})

    except Exception as erro:
        db.rollback()
        return jsonify({"erro": str(erro)}), 500

    finally:
        db.close()


@app.route("/livro", methods=["POST"])
def criar_livro():
    data = request.get_json(silent=True) or {}

    if not data.get("titulo"):
        return jsonify({"erro": "Titulo e obrigatorio"}), 400

    db = SessionLocal()

    try:
        livro = Livro(
            titulo=data["titulo"]
        )

        if data.get("id_livro") is not None:
            livro.id_livro = data["id_livro"]

        db.add(livro)
        db.flush()
        id_livro = livro.id_livro
        db.commit()

        return jsonify({"msg": "Livro criado", "id_livro": id_livro})

    except Exception as erro:
        db.rollback()
        return jsonify({"erro": str(erro)}), 500

    finally:
        db.close()


@app.route("/emprestimo", methods=["POST"])
def criar_emprestimo():
    data = request.get_json(silent=True) or {}
    data_devolucao_prevista = converter_data(
        data.get("data_devolucao_prevista") or data.get("data_devolucao")
    )
    matricula = data.get("matricula") or data.get("aluno_id")
    id_exemplar = data.get("id_exemplar")

    if not matricula or not id_exemplar or not data_devolucao_prevista:
        return jsonify({
            "erro": "matricula, id_exemplar e data_devolucao_prevista sao obrigatorios"
        }), 400

    db = SessionLocal()

    try:
        emprestimo = Emprestimo(
            matricula=matricula,
            id_exemplar=id_exemplar,
            data_devolucao_prevista=data_devolucao_prevista
        )

        db.add(emprestimo)
        db.flush()
        id_emprestimo = emprestimo.id_emprestimo
        db.commit()

        return jsonify({"msg": "Emprestimo registrado", "id_emprestimo": id_emprestimo})

    except Exception as erro:
        db.rollback()
        return jsonify({"erro": str(erro)}), 500

    finally:
        db.close()


@app.route("/enviar_codigo", methods=["POST"])
def enviar_codigo():
    data = request.get_json(silent=True) or {}
    contato = data.get("contato")
    tipo, contato_normalizado = normalizar_contato(contato)

    if not contato_normalizado:
        return jsonify({"erro": "Email ou numero invalido"}), 400

    codigo = gerar_codigo()
    codigos[contato_normalizado] = codigo

    if tipo == "numero":
        enviar_whatsapp(contato_normalizado, f"Seu codigo de confirmacao e: {codigo}")
    else:
        print(f"Codigo para {contato_normalizado}: {codigo}")

    return jsonify({"msg": f"Codigo enviado via {tipo}"})


@app.route("/verificar_codigo", methods=["POST"])
def verificar_codigo():
    data = request.get_json(silent=True) or {}
    contato = data.get("contato")
    codigo = data.get("codigo")
    _, contato_normalizado = normalizar_contato(contato)

    if contato_normalizado and codigos.get(contato_normalizado) == codigo:
        del codigos[contato_normalizado]
        return jsonify({"msg": "Verificado com sucesso"})

    return jsonify({"erro": "Codigo incorreto"}), 400


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
