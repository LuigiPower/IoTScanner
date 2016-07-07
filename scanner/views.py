from scanner import app
from scanner.mongo import get_gcm_list
from scanner.mongo import insert_gcm
from scanner.iotnodes import Scanner
from scanner.iotnodes import IoTNode
from scanner.iotgcm import Notifier
from flask import request
from flask import render_template
import time
import json

#TODO access to this should be regulated by a mutex semaphore, handler thread needs at least read access...
iotscanner = Scanner(init_test = True, auto_scan = False)

@app.route('/kill/scanner')
def kill_scanner():
    iotscanner.stop_handler_thread()
    return "killed..."

############################################################################
# NETWORK SCAN
############################################################################

@app.route('/init/scan')
def start_scan():
    print "Starting network scan (might take a while)..."
    iotscanner.run_scan()
    print "Scan completed."
    return str(iotscanner.esplist)

############################################################################

############################################################################
# INDEX
############################################################################

@app.route('/')
def index():
    return render_template('index.html', data=iotscanner.get_node_list())

############################################################################

############################################################################
# GCM TEST
############################################################################

@app.route('/gcm/testmessage')
def send_test_message():
    reg_id_list = get_gcm_list()

    data = {
        "message": "Cose",
        "data": {
            "node": {
                "ip": "192.168.1.14",
                "mode": {
                    "name": "gpio_mode",
                    "params": {
                        "gpio": 2,
                        "status": 1
                    }
                },
                "name": "esp0"
            },
            "event": {
                "type": "VALUE_CHANGED",
                "mode_name": "gpio_read_mode",
                "params": ["status"],
                "oldvalues": [0],
                "newvalues": [1],
                }
            }
        }

    Scanner.notifier._send_message(reg_id_list, data)
    return "Test message sent"

################################################################################

@app.route('/node/list', methods=['GET'])
def show_node_list():
    tosend = iotscanner.get_node_list()
    return json.dumps(tosend)

@app.route('/node/<nodeid>/<path:action>', methods=['GET', 'POST'])
def send_action_to_node(nodeid, action):
    print "Sending %s to %s" % (action, nodeid)
    #TODO send it to the actual node
    return "Sent"

@app.route('/testnode/<nodeid>/<path:action>', methods=['GET', 'POST'])
def send_action_to_test_node(nodeid, action):
    print "Sending %s to test node %s" % (action, nodeid)
    node = iotscanner.get_node(nodeid)
    return json.dumps(node.send_test_command(action))

@app.route('/node/<nodeid>/status')
def get_current_node_status(nodeid):
    return iotscanner.get_node_json(nodeid)

@app.route('/init/testdata')
def load_test():
    return json.dumps(scanner._create_test_data())

@app.route('/gcm/registration', methods=['POST'])
def receive_registration_id():
    regid = request.form['registration_id']
    print "Received registration id POST: %s" % regid
    insert_gcm(regid)
    return "Received registration id %s" % regid

@app.route('/gcm/logout', methods=['POST'])
def remove_registration_id():
    regid = request.form['registration_id']
    print "To remove registration id POST: %s" % regid
    remove_gcm(regid)
    return "Removed registration id %s" % regid

@app.route('/door/test', methods=['GET', 'POST'])
def doortesting():
    testdoor()
    return "ciao"

def testdoor():
    i = 0
    while i < 10000:
        result = send_command("192.168.1.76", "/gpio2")
        print "pass %d result %s" % (i, str(result))
        if "HIGH" in result:
            print "HDFIUOHSAFIODSFAHOF"
            send_message(get_gcm_list(), "CIAO MAMMA SONO IN TV")
        #jsonres = json.loads(result)
        #if jsonres['HIGH']:
        #    print "HIIIIIIIIIIGH"
        time.sleep(1)
        i = i + 1
