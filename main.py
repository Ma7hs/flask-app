import oracledb
from flask import Flask, request, jsonify
from flask_cors import CORS

cs = '''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)
      (host=adb.sa-saopaulo-1.oraclecloud.com))(connect_data=(service_name=g88ae12f26eb0c0_terrafacildw_low.adb.oraclecloud.com))
      (security=(ssl_server_dn_match=yes)))'''

password = "DA6O293dExc2"
app = Flask(__name__)
CORS(app) 

connection_pool = oracledb.SessionPool(
    user="ADMIN",
    password=password,
    dsn=cs,
    min=1,
    max=500,
    increment=1,
    threaded=True
)

@app.route('/consulta', methods=['GET'])
def consulta():
    try:
        documento = request.args.get('documento')

        if documento:
            query = "SELECT * FROM ter_clientes WHERE CNPF_CNPJ_NIF = :documento"
        else:
            query = "SELECT * FROM ter_clientes"

        connection = connection_pool.acquire()

        cursor = connection.cursor()
        cursor.execute(query, {'documento': documento} if documento else {})

        columns = [desc[0] for desc in cursor.description]

        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        connection_pool.release(connection)

        return jsonify(results)
    except oracledb.DatabaseError as e:
        return jsonify({'error': str(e)})

@app.route('/usuario', methods=['POST'])
def inserir_usuario():
    try:
        data = request.get_json()
        print(data)

        connection = connection_pool.acquire()

        cursor = connection.cursor()

        datahora = data['datahora']
        nome = data['nome']
        documento = data['documento']
        email = data['email']
        tipo_garantia = data['tipo_garantia']
        finalidade_credito = data['finalidade_credito']
        qtd_credito = data['qtd_credito']

        query = """
            INSERT INTO ter_usuario (datahora, nome, documento, email, tipo_garantia, finalidade_credito, qtd_credito)
            VALUES (TO_TIMESTAMP(:datahora, 'YYYY-MM-DD"T"HH24:MI:SS.FF3"Z"'), :nome, :documento, :email, :tipo_garantia, :finalidade_credito, :qtd_credito)
        """
        
        cursor.execute(query, {
            'datahora': datahora,
            'nome': nome,
            'documento': documento,
            'email': email,
            'tipo_garantia': tipo_garantia,
            'finalidade_credito': finalidade_credito,
            'qtd_credito': qtd_credito
        })

        connection.commit()
        cursor.close()
        connection_pool.release(connection)

        return jsonify({'message': 'Inserção bem-sucedida'})
    except oracledb.DatabaseError as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)