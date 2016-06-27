from gcm import GCM
from scanner.mongo import get_gcm_list
import json

################################################################################
# GCM INIT
################################################################################

class Event(object):
    VALUE_CHANGED = "VALUE_CHANGED"
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"

    def __init__(self, noderef, moderef, evtype = "VALUE_CHANGED", parameters = [], oldvalues = [], newvalues = []):
        self.noderef = noderef
        self.moderef = moderef
        self.evtype = evtype
        self.parameters = parameters
        self.oldvalues = oldvalues
        self.newvalues = newvalues

        print "Created event %s %s %s %s %s %s" % (str(noderef), str(moderef.to_dict()), self.evtype, self.parameters, self.oldvalues, self.newvalues)

    def to_dict(self):
        return {
                'node': self.noderef.to_dict(),
                'event': {
                    'type': self.evtype,
                    'mode_name': self.moderef.name,
                    'params': self.parameters,
                    'oldvalues': self.oldvalues,
                    'newvalues': self.newvalues
                }
            }

    def to_json(self):
        return json.dumps(self.to_dict())

class Notifier(object):

    def __init__(self):
        self.API_KEY = "AIzaSyAh1LQr0p_0qB6b4RKhrMr_nxPtjxZfqiI"
        self.event_queue = []

    def add_event(self, event):
        self.event_queue.append(event)

    def process_queue(self, max_sent = 64):
        """ Processes queue
        Sends a maximum of max_sent messages in one call
        returns number of messages sent
        """
        sent = 0
        while sent < max_sent and len(self.event_queue) > 0:
            event = self.event_queue.pop(0)
            print "Sending message %s" % event.to_json()
            self._send_message(get_gcm_list(), event.to_json())  #TODO in a very far future, choose regid based on USERID (yeah users, with login and password...)
            sent = sent + 1
        return sent

    def _send_message(self, reg_id_list, json_to_send):
        gcm = GCM(self.API_KEY)
        data = json_to_send

        print "Sending this data:"
        print "%s" % str(data)
        # Downstream message using JSON request
        #TODO fix "COULD NOT BE PARSED AS JSON" error...
        response = gcm.json_request(registration_ids=reg_id_list, data=data)

        # Downstream message using JSON request with extra arguments
        #res = gcm.json_request(
        #            registration_ids=reg_ids, data=data,
        #                collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600
        #                )

        # Topic Messaging
        #topic = 'topic name'
        #gcm.send_topic_message(topic=topic, data=data)

