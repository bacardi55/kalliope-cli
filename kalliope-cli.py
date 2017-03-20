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


    history_file = os.path.expanduser('~/.kalliopecli_history')
    if not os.path.exists(history_file):
        with open(history_file, "w") as fobj:
            fobj.write("")
    readline.read_history_file(history_file)
    atexit.register(readline.write_history_file, history_file)

    app = KalliopeCli(host, (login, password))
    app.debug = True
    app.echo = True
    app.cmdloop()


class KalliopeCli(Cmd):
    prompt = "KalliopeCLI> "
    intro = "Welcome to Kalliopé ClI tool"

    def __init__(self, host, credentials):
        Cmd.__init__(self)

        self.host = host
        self.credentials = credentials

        # Get all orders
        resp = requests.get(self.host + '/synapses', auth=self.credentials)
        synapses = resp.json()
        orders = []
        for synapse in synapses['synapses']:
            for signal in synapse['signals']:
                orders.append(signal['order'])

        self.orders = orders
        logging.debug(self.orders)

    def do_help(self):
        pass

    def do_list(self):
        pass

    def do_order(self, line):
        if line:
            resp = requests.post(self.host + '/synapses/start/order', auth = self.credentials, data = '{"order": "' + line + '"}', headers = {'Content-Type': 'application/json'})
            if resp.status_code == 200:
                print(self.colorize("200", "green"))
            else:
                print(self.colorize(str(resp.status_code), "red"))

    def complete_order(self, text, line, begidx, endidx):
        command = line[len("order "):]
        logging.debug(command)

        val = []
        logging.debug(self.orders)
        for order in self.orders:
            if re.search(command, order, re.I):
                val.append(order)

        logging.debug(val)
        if len(val) > 0:
            return val
        else:
            return [text]

if __name__ == '__main__':
    main()
