from flask import Flask, jsonify, make_response, request
from core.database import registrar_usuario, iniciar_database, login_user

app = Flask(__name__)
try:
    iniciar_database()
    print("Banco iniciado com sucesso!")
except Exception as error:
    print(f'erro encontrado! {error}')


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data= request.get_json()
        usuario = data.get('usuario')
        password = data.get('password')
        if not all([usuario, password]):
            return make_response(jsonify({"status": "erro, todos campos devem ser preenchidos!"}),400)
        
        login_user(usuario, password)
        return make_response(jsonify({"status":"sucesso!"}), 200)


# Ping-Pong API TEST
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"status": "pong", "message":"API is running!"}), 200

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data= request.get_json()
        nome= data.get('nome')
        usuario= data.get('usuario')
        senha= data.get('senha')
        email= data.get('email')

        if not all([nome, usuario, senha, email]):
            return make_response(jsonify({"status":"error, preenche tudo, porra :)"}), 400)

        registrar_usuario(nome, usuario, senha, email)
        return make_response(jsonify({"status":"sucesso!"}), 200)
    except Exception as error:
        return make_response(jsonify({"status":str(error)}), 500)

if __name__ == '__main__':
    app.run(debug=True)
