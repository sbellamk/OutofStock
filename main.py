import flask
from flask import request, jsonify
import pymysql
from flaskext.mysql import MySQL
import json

__ip = "35.223.105.218"
__username = "basicUser"
__password = "password"
__dbname = "out_of_stock"
__unix_socket = "/cloudsql/pro-kayak-230507:us-central1:out-of-stock"

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['MYSQL_USER'] = __username
app.config['MYSQL_PASSWORD'] = __password
app.config['MYSQL_DB'] = __dbname
app.config['MYSQL_UNIX_SOCKET'] = __unix_socket



@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Store Archive</h1>
<p>A prototype API for distant store list for COVID protocol.</p>'''


@app.route('/api/v1/stores', methods=['GET'])
def getallStoresinarea():
    if 'latmin' in request.args:
        latmin = (request.args['latmin'])
    else:
        return "Error: No id field provided. Please specify an latmin."
    if 'latmax' in request.args:
        latmax = (request.args['latmax'])
    else:
        return "Error: No id field provided. Please specify an latmax."
    if 'longmin' in request.args:
        longmin = (request.args['longmin'])
    else:
        return "Error: No id field provided. Please specify an longmin."
    if 'longmax' in request.args:
        longmax = (request.args['longmax'])
    else:
        return "Error: No id field provided. Please specify an longmax."
    #127.0.0.1:5000/api/v1/stores?latmin=[LATITUDEMIN]&latmax=[LATITUDEMAX]&longmin=[LONGITUDEMIN]&longmax=[LONGITUDEMAX]
    # Open database connection
    db = getdb()
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "SELECT * FROM stores WHERE latitude >= {} AND latitude <= {} AND \
            longitude >= {} AND longitude <= {} ".format(latmin, latmax, longmin, longmax)
    cur.execute(params)
    rv = cur.fetchall()
    payload = []
    content = {}
    for result in rv:
       content = {'storeID': str(result[0]),
                'storeName': str(result[1]),
                'addr': str(result[2]),
                'latitude': str(result[3]),
                'longitude': str(result[4]),
                'occupancy': str(result[5]),}
       payload.append(content)
       content = {}
    return jsonify(payload)



@app.route('/api/v1/items/all', methods=['GET'])
def getallItems():
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify an storeid."
    #127.0.0.1:5000/api/v1/items/all?storeid=[STORE_ID]
    # Open database connection
    db = getdb()
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "SELECT * FROM availability WHERE store_id = (%s)"
    cur.execute(params, storeid)
    rv = cur.fetchall()
    payload = []
    content = {}
    for result in rv:
        availability = str(result[2])
        if availability == "1":
            availability = True
        else:
            availability = False
        content = {'item_name': str(result[1]),
                 'available': availability}
        payload.append(content)
        content = {}
    return jsonify(payload)



@app.route('/api/v1/availabilityitems/all', methods=['GET'])
def getallavailabilityitems():
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify an storeid."
    if 'available' in request.args:
        available = (request.args['available'])
    else:
        return "Error: No id field provided. Please specify an available."
    #127.0.0.1:5000/api/v1/availabilityitems/all?storeid=[STORE_ID]&available=[AVAILABLEBOOLEAN]
    # Open database connection
    db = getdb()
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "SELECT * FROM availability WHERE store_id = (%s) AND available = (%s)"
    if available == "true":
        available = 1
    else:
        available = 0
    cur.execute(params, (storeid,available))
    rv = cur.fetchall()
    payload = []
    content = {}
    for result in rv:
        availability = str(result[2])
        if availability == "1":
            availability = True
        else:
            availability = False
        content = {'item_name': str(result[1]),
                 'available': availability}
        payload.append(content)
        content = {}
    return jsonify(payload)




@app.route('/api/v1/items/add', methods=['POST', 'GET'])
def postaddItem():
    if 'itemname' in request.args:
        itemname = (request.args['itemname'])
    else:
        return "Error: No id field provided. Please specify an itemname."
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify an storeid."
    if 'available' in request.args:
        available = (request.args['available'])
    else:
        return "Error: No id field provided. Please specify an available."

    #127.0.0.1:5000/api/v1/items/add?itemid=[itemid]&storeid=[STORE_ID]&available=[AVAILABLEBOOLEAN]
    # Open database connection
    db = getdb()
    # prepare a cursor object using cursor() method
    if available == "true":
        available = 1
    else:
        available = 0
    z = 0
    try:
        curcheck = db.cursor()
        paramscheck = "SELECT * FROM `availability` WHERE store_ID = (%s) \
                        AND item_name = (%s)"

        curcheck.execute(paramscheck, (storeid, itemname))
        z = curcheck.rowcount
        if  z>0:
            cur2 = db.cursor()
            params = "UPDATE `availability` SET available = (%s) WHERE \
                        store_ID = (%s) AND item_name = (%s)"
            cur2.execute(params, (available, storeid,itemname))
        else:
            cur2 = db.cursor()
            params = "INSERT INTO `availability` (store_id, item_name, available) VALUES (%s, %s,%s)"
            cur2.execute(params, (storeid, itemname, available))
    #check for duplicates, and add to item list
    except:
        pass
    db.commit()
    return "completed"


@app.route('/api/v1/items/remove', methods=['POST', 'GET'])
def postremoveItem():

    if 'itemname' in request.args:
        itemname = (request.args['itemname'])
    else:
        return "Error: No id field provided. Please specify an itemname."
        if 'storeid' in request.args:
            storeid = (request.args['storeid'])
        else:
            return "Error: No id field provided. Please specify an storeid."

        #127.0.0.1:5000/api/v1/items/remove?itemname=[ITEM_NAME]&storeid=[STORE_ID]
        # Open database connection
        db = getdb()
        # prepare a cursor object using cursor() method
        cur = db.cursor()
        params = "DELETE FROM `availability` WHERE item_name = %s AND store_id = %s"
        cur.execute(params,(itemname,storeid))
        db.commit()
        return "completed"

@app.route('/api/v1/store/add', methods=['POST', 'GET'])
def addstore():
    if 'storename' in request.args:
        storename = (request.args['storename'])
    else:
        return "Error: No id field provided. Please specify a storename."
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify a storeid."
    if 'address' in request.args:
        address = (request.args['address'])
    else:
        return "Error: No id field provided. Please specify a address."
    if 'latitude' in request.args:
        latitude = (request.args['latitude'])
    else:
        return "Error: No id field provided. Please specify a latitude."
    if 'longitude' in request.args:
        longitude = (request.args['longitude'])
    else:
        return "Error: No id field provided. Please specify a longitude."

    db = getdb()

    #127.0.0.1:5000/api/v1/store/add?storename=[ITEM_NAME]&storeid=[STORE_ID]&address=[ADDRESS]&latitude=[LATITUDE]&longitude=[LONGITUDE]
    # Open database connection
    try:
        cur = db.cursor()
        params = "INSERT INTO `stores` (storeID, storeName, addr, latitude, longitude, occupancy) \
            VALUES (%s,%s,%s,%s,%s,0)"

        cur.execute(params, (storeid, storename, address, latitude, longitude))

    #check for duplicates, and add to item list
    except:
        pass
    db.commit()
    return "completed"

@app.route('/api/v1/person/add', methods=['POST', 'GET'])
def postaddperson():
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify a storeid."
    #127.0.0.1:5000/api/v1/person/add?storeid=[STORE_ID]
    # Open database connection
    db = getdb()
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "UPDATE `stores` SET occupancy = occupancy+1 WHERE storeid = (%s)"
    cur.execute(params, storeid)
    db.commit()
    return "completed"

@app.route('/api/v1/person/remove', methods=['POST', 'GET'])
def postremoveperson():
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify a storeid."
    #127.0.0.1:5000/api/v1/person/remove?storename=[STORE_ID]
    # Open database connection
    db = getdb()
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "UPDATE `stores` SET occupancy = occupancy-1 WHERE storeid = (%s)"
    cur.execute(params, storeid)
    db.commit()
    return "completed"

def getdb():
	return pymysql.connect(user=__username, passwd=__password,db=__dbname,unix_socket=__unix_socket)


if __name__ == '__main__':
    app.run(debug=True)
