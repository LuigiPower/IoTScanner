import netifaces
import httplib
import json
import sys
import traceback
import random
#from netaddr import IPNetwork
#from netaddr import IPAddress
#from netaddr import iter_iprange
from threading import Thread
from iotgcm import Notifier
from iotgcm import Event
import time

current_milli_time = lambda: int(round(time.time() * 1000))

################################################################################
# NODE INITIALIZATION
################################################################################
class IOperatingMode(object):
    """ IoTMode helper class
    An IoTMode has it's name and it's parameters
    name is mode type ('gpio_mode', 'composite_mode'...)
    parameters is a dict object containing all it's parameters,
    depending on mode type
    """
    STATUS = 'status'

    success = { STATUS: "OK" }
    failure = { STATUS: "ERR" }

    def __init__(self, name, parameters):
        self.noderef = None
        self.name = name
        self.parameters = parameters

    def update_data(self):
        #print "Updating data of %s" % str(self)
        pass

    def update_test_data(self):
        #print "Updating test data of %s" % str(self)
        pass

    def set_node_reference(self, noderef):
        self.noderef = noderef

    def set_parameter(self, key, value, notify = True):
        """ Set specified parameter to value
        Also notifies any observers
        """
        oldvalue = self.parameters[key]
	self.parameters[key] = value

        if notify:
            print "Notifying node %s about %s on %s with values %s" % (self.noderef.name, self.name, str(Event.VALUE_CHANGED), str(value))
            event = Event(self.noderef, self, Event.VALUE_CHANGED, [key], [oldvalue], [value])
            Scanner.notifier.add_event(event)

    def get_parameter(self, parameter):
        """ Get specified parameter """
        return self.parameters[parameter]

    def do_test_command(self, command, json_parameters):
        print "Got command %s with params %s" % (command, str(json_parameters))
        if command.startswith("basic/set/mode/"):
            split = command.split('/')
            print "Split is %s" % str(split)
            if len(split) < 3:
                return self.failure
            newmode = split[3]
            modetoset = stringToMode(newmode, json_parameters)
            self.noderef.mode = modetoset
            return self.success
        return False

    def to_dict(self):
        """ Gets this mode as a dictionary """
        return {
                'name': self.name,
                'params': self.parameters
            }

    def to_json(self):
        return json.dumps(self.to_dict())


class BasicMode(IOperatingMode):
    """ Basic Mode
    Allows
        /scanning/beacon
        /init/set/mode/<modename>
    """
    NAME = "basic_mode"

    def __init__(self, parameters = {}):
        super(BasicMode, self).__init__(name = BasicMode.NAME, parameters = parameters)

    def update_data(self):
        super(BasicMode, self).update_data()
        try:
            self.noderef.send_command("/scanning/beacon")
        except:
            #Node is dead?
            #TODO notify DISCONNECTED
            pass

    def update_test_data(self):
        #print "Updating test data of %s" % str(self)
        pass

    def do_test_command(self, command, json_parameters):
        result = super(EmptyMode, self).do_test_command(command, json_parameters)
        if result:
            return result
        return False


class EmptyMode(IOperatingMode):
    """ Empty Mode
    Allows nothing
    """
    NAME = "empty_mode"

    def __init__(self, parameters = {}):
        super(EmptyMode, self).__init__(name = EmptyMode.NAME, parameters = parameters)

    def update_data(self):
        super(EmptyMode, self).update_data()

    def update_test_data(self):
        #print "Updating test data of %s" % str(self)
        super(EmptyMode, self).update_test_data()

    def do_test_command(self, command, json_parameters):
        result = super(EmptyMode, self).do_test_command(command, json_parameters)
        if result:
            return result
        return False


class SensorMode(IOperatingMode):
    """ GPIO Read Mode
    Allows
        /sensor<id>/value
    """
    NAME = "sensor_mode"

    ID = 'id'
    SENSOR_DESCRIPTION = 'sensor_description'
    UNIT_TYPE = 'unit_type'
    UNIT_SYMBOL = 'unit_symbol'
    CURRENT_VALUE = 'current_value'
    VALUE_HISTORY = 'value_history'
    TIME_MILLIS = 'time_millis'

    random_min = 0
    random_max = 100
    maximum_values = 10

    def __init__(self, sensorid = 0, name = "sensor_mode", parameters = None):
        if parameters is None:
            parameters = {
                SensorMode.ID: sensorid,
                SensorMode.VALUE_HISTORY: [],
                SensorMode.SENSOR_DESCRIPTION: "Temperatura",
                SensorMode.UNIT_TYPE: "Temperatura",
                SensorMode.UNIT_SYMBOL: "°C"
            }
        super(SensorMode, self).__init__(name, parameters = parameters)

    def do_test_command(self, command, json_parameters):
        result = super(SensorMode, self).do_test_command(command, json_parameters)
        if result:
            return result

        print "SensorMode do_test_command command %s" % command
        if command == "sensor%s/set/description" % self.get_parameter(SensorMode.ID):
            description = json_parameters['description']
            self.set_parameter(SensorMode.SENSOR_DESCRIPTION, description)
        elif command == "sensor%s/set/unit_type" % self.get_parameter(SensorMode.ID):
            unit_type = json_parameters['unit_type']
            self.set_parameter(SensorMode.UNIT_TYPE, unit_type)
        elif command == "sensor%s/set/unit_symbol" % self.get_parameter(SensorMode.ID):
            unit = json_parameters['unit']
            self.set_parameter(SensorMode.UNIT_SYMBOL, unit)
        elif command == "sensor%s/value" % self.get_parameter(SensorMode.ID):
            return {
                    SensorMode.VALUE_HISTORY: self.get_parameter(SensorMode.VALUE_HISTORY),
                    SensorMode.ID: self.get_parameter(SensorMode.ID)
                }
        else:
            return False

    def update_data(self):
        super(SensorMode, self).update_data()
        result = self.noderef.send_command("/sensor%d/value" % self.get_parameter(SensorMode.ID))
        val = result[SensorMode.CURRENT_VALUE]
        self.set_parameter(SensorMode.CURRENT_VALUE, val)

    def update_test_data(self):
        super(SensorMode, self).update_test_data()
        oldhistory = list(self.get_parameter(SensorMode.VALUE_HISTORY))
        val = random.randint(self.random_min, self.random_max)

        oldhistory.append({
            SensorMode.CURRENT_VALUE: val,
            SensorMode.TIME_MILLIS: current_milli_time()
        })

        if len(oldhistory) > self.maximum_values:
            del oldhistory[0]

        self.set_parameter(SensorMode.VALUE_HISTORY, oldhistory)


class GPIOReadMode(IOperatingMode):
    """ GPIO Read Mode
    Allows
        /gpio<pin>
    """
    NAME = "gpio_read_mode"

    GPIO = 'gpio'

    def __init__(self, pin = 0, name = "gpio_read_mode", parameters = None):
        if parameters is None:
            parameters = {
                GPIOReadMode.GPIO: pin,
                IOperatingMode.STATUS: 0
            }
        super(GPIOReadMode, self).__init__(name, parameters = parameters)

    def update_data(self):
        super(GPIOReadMode, self).update_data()
        result = self.noderef.send_command("/gpio%d" % self.get_parameter(GPIOReadMode.GPIO))

        json.loads(result) #TODO check this
        oldval = self.get_parameter(IOperatingMode.STATUS)
        val = 0 #TODO CHANGE TO 0 ELSE NOTHING WORKS
        if result['status'] == IOperatingMode.HIGH:
            val = 1

        if  val != oldval:
            self.set_parameter(IOperatingMode.STATUS, val)

    def update_test_data(self):
        super(GPIOReadMode, self).update_test_data()

        oldval = self.get_parameter(IOperatingMode.STATUS)
        val = random.randint(0, 1)

        if  val != oldval:
            self.set_parameter(IOperatingMode.STATUS, val)

    def do_test_command(self, command, json_parameters):
        result = super(GPIOReadMode, self).do_test_command(command, json_parameters)
        if result:
            return result

        if command == "gpio%d" % self.get_parameter(GPIOReadMode.GPIO):
            return self.parameters
        else:
            return False


class GPIOMode(GPIOReadMode):
    """ GPIO Mode
    Allows
        /gpio<pin>
        /gpio<pin>/<value>
    """
    NAME = "gpio_mode"

    GPIO = 'gpio'

    def __init__(self, pin = 0, parameters = None):
        super(GPIOMode, self).__init__(pin, name = "gpio_mode", parameters = parameters)

    def update_data(self):
        super(GPIOMode, self).update_data()

    def update_test_data(self):
        super(GPIOMode, self).update_test_data()

    def do_test_command(self, command, json_parameters):
        result = super(GPIOMode, self).do_test_command(command, json_parameters)
        if result:
            return result

        print "GPIOMode command is %s and I'm a new version" % command
        if command == "gpio%d/%d" % (self.get_parameter(GPIOMode.GPIO), 1):
            print "GPIOMode setting parameter %s to %s" % (IOperatingMode.STATUS, 1)
            self.set_parameter(IOperatingMode.STATUS, 1)
            return self.parameters
        elif command == "gpio%d/%d" % (self.get_parameter(GPIOMode.GPIO), 0):
            print "GPIOMode setting parameter %s to %s" % (IOperatingMode.STATUS, 0)
            self.set_parameter(IOperatingMode.STATUS, 0)
            return self.parameters
        elif command.startswith("gpio%d" % self.get_parameter(GPIOMode.GPIO)):
            if json_parameters == None:
                return self.parameters
            else:
                self.parameters = json_parameters #set the new parameters...
        else:
            return False


class CompositeMode(IOperatingMode):
    """ Composite Mode
    A container for any number of modes
    can be nested inside other composite modes
    """
    NAME = "composite_mode"

    MODES = 'modes'

    def __init__(self, parameters = None):
        if parameters is None:
            parameters = {
                CompositeMode.MODES: []
            }
        super(CompositeMode, self).__init__(name = "composite_mode", parameters = parameters)

    def update_data(self):
        """ Updates data on all submodes """
        super(CompositeMode, self).update_data()
        for mode in self.get_parameter(CompositeMode.MODES):
            mode.update_data()

    def update_test_data(self):
        super(CompositeMode, self).update_test_data()
        for mode in self.get_parameter(CompositeMode.MODES):
            mode.update_test_data()

    def add_mode(self, mode):
        """ Adds a mode to this composite mode """
        mode.set_node_reference(self.noderef)
        self.parameters['modes'].append(mode)

    def _modes_to_dict(self):
        ret = []
        for mode in self.parameters['modes']:
            ret.append(mode.to_dict())
        return ret

    def to_dict(self):
        ret = {
                'name': self.name,
                'params': {
                    'modes': self._modes_to_dict()
                }
            }
        return ret

    def do_test_command(self, command, json_parameters):
        result = super(CompositeMode, self).do_test_command(command, json_parameters)
        if result:
            return result

        #print "CompositeMode doing test command %s" % command
        if command.startswith("composite/add/mode/"):
            split = command.split('/')
            newmode = split[3]
            modetoset = stringToMode(newmode, json_parameters)
            self.noderef.mode = modetoset
            return self.success
        elif command.startswith("composite/del/mode/"):
            split = command.split('/')
            return self.failure #TODO instant failure as I have no ID to identify modes with
        else:
            ret = {}
            for mode in self.parameters['modes']:
                result =  mode.do_test_command(command, json_parameters)
                if result:
                    ret = result
                    break
            return ret


class IoTNode(object):
    """ IoTNode helper class
    An IoTNode has its IPAddress, its name and its mode
    ip is an IPAddress (or a string)
    name is a string
    mode is an instance of OperatingMode
    values is a dictionary containing node status
    """
    PORT_NUMBER = 5575

    def __init__(self, ip, name, mode):
        self.ip = ip
        self.name = name
        self.mode = mode
        self.mode.set_node_reference(self)

    def update_data(self):
        """ Asks current mode to update it's data """
        self.mode.update_data()

    def update_test_data(self):
        self.mode.update_test_data()

    def send_test_command(self, command, json_parameters):
        return self.mode.do_test_command(command, json_parameters)

    def send_command(self, command):
        """ Send the specified command to this node
        ex.:
            /gpio1/0
            /gpio1
            /dashboard
            ...
        """
        #print "Sending command to %s" % self.ip
        conn = httplib.HTTPConnection(str(self.ip), IoTNode.PORT_NUMBER)
        conn.request("GET", command)
        response = conn.getresponse()
        return response.read()

    def to_dict(self):
        json = {
                'name': self.name,
                'ip': self.ip,
                'mode': self.mode.to_dict()
            }
        return json

    def to_json(self):
        return json.dumps(self.to_dict())

    def get_value(self, value_name):
        return self.values[value_name]


