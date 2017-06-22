from flask import Flask, json
from flask import request
from flask import abort
from flask import jsonify
from datetime import datetime

app = Flask(__name__)

ip_databases = {}
data_databases = {}

@app.route('/database/:<database_name>', methods=['POST', 'GET'])
def database_services(database_name):
    ip_address = request.remote_addr
    if request.method == 'POST':
        if len(ip_databases) == 0:
            ip_databases[str(ip_address)] = database_name
            data_databases[str(database_name)] = {}
            return ('', 204)
        else:
            found = False
            for k in data_databases.keys():
                if k == database_name:
                    found = True
                    break

            if found == True:
                abort(409, description="La base de datos especificada ya existe")
            else:
                ip_databases[str(ip_address)] = database_name
                data_databases[str(database_name)] = {}
                return ('', 204)

    elif request.method == 'GET':
        found = False
        for k in data_databases.keys():
            if k == database_name:
                found = True
                break

        if found == False:
            abort(405, description="La base de datos especificada no existe")
        else:
            res = []
            ip_databases[str(ip_address)] = database_name
            data = data_databases[str(database_name)]
            print(data)
            for key, val in data.items():
                print(key)
                print(val)
                value, tim = str(val).split(";")
                timestamp = datetime.fromtimestamp(int(tim))
                now = datetime.now()
                date_max = max((timestamp, now))
                if date_max == timestamp:
                    str_res = {}
                    str_res['key'] = key
                    str_res['value'] = value
                    str_res['timestamp'] = tim
                    print(str_res)
                    res.append(str_res)
            return jsonify({"data":res})

@app.route('/database', methods=['GET', 'POST'])
def list_add_databases_services():

    if request.method == 'GET':

        key = request.args.get('key', None)
        if key == None:
            if len(data_databases) == 0:
                res = {'databases':[]}
                return jsonify(res)
            else:
                list = []
                for k in data_databases.keys():
                    list.append(k)
                return jsonify({'databases':list})
        else:
            res = get_registry(key=key)
            return  res
    elif request.method == 'POST':

        ip_address = request.remote_addr
        data = request.data
        dataDict = json.loads(data)
        key = str(dataDict['key'])
        value = str(dataDict['value'])
        timestamp = str(dataDict['timestamp'])

        stored_bd = ip_databases.get(str(ip_address))
        if stored_bd != None:
            data_databases[stored_bd][key]= str(value +';'+ timestamp)
            return jsonify('Se agrego correctamente el registro a la base de datos')
        else:
            abort(409, description='No se ha creado la base de datos para esta IP')

def get_registry(key):

    print(key)
    ip_address = request.remote_addr
    stored_bd = ip_databases.get(str(ip_address))
    if stored_bd != None:
        found = False
        for k in data_databases[stored_bd].keys():
            if k == key:
                found = True
                break

        if found == True:
            val = data_databases[stored_bd][key]
            value, tim = str(val).split(";")
            timestamp = datetime.fromtimestamp(int(tim))
            now = datetime.now()
            date_max = max((timestamp, now))
            if date_max == timestamp:
                str_res = {}
                str_res['key'] = key
                str_res['value'] = value
                str_res['timestamp'] = tim
                print(str_res)
                return jsonify(str_res)
        else:
            abort(404, description='No se ha encontrado el registro con la llave indicada')
    else:
        abort(409, description='No se ha creado la base de datos para esta IP')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
