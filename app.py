from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)

BANCO = "orcador.db"


def conectar_banco():
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            empresa_nome TEXT,
            empresa_email TEXT,
            empresa_telefone TEXT,
            cliente_nome TEXT,
            cliente_telefone TEXT,
            cliente_endereco TEXT,
            data_emissao TEXT,
            validade TEXT,
            garantia TEXT,
            situacao TEXT,
            pagamento TEXT,
            condicoes TEXT,
            desconto REAL DEFAULT 0,
            bdi REAL DEFAULT 0,
            itens TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()


@app.route("/")
def inicio():
    return render_template(
        "index.html",
        data_atual=date.today().isoformat()
    )


@app.route("/api/orcamentos", methods=["POST"])
def salvar_orcamento():
    dados = request.get_json()

    conexao = conectar_banco()

    cursor = conexao.execute("""
        INSERT INTO orcamentos (
            numero,
            empresa_nome,
            empresa_email,
            empresa_telefone,
            cliente_nome,
            cliente_telefone,
            cliente_endereco,
            data_emissao,
            validade,
            garantia,
            situacao,
            pagamento,
            condicoes,
            desconto,
            bdi,
            itens
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados.get("numero", ""),
        dados.get("empresa_nome", ""),
        dados.get("empresa_email", ""),
        dados.get("empresa_telefone", ""),
        dados.get("cliente_nome", ""),
        dados.get("cliente_telefone", ""),
        dados.get("cliente_endereco", ""),
        dados.get("data_emissao", ""),
        dados.get("validade", ""),
        dados.get("garantia", ""),
        dados.get("situacao", ""),
        dados.get("pagamento", ""),
        dados.get("condicoes", ""),
        dados.get("desconto", 0),
        dados.get("bdi", 0),
        str(dados.get("itens", []))
    ))

    conexao.commit()

    id_orcamento = cursor.lastrowid

    conexao.close()

    return jsonify({
        "sucesso": True,
        "id": id_orcamento,
        "mensagem": "Orçamento salvo com sucesso."
    })


@app.route("/api/orcamentos", methods=["GET"])
def listar_orcamentos():
    conexao = conectar_banco()

    registros = conexao.execute("""
        SELECT
            id,
            numero,
            cliente_nome,
            situacao,
            data_emissao,
            criado_em
        FROM orcamentos
        ORDER BY id DESC
    """).fetchall()

    conexao.close()

    return jsonify([
        dict(registro)
        for registro in registros
    ])


@app.route("/api/orcamentos/<int:id>", methods=["GET"])
def buscar_orcamento(id):
    conexao = conectar_banco()

    registro = conexao.execute("""
        SELECT *
        FROM orcamentos
        WHERE id = ?
    """, (id,)).fetchone()

    conexao.close()

    if registro is None:
        return jsonify({
            "erro": "Orçamento não encontrado."
        }), 404

    return jsonify(dict(registro))


@app.route("/api/orcamentos/<int:id>", methods=["PUT"])
def atualizar_orcamento(id):
    dados = request.get_json()

    conexao = conectar_banco()

    conexao.execute("""
        UPDATE orcamentos
        SET
            numero = ?,
            empresa_nome = ?,
            empresa_email = ?,
            empresa_telefone = ?,
            cliente_nome = ?,
            cliente_telefone = ?,
            cliente_endereco = ?,
            data_emissao = ?,
            validade = ?,
            garantia = ?,
            situacao = ?,
            pagamento = ?,
            condicoes = ?,
            desconto = ?,
            bdi = ?,
            itens = ?
        WHERE id = ?
    """, (
        dados.get("numero", ""),
        dados.get("empresa_nome", ""),
        dados.get("empresa_email", ""),
        dados.get("empresa_telefone", ""),
        dados.get("cliente_nome", ""),
        dados.get("cliente_telefone", ""),
        dados.get("cliente_endereco", ""),
        dados.get("data_emissao", ""),
        dados.get("validade", ""),
        dados.get("garantia", ""),
        dados.get("situacao", ""),
        dados.get("pagamento", ""),
        dados.get("condicoes", ""),
        dados.get("desconto", 0),
        dados.get("bdi", 0),
        str(dados.get("itens", [])),
        id
    ))

    conexao.commit()
    conexao.close()

    return jsonify({
        "sucesso": True,
        "mensagem": "Orçamento atualizado com sucesso."
    })


@app.route("/api/orcamentos/<int:id>", methods=["DELETE"])
def excluir_orcamento(id):
    conexao = conectar_banco()

    conexao.execute("""
        DELETE FROM orcamentos
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return jsonify({
        "sucesso": True,
        "mensagem": "Orçamento excluído com sucesso."
    })


if __name__ == "__main__":
    criar_banco()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
