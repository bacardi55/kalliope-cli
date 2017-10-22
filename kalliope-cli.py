#!/usr/bin/python
# coding: utf-8

import os
import atexit
import readline
import requests
import re

from cmd2 import Cmd

import logging
logging.basicConfig(filename='./debug.log',level=logging.DEBUG)

def main():
    """
    Configuration
    """
    host = 'http://localhost:5000'
    login= 'admin'
    password = 'secret'
    history_file = '~/.kalliopecli_history'
    no_voice_flag = "true"


    history_file = os.path.expanduser('~/.kalliopecli_history')
    if not os.path.exists(history_file):
        with open(history_file, "w") as fobj:
            fobj.write("")
    readline.read_history_file(history_file)
    atexit.register(readline.write_history_file, history_file)

    app = KalliopeCli(host, (login, password), no_voice_flag)
    app.debug = True
    app.quiet = True
    app.echo = True
    app.cmdloop()


class KalliopeCli(Cmd):

    def __init__(self, host, credentials, no_voice_flag):
        Cmd.__init__(self)

        self.host = host
        self.credentials = credentials
        self.no_voice_flag = no_voice_flag
        self.settable.update({'no_voice_flag': 'If the no_voice flag should be used in the API parameters'})

        self.prompt = self.colorize(self.colorize("Kalliope → ", "bold"), "blue")
        self.intro = self.colorize("*** Welcome to Kalliopé ClI tool ***", "green")
#        # Get all orders
#        resp = requests.get(self.host + '/synapses', auth=self.credentials)
#        synapses = resp.json()
#
#        orders = []
#        for synapse in synapses['synapses']:
#            for signal in synapse['signals']:
#                if signal['name'] == "order":
#                    orders.append(signal['parameters'])
#
#        self.orders = orders
#        logging.debug(self.orders)


    def do_order(self, line):
        self.send_order(line)

    def default(self, line):
        self.send_order(line)

    def send_order(self, order):
        if order:
            resp = requests.post(self.host + '/synapses/start/order', auth = self.credentials, data = '{"order": "' + order + '", "no_voice": "' + self.no_voice_flag + '"}', headers = {'Content-Type': 'application/json'})
            if resp.status_code >= 200 and resp.status_code < 300:
                values = resp.json()
                orders = 'Matched orders: ' + ', '.join("%s" % (val) for (val) in self.get_matched_orders(values['matched_synapses']))
                messages = 'Response: ' + ', '.join("%s" % (val) for (val) in self.get_generated_messages(values['matched_synapses']))
                self.pfeedback(self.colorize(orders, 'cyan'))
                self.poutput(self.colorize(self.colorize(messages, 'green'), 'bold'))

            else:
                print(self.colorize(str(resp.status_code), "red"))

    def get_matched_orders(self, synapses):
        orders = []
        for synapse in synapses:
            orders.append(synapse['matched_order'])

        logging.debug(orders)
        return orders

    def get_generated_messages(self, synapses):
        messages = []
        for synapse in synapses:
            for gm in synapse['neuron_module_list']:
                messages.append(gm['generated_message'])

        logging.debug(messages)
        return messages

if __name__ == '__main__':
    main()