class Scanner(object):

    def __init__(self, auto_scan = False, init_test = False, start_handler = True):
        self.esplist = {}
        self.running = False
        self.handler = None
        Scanner.notifier = Notifier()

        if auto_scan:
            self.run_scan()

        if init_test:
            random.seed(None)
            self._create_test_data()

        if start_handler:
            self.start_handler_thread()

    def handler_thread(self):
        while self.running:
            #TODO do stuff like polling the nodes and making notifications
            time.sleep(30)
            #self.poll_found_nodes()
            self.poll_found_nodes_test()
            Scanner.notifier.process_queue()
            pass

    def stop_handler_thread(self):
        #print "Stopping handler thread..."
        self.running = False

    def start_handler_thread(self):
        self.handler = Thread(target = self.handler_thread)
        self.running = True
        self.handler.start()

    def poll_found_nodes_test(self):
        for name in self.esplist:
            self.esplist[name].update_test_data()

    def poll_found_nodes(self):
        """ Asks all found nodes for a data update
        Takes a while, done by the handler thread
        """
        for name in self.esplist:
            #print "polling %s" % str(name)
            #TODO decomment this
            self.esplist[name].update_data()

    def get_node_map(self):
        return self.esplist

    def get_node(self, nodename):
        return self.esplist[nodename]

    def get_json(self):
        return json.dumps(self.get_node_map())

    def get_node_json(self, nodename):
        return self.get_node(nodename).to_json()

    def _create_test_data(self):
        self.esplist = {}

        gpiomode0 = GPIOMode(2)
        gpiomode0.set_parameter(IOperatingMode.STATUS, 1, notify = False)
        esp0 = IoTNode('192.168.1.14', 'Ingresso', gpiomode0)
        self.esplist[esp0.name] = esp0

        sensormode0 = SensorMode(1)
        sensormode0.random_min = 31
        sensormode0.random_max = 34
        sensormode0.set_parameter(SensorMode.VALUE_HISTORY, [], notify = False)
        sensormode0.set_parameter(SensorMode.SENSOR_DESCRIPTION, "Temperatura della cucina", notify = False)
        sensormode0.set_parameter(SensorMode.UNIT_TYPE, "Celsius", notify = False)
        sensormode0.set_parameter(SensorMode.UNIT_SYMBOL, "°C", notify = False)
        sensore_cucina = IoTNode('192.168.1.44', 'Cucina', sensormode0)
        self.esplist[sensore_cucina.name] = sensore_cucina

        compositemode1 = CompositeMode()
        esp1 = IoTNode('192.168.1.74', 'Cantina', compositemode1)
        gpiomode11 = GPIOReadMode(1)
        gpiomode11.set_parameter(IOperatingMode.STATUS, 1, notify = False)
        compositemode12 = CompositeMode()
        compositemode1.add_mode(compositemode12)
        gpiomode12 = GPIOMode(2)
        gpiomode12.set_parameter(IOperatingMode.STATUS, 0, notify = False)
        compositemode12.add_mode(gpiomode12)
        #cosemode1 = IOperatingMode("cose_mode", {'coseparams': 42})
        sensormode1 = SensorMode(1)
        sensormode1.random_min = 26
        sensormode1.random_max = 29
        sensormode1.set_parameter(SensorMode.VALUE_HISTORY, [], notify = False)
        sensormode1.set_parameter(SensorMode.SENSOR_DESCRIPTION, "Temperatura della cantina", notify = False)
        sensormode1.set_parameter(SensorMode.UNIT_TYPE, "Celsius", notify = False)
        sensormode1.set_parameter(SensorMode.UNIT_SYMBOL, "°C", notify = False)
        compositemode1.add_mode(sensormode1)
        compositemode1.add_mode(gpiomode11)
        #compositemode1.add_mode(cosemode1)
        self.esplist[esp1.name] = esp1

    def get_node_list(self):
        tosend = []

        for esp in self.esplist:
            #print "ESP: %s" % esp
            node = self.esplist[esp]
            #print "ESP: %s %s" % (esp, str(node))
            tosend.append({ "name": node.name, "ip": node.ip, "mode": node.mode.to_dict() })

        #print str(tosend)

        return tosend

    def get_local_ips(self):
        local_ip_addresses = []
        interfaces = netifaces.interfaces()

        for interface in interfaces:
            try:
                for addresses in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                    if addresses['addr'].startswith("127."):
                        continue

                    #print addresses
                    local_ip_addresses.append(addresses)
            except:
                pass

        return local_ip_addresses

    def mask_to_count(self, mask):
        count = 0
        bit = 1
        split = mask.rsplit('.')
        binarymask = []
        numbermask = []

        for number in split:
            n = int(number)
            numbermask.append(n)
            while bit < 256:
                if n & bit == 0:
                    binarymask.append(0)
                else:
                    binarymask.append(1)
                    count += 1
                    bit *= 2
        #for c in mask.bits():
        #    if c == '1':
        #        count = count + 1
        return (count, binarymask, numbermask)

    def get_network_address(self, address, numbermask):
        split = address.rsplit('.')
        numbernetwork = []
        for i in range(0, len(split)):
            n = int(split[i])
            numbernetwork.append(n & numbermask[i])
        return numbernetwork

    def run_scan(self):
        """ Runs a network scan
        may take a few minutes (does a HTTP request on each device connected to the network)
        """
        #print "Running scan..."
        iplist = self._get_local_ip_list()
        esplist = self._scan_local_ips(iplist)
        return esplist

    def get_broadcast_address(self, numberaddress, numbermask):
        broadcast = []

        for i in range(0, len(numberaddress)):
            number = (numberaddress[i] & numbermask[i]) | ~numbermask[i]
            broadcast.append(number & 255)
        return broadcast

    def ipcmp(self, numberipa, numberipb):
        for i in range(0, len(numberipa)):
            if numberipa[i] != numberipb[i]:
                return False
        return True

    def iter_iprange(self, numbernetwork, numbermask):
        iprange = []
        #iter_bounds = []
        actual = []
        last_ip = numbernetwork

        broadcast = self.get_broadcast_address(numbernetwork, numbermask)
        #for i in xrange(0, len(broadcast)):
        #    iter_bounds[i] = (numbernetwork[i], broadcast[i])

        actual = list(numbernetwork)
        current_number = len(actual) - 1

        while not self.ipcmp(actual, broadcast):
            # 192.168.0.0
            if actual[current_number] < broadcast[current_number]:
                actual[current_number] += 1
                if current_number < len(actual) - 1:
                    current_number += 1
            else: #actual[current_number] is 255 (or similar)
                actual[current_number] = numbernetwork[current_number]
                if current_number > 0:
                    current_number -= 1

            new_list = list(actual)
            iprange.append(new_list)

        return iprange

    def _get_local_ip_list(self):
        """ Gets list of this server's interfaces
        to get their local ip
        """
        local_ip_addresses = self.get_local_ips()
        iplist = []

        #print "Addresses %s" % str(local_ip_addresses)
        for address in local_ip_addresses:
            (count, binarymask, numbermask) = self.mask_to_count(address['netmask'])
            numbernetwork = self.get_network_address(address['addr'], numbermask)

            iterator = self.iter_iprange(numbernetwork, numbermask)
            for ip in iterator:
                iplist.append(ip)

        return iplist

    def _scan_local_ips(self, iplist):
        """ Scans given list of networks for ESPs
        or similarly configured HTTP servers
        """
        #TODO magari implementare la cosa che diceva il prof (il nodo fa da server a cui questo si collega per essere configurato. una volta che il nodo e' stato configurato, si passa al normale funzionamento [magari farlo come parametro opzionale? comunque servono 2 interfaccie per fare cio' che dice il prof, per quanto sia essenziale... {in caso staccare momentaneamente il server per collegarsi all'ESP, ma questo tira giu tutto ogni volta che si aggiunge un nodo}])
        esplist = {}

        number = 0
        for ip in iplist:
            try:
                strip = "%d.%d.%d.%d:%d" % (ip[0], ip[1], ip[2], ip[3], IoTNode.PORT_NUMBER)
                if strip != "10.40.0.88":
                    continue
                #print "Doing HTTPConnection to %s" % strip
                conn = httplib.HTTPConnection(strip)
                conn.request("GET", "/scanning/beacon")
                #TODO fare un POST invece di GET, inviando l'ip del server
                #TODO l'ip del server dovrebbe corrispondere all'interfaccia corretta... (basta passarlo insieme alla lista (quindi non passare una lista ma un dizionario in cui a ogni interfaccia corrisponde la sua lista di ip))
                response = conn.getresponse()

                data = response.read()
                #print "FOUND ESP, data is %s" % data
                #TODO esp must give back name and current mode(s)
                jsondata = json.loads(data)
                extras = jsondata['extras']

                gpiomode0 = GPIOMode(2)
                gpiomode0.set_parameter(IOperatingMode.STATUS, 1, notify = False)
                node = IoTNode(extras['ip'], extras['name'], gpiomode0)
                #TODO mode...

                self.esplist[extras['name']] = node
                #print self.esplist
                number += 1
            except :
                #print "Unexpected error", sys.exc_info()[0]
                print traceback.format_exc()
                pass

        #print self.esplist

        return esplist

