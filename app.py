import flask
from flask import request, jsonify
import pymysql
from flaskext.mysql import MySQL
import json

__ip = "35.223.105.218"
__username = "basicUser"
__password = "password"
__dbname = "out_of_stock"

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['MYSQL_HOST'] = __ip
app.config['MYSQL_USER'] = __username
app.config['MYSQL_PASSWORD'] = __password
app.config['MYSQL_DB'] = __dbname

mysql = MySQL()
mysql.init_app(app)



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
    db = pymysql.connect(__ip,__username,__password,__dbname)
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
    db = pymysql.connect(__ip,__username,__password,__dbname)
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "SELECT * FROM outOfStock WHERE store_id = (%s)"
    cur.execute(params, storeid)
    rv = cur.fetchall()
    itemids = []
    for result in rv:
       content = int(result[1])
       itemids.append(content)
    #Create a new cursor for selecing items of certain ID
    payload2 = []
    content2 = {}
    cur2 = db.cursor()
    for each in itemids:
        params = "SELECT * FROM items WHERE itemID = %s"
        cur2.execute(params, each)
        rv2 = cur2.fetchall()
        for result in rv2:
           content2 = {'itemID': str(result[0]),
                    'itemName': str(result[1])}
           payload2.append(content2)
           content2 = {}
    return jsonify(payload2)



@app.route('/api/v1/items/add', methods=['POST'])
def postaddItem():
    if 'itemname' in request.args:
        itemname = (request.args['itemname'])
    else:
        return "Error: No id field provided. Please specify an itemname."
    if 'itemid' in request.args:
        itemid = (request.args['itemid'])
    else:
        return "Error: No id field provided. Please specify an itemid."
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify an storeid."

    #127.0.0.1:5000/api/v1/items/add?itemid=[itemid]&storeid=[STORE_ID]&itemname=[ITEM_NAME]
    # Open database connection
    db = pymysql.connect(__ip,__username,__password,__dbname)
    # prepare a cursor object using cursor() method

    try:
        cur = db.cursor()
        params = "INSERT INTO `items` (itemid,itemName) VALUES (%s, %s)"
        cur.execute(params, (itemid, itemname))
    except:
        pass
    try:
        cur2 = db.cursor()
        params = "INSERT INTO `outOfStock` (store_id, item_id) VALUES (%s, %s)"
        cur2.execute(params, (storeid, itemid))
        #check for duplicates, and add to item list
    except:
        pass
    db.commit()

    return "completed"


@app.route('/api/v1/items/remove', methods=['POST'])
def postremoveItem():
    if 'itemname' in request.args:
        itemname = (request.args['itemname'])
    else:
        return "Error: No id field provided. Please specify an itemname."
    if 'itemid' in request.args:
        itemid = (request.args['itemid'])
    else:
        return "Error: No id field provided. Please specify an itemid."
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify an storeid."

    #127.0.0.1:5000/api/v1/items/remove?itemname=[ITEM_NAME]&storeid=[STORE_ID]&itemid=[ITEM_ID]
    # Open database connection
    db = pymysql.connect(__ip,__username,__password,__dbname)
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "DELETE FROM `outOfStock` WHERE item_id = %s AND store_id = %s"
    cur.execute(params,(itemid,storeid))
    db.commit()
    return "completed"

@app.route('/api/v1/person/add', methods=['POST'])
def postaddperson():
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify a storeid."
    #127.0.0.1:5000/api/v1/person/add?storename=[STORE_ID]
    # Open database connection
    db = pymysql.connect(__ip,__username,__password,__dbname)
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "UPDATE `stores` SET occupancy = occupancy+1 WHERE storeid = (%s)"
    cur.execute(params, storeid)
    db.commit()
    return "completed"

@app.route('/api/v1/person/remove', methods=['POST'])
def postremoveperson():
    if 'storeid' in request.args:
        storeid = (request.args['storeid'])
    else:
        return "Error: No id field provided. Please specify a storeid."
    #127.0.0.1:5000/api/v1/person/remove?storename=[STORE_ID]
    # Open database connection
    db = pymysql.connect(__ip,__username,__password,__dbname)
    # prepare a cursor object using cursor() method
    cur = db.cursor()
    params = "UPDATE `stores` SET occupancy = occupancy-1 WHERE storeid = (%s)"
    cur.execute(params, storeid)
    db.commit()
    return "completed"


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
