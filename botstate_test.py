#!/usr/bin/env python3

from botstate import BotState
import os


def testSerializingDeserializing():
    try:
        state = BotState("test.pickle")
        state.commit_last_read("2021/12/30-12:35:50")
        state.commit_last_read("2020/12/21-12:35:50")
        state.inc_death_count("Manu")
        state.inc_death_count("Delmas")
        state.inc_death_count("Delmas")
        state.inc_death_count("Delmas")
        state.save()
        state2 = BotState("test.pickle")
        state2.load()
        assertEqual(state2.get_last_commit(), "2021/12/30-12:35:50")
        assertEqual(state2.get_death_count("Manu"), 1)
        assertEqual(state2.get_death_count("Delmas"), 3)
        print("testSerializingDeserializing : Sucess !")
    except AssertionError:
        return False
    finally:
        os.remove("test.pickle")


def assertEqual(a, b):
    if a != b:
        print("Expect %s equals to %s but was not" % (a, b))
    assert a == b


if __name__ == "__main__":
    testSerializingDeserializing()
    print("Done !")
