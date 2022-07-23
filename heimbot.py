import asyncio
import re
import time
import os
from mimir import parse_line
import logging
import requests
from os.path import dirname


from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

logging.basicConfig(filename="/tmp/heimbot.log",level=logging.DEBUG)
URL = "https://api.telegram.org/bot"

class FacTeleBot():
    # Interacts with telegram
    def __init__(self, channel_id, data_dir, bot_token, host):
        self.channel_id = channel_id
        self.data_dir = data_dir
        self.host = host
        self.bot_token = bot_token

    def send_to_telegram(self, text):
        logging.info("Sending " + text)
        params = { "text" : text}
        #print(text)
        r = requests.get(url=URL+self.bot_token+"/sendMessage?chat_id="+self.channel_id, params=params)
        logging.info(r.json())


class ValLogHandlerV2():
    def __init__(self,fbot, logfile):
        self.fbot = fbot
        self.log_loc = logfile
        self.logfile = None
        self.players = dict()
        self.last_line = ""
        self.spin_up()

    def spin_up(self):
        # When the bridge first starts up, wait for valheim to start and
        # create the log file, then read to the end so we don't duplicate
        # any messages

        self.logfile = None
        elapsed = 0
        while self.logfile is None:
            try:
                self.logfile = open(self.log_loc, 'r')
            except:
                time.sleep(1)
                elapsed = elapsed + 1
                if elapsed > 20:
                    elapsed = 0
                    raise Exception("Timed out opening log file!")
        self.fbot.send_to_telegram("HEIMBOT HAS ARRIVED !!!")

        # read up to last line before EOF
        for line in self.logfile:
            pass

    def run(self):
        while True:
            line = self.logfile.readline()
            if (line != ""):
                self.on_modified(line)
            time.sleep(1)
         
    def on_modified(self, line):
        resp = parse_line(self.players, line)
        if resp != "":
            self.fbot.send_to_telegram(resp)
        for line in self.logfile:
            resp = parse_line(self.players, line)
            if resp != "":
                self.fbot.send_to_telegram(resp)

    def default_handler(self, kind, name):
        self.fbot.send_to_telegram(name)

def regenerateBot():
    data_dir = os.environ.get("VALHEIM_DIR_PATH", ".")
    return HelmTeleBot(os.environ['TELEGRAM_CHANNEL_ID'],
                    data_dir,
                    os.environ["TELEGRAM_BOT_TOKEN"],
                    os.environ.get("FACTORIO_HOST", '127.0.0.1'))

if __name__ == "__main__":
    logging.info("Starting telegram/valheim bridge....")
    data_dir = os.environ.get("VALHEIM_DIR_PATH", "")
    fb =  regenerateBot()
    bot = ValLogHandlerV2(fb, data_dir+"/log/valheim_server.log")
    bot.run()
