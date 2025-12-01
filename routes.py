from app import app
from flask import render_template, request, make_response, jsonify, redirect
import re
from db import *

def validar_cnpj(cnpj):
    regex = r'^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$'
    
    if not re.match(regex, cnpj):
        return False
    
    cnpj_limpo = re.sub(r'[^\d]', '', cnpj)
    
    if len(cnpj_limpo) != 14:
        return False
    
    return validar_digitos_cnpj(cnpj_limpo)

def validar_digitos_cnpj(cnpj):
    if len(cnpj) != 14:
        return False
    
    return True

@app.route('/')
def home():
    return render_template('index.html')

# Cadastrar sacador
@app.route('/sacador', methods=['POST'])
def cadastrar_sacador():
    dados = request.get_json(silent=True) or request.form

    valores = ["nome","cnpj"]
    for campo in valores:
        if campo not in dados:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
        
    if not validar_cnpj(dados["cnpj"]):
        return jsonify({"erro": "CNPJ inválido"}), 400
    
    try:
        query = """
        INSERT INTO sacador (nome, cnpj)
        VALUES (?, ?)
        """

        cnpj_limpo = re.sub(r'[^\d]', '', dados["cnpj"])

        params = [
            dados["nome"],
            cnpj_limpo
        ]

        cursor = conexao.execute(query, params)
        conexao.commit()

        novo_id = cursor.lastrowid

        return jsonify({
            "mensagem": "Sacador cadastrado!",
            "id": novo_id
        }), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Cadastrar sacado  
@app.route('/sacado', methods=['POST'])
def cadastrar_sacado():
    dados = request.get_json(silent=True) or request.form

    valores = ["nome","cnpj"]
    for campo in valores:
        if campo not in dados:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
        
    if not validar_cnpj(dados["cnpj"]):
        return jsonify({"erro": "CNPJ inválido"}), 400
        
    try:
        query = """
        INSERT INTO sacado (nome, cnpj)
        VALUES (?, ?)
        """
        cnpj_limpo = re.sub(r'[^\d]', '', dados["cnpj"])

        params = [
            dados["nome"],
            cnpj_limpo
        ]

        cursor = conexao.execute(query, params)
        conexao.commit()

        novo_id = cursor.lastrowid

        return jsonify({
            "mensagem": "Sacado cadastrado!",
            "id": novo_id
        }), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/cad_sacado', methods=['GET'])
def sacado_form():
    return render_template('cad_sacado.html')

@app.route('/cad_sacador', methods=['GET'])
def sacador_form():
    return render_template('cad_sacador.html')

