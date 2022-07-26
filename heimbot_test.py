#!/usr/bin/env python3

from botstate import BotState
from heimbot import HelmTeleBot
import os
import subprocess
import signal


def testSerializingDeserializing():
    try:
        with open("./valheim_server.log", "w") as f:
            f.write("Serveur starting")

        bot = HelmTeleBot(
            "tg_id",
            ".",
            "tg_token",
            os.environ.get("VALHEIM_HOST", "127.0.0.1"),
            "./valheim_server.log",
        )
        telegramMock = []
        bot.send_to_telegram = lambda x: telegramMock.append(x)
        # p = Popen(['sleep', '2', "&&", "echo", "02/21/2021 19:02:40: Got character ZDOID from Kvykv : 4072265675:3", ">>", "./valheim_server.log"])
        command = 'sleep 1 && echo "02/21/2021 19:02:40: Got character ZDOID from Kvykv : 4072265675:3" >> ./valheim_server.log && echo "02/21/2021 19:05:40: Got character ZDOID from Kvykv : 0:0" >> ./valheim_server.log && echo "02/21/2021 19:10:40: Got character ZDOID from Kvykv : 4072265675:3" >> ./valheim_server.log'
        ret = subprocess.run(command, capture_output=True, shell=True)

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(3)

        bot.run()

        assertEqual(len(telegramMock), 2)
        assertEqual(telegramMock[0], "Kvykv HAS ARRIVED")
        assertEqual(bot.state.get_last_commit(), "2021/02/21-19:10:40")
        assertEqual(bot.state.get_death_count("Kvykv"), 1)
        print("Success !")

    except AssertionError:
        return False
    finally:
        os.remove("./valheim_server.log")
        os.remove("./botstate.pickle")


def handler(signum, frame):
    raise Exception("")


def assertEqual(a, b):
    if a != b:
        print("Expect %s equals to %s but was not" % (a, b))
    assert a == b


if __name__ == "__main__":
    testSerializingDeserializing()
    print("Done !")
