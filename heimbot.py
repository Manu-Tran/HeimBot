#!/usr/bin/env python3

import time
import os
import logging
import requests

from botstate import BotState
from helper import parse_line, get_next_offset

logging.basicConfig(filename="/tmp/heimbot.log", level=logging.DEBUG)


class HelmTeleBot:
    # Interacts with telegram
    def __init__(
        self, channel_id: str, data_dir: str, bot_token: str, host, serverLogFile: str
    ) -> None:
        self.channel_id = channel_id
        self.data_dir = data_dir
        self.host = host
        self.bot_token = bot_token
        self.log_loc = serverLogFile
        self.state = BotState(data_dir + "/botstate.pickle")
        self.cur_log_size = os.path.getsize(serverLogFile)
        self.cur_players = dict()
        self.spin_up()

    def send_to_telegram(self, text):
        logging.info("Sending " + text)
        params = {"text": text}
        url = "https://api.telegram.org/bot"
        r = requests.get(
            url + self.bot_token + "/sendMessage?chat_id=" + self.channel_id,
            params=params,
        )
        logging.info(r.json())

    def spin_up(self):
        self.logfile = None
        elapsed = 0
        while self.logfile is None:
            try:
                self.logfile = open(self.log_loc, "r")
            except:
                time.sleep(1)
                elapsed = elapsed + 1
                if elapsed > 20:
                    elapsed = 0
                    raise Exception("Timed out opening log file!")
        # Skip to last offset
        for line in self.logfile:
            offset = get_next_offset(line)
            last_commit = self.state.get_last_commit()
            if offset and offset < last_commit:
                pass

    def run(self):
        try:
            while True:
                line = self.logfile.readline()
                if line != "":
                    self.on_new_line(line)

                # Detect if the log file has been refreshed
                try:
                    new_log_size = os.path.getsize(self.log_loc)
                except:
                    new_log_size = 0
                # print(new_log_size, self.cur_log_size)
                if new_log_size < self.cur_log_size:
                    logging.info("Detecting log file deletion")
                    self.cur_log_size = new_log_size
                    self.spin_up()
                else:
                    self.cur_log_size = new_log_size
                time.sleep(1)
        except Exception as e:
            print("Error while running %s" % e)

    def on_new_line(self, line):
        offset = get_next_offset(line)
        last_commit = self.state.get_last_commit()
        if offset > last_commit:
            resp = parse_line(self.state, line, self.cur_players)
            if resp != "":
                self.send_to_telegram(resp)
            self.state.commit_last_read(offset)
        for line in self.logfile:
            offset = get_next_offset(line)
            last_commit = self.state.get_last_commit()
            if offset > last_commit:
                resp = parse_line(self.state, line, self.cur_players)
                if resp != "":
                    self.send_to_telegram(resp)
                self.state.commit_last_read(offset)


if __name__ == "__main__":
    logging.info("Starting telegram/valheim bridge....")
    data_dir = os.environ.get("VALHEIM_DIR_PATH", "")
    bot = HelmTeleBot(
        os.environ["TELEGRAM_CHANNEL_ID"],
        data_dir,
        os.environ["TELEGRAM_BOT_TOKEN"],
        os.environ.get("VALHEIM_HOST", "127.0.0.1"),
        os.environ.get("VALHEIM_SERVER_LOG_PATH", "/log/valheim_server.log"),
    )
    bot.run()