def stringToMode(name, json):
    if name == BasicMode.NAME:
        return BasicMode(parameters = json)
    elif name == EmptyMode.NAME:
        return EmptyMode(parameters = json)
    elif name == GPIOMode.NAME:
        return GPIOMode(parameters = json)
    elif name == GPIOReadMode.NAME:
        return GPIOReadMode(parameters = json)
    elif name == SensorMode.NAME:
        return SensorMode(parameters = json)
    else:
        return IOperatingMode(name, parameters)

################################################################################
#   EXAMPLE DATA
#
#    esplist = {
#            "esp0": {
#                "ip": "192.168.1.14",
#                "mode": {
#                    "name": "gpio_mode",
#                    "params": {
#                        "gpio": 2,
#                        "status": 1
#                    }
#                }
#            },
#            "esp1": {
#                "ip": "192.168.1.74",
#                "mode": {
#                    "name": "composite_mode",
#                    "params": {
#                        "modes": [
#                            {
#                                "name": "gpio_mode",
#                                "params": {
#                                    "gpio": 1,
#                                    "status": 1
#                                }
#                            },
#                            {
#                                "name": "composite_mode",
#                                "params": {
#                                    "modes": [
#                                        {
#                                            "name": "gpio_mode",
#                                            "params": {
#                                                "gpio": 2,
#                                                "status": 0
#                                            }
#                                        }
#                                    ]
#                                }
#                            },
#                            {
#                                "name": "sticazzi_mode",
#                                "params": {
#                                    "sticazziparams": 42
#                                }
#                            }
#                        ]
#                    }
#                }
#            }
#        }
#
################################################################################