# Cadastrar duplicata
@app.route('/cad_duplicata', methods=['GET', 'POST'])
def cad_duplicata():

    if request.method == "GET":

        sacadores = conexao.execute("SELECT id, nome FROM sacador").fetchall()
        sacados = conexao.execute("SELECT id, nome FROM sacado").fetchall()

        return render_template("cad_duplicata.html", sacadores=sacadores, sacados=sacados)

    dados = request.get_json(silent=True) or request.form

    valores = ["valor", "prazo", "data", "sacador_id", "sacado_id"]
    for campo in valores:
        if campo not in dados:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400

    try:
        query = """
        INSERT INTO duplicata (valor, prazo, data, sacador_id, sacado_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        status_duplicata = dados.get("status")
        if not status_duplicata:
            status_duplicata = "emitida"

        params = [
            dados["valor"],
            dados["prazo"],
            dados["data"],
            dados["sacador_id"],
            dados["sacado_id"],
            status_duplicata
        ]

        cursor = conexao.execute(query, params)
        conexao.commit()

        novo_id = cursor.lastrowid

        return jsonify({
            "mensagem": "Duplicata cadastrada com sucesso!",
            "id": novo_id,
        }), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/cad_duplicata_form')
def cad_duplicata_form():

    sacadores = conexao.execute("SELECT id, nome FROM sacador").fetchall()
    sacados = conexao.execute("SELECT id, nome FROM sacado").fetchall()

    return render_template("cad_duplicata.html", sacadores=sacadores, sacados=sacados)


# Buscar duplicata
@app.route('/buscar_duplicatas', methods=['GET'])
def buscar_dupe():
    dados_json = request.get_json(silent=True)

    if dados_json:
        numero = dados_json.get('id')
        sacado = dados_json.get('sacado')
        sacador = dados_json.get('sacador')
        data = dados_json.get('data')
        status = dados_json.get('status')
    else:
        numero = request.args.get('id')
        sacado = request.args.get('sacado')
        sacador = request.args.get('sacador')
        data = request.args.get('data')
        status = request.args.get('status')

    query = """
    SELECT
        duplicata.id,
        duplicata.valor,
        duplicata.prazo,
        duplicata.data,
        sacador.nome AS sacador_nome,
        sacador.cnpj AS sacador_cnpj,
        sacado.nome AS sacado_nome,
        sacado.cnpj AS sacado_cnpj,
        duplicata.status
    FROM duplicata
    LEFT JOIN sacador ON duplicata.sacador_id = sacador.id
    LEFT JOIN sacado  ON duplicata.sacado_id  = sacado.id
    WHERE 1 = 1
    """

    params = []

    if numero:
        query += " AND duplicata.id = ? "
        params.append(numero)

    if sacado:
        query += " AND (sacado.nome LIKE ? OR sacado.cnpj LIKE ?) "
        params.append(f"%{sacado}%")
        params.append(f"%{sacado}%")

    if sacador:
        query += " AND (sacador.nome LIKE ? OR sacador.cnpj LIKE ?) "
        params.append(f"%{sacador}%")
        params.append(f"%{sacador}%")

    if data:
        query += " AND duplicata.data = ? "
        params.append(data)

    if status:
        query += " AND duplicata.status = ? "
        params.append(status)

    query += " ORDER BY duplicata.id ASC"

    cursor = conexao.execute(query, params)
    resultados = cursor.fetchall()

    lista = []
    for row in resultados:
        lista.append({
            "id": row[0],
            "valor": row[1],
            "prazo": row[2],
            "data": row[3],
            "sacador": {
                "nome": row[4],
                "cnpj": row[5]
            },
            "sacado": {
                "nome": row[6],
                "cnpj": row[7]
            },
            "status": row[8]
        })

    if dados_json:
        return jsonify(lista)

    return render_template("buscar_duplicata.html", duplicatas=lista)


# Atualizar status
@app.route('/duplicatas/<int:id>/status', methods=['GET', 'POST'])
def atualizar_status(id):
    
    cursor = conexao.execute("SELECT status FROM duplicata WHERE id = ?", (id,))
    row = cursor.fetchone()
    status_atual = row[0] if row else None
    
    if request.method == 'POST':
        novo_status = request.form.get("status")


        if not novo_status:
            return render_template("atualizar_status.html", id=id, erro="O status é obrigatório!")

        try:
            query = """
            UPDATE duplicata
            SET status = ?
            WHERE id = ?
            """

            conexao.execute(query, (novo_status, id))
            conexao.commit()

            return render_template("atualizar_status.html",
                                   id=id,sucesso="Status atualizado com sucesso!",
                                   novo_status=novo_status)

        except Exception as e:
            return render_template("atualizar_status.html", id=id, erro=str(e))

    return render_template("atualizar_status.html", id=id, status=status_atual)

@app.route("/duplicatas/options")
def escolher_id():
    return render_template("options.html")

@app.route("/duplicatas/buscar_id")
def buscar_id():
    duplicata_id = request.args.get("id")

    cursor.execute("SELECT * FROM duplicata WHERE id = ?", (duplicata_id,))
    duplicata = cursor.fetchone()

    if not duplicata:
        return render_template("index.html", erro="Nenhuma duplicata encontrada com esse ID.")

    return redirect(f"/duplicatas/{duplicata_id}/status")