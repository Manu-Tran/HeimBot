#!/usr/bin/env python3
import re
import pickle
import logging
import os.path
from helper import verify_date

logging.basicConfig(filename="/tmp/heimbot.log",level=logging.DEBUG)

class BotState:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.state = dict()
        self.state.setdefault("last_commit", "")
        self.state.setdefault("death_count", dict())
        self.load()

    def load(self) -> bool:
        if not(os.path.exists(self.file_path)):
            logging.info("File %s not found for loading" % self.file_path)
            return False
        try:
            with open(self.file_path, 'rb') as f:
                data = pickle.load(f)
            self.state["last_commit"] = data["last_commit"]
            for name in data["death_count"]:
                self.state["death_count"][name] = int(data["death_count"][name])
            return True
        except Exception as e:
            logging.error("Error while loading : %s" % e)
            return False


    def save(self) -> bool:
        try:
            if (os.path.exists(self.file_path)):
                # Check if old_state is newer
                old_state = BotState(self.file_path)
                if old_state.get_last_commit() > self.state["last_commit"]:
                    logging.info("Could not save : commit date too young")
                    return False
            with open(self.file_path, 'wb') as f:
                pickle.dump(self.state, f, protocol=pickle.HIGHEST_PROTOCOL)
                return True
        except Exception as e:
            logging.error("Error while saving : %s" % e)
            return False

    def commit_last_read(self, date: str) -> None:
        if verify_date(date):
            if self.state.get("last_commit", "") < date:
                self.state["last_commit"] = date
                self.save()
            else:
                logging.warn("Commited early read")
        else:
            logging.warn("Date not valid")

    def get_last_commit(self) -> str:
        return self.state["last_commit"]

    def inc_death_count(self, name: str) -> int:
        self.state["death_count"][name] = self.state["death_count"].get(name, 0) + 1
        self.save()
        return self.state["death_count"][name]

    def get_death_count(self, name: str) -> int:
        return self.state["death_count"].get(name, 0)
