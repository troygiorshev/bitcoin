#!/usr/bin/env python3
# Copyright and whatever
"""
Dostring here

"""

import sys

sys.path.append('test/functional')

from test_framework.messages import *
from test_framework.mininode import MESSAGEMAP

import argparse
from typing import Any, List
import json
from pathlib import Path
from io import BytesIO

TIME_SIZE = 8
LENGTH_SIZE = 4
COMMAND_SIZE = 12

def to_jsonable(obj: Any) -> Any:
    ret = {}
    # The msg objects don't generally include "msgtype" in their __slots__
    if hasattr(obj, "msgtype"):
        ret["msgtype"] = getattr(obj, "msgtype", None).decode()
    if hasattr(obj, "__dict__"):
        ret = obj.__dict__
    elif hasattr(obj, "__slots__"):
        for slot in obj.__slots__:
            val = getattr(obj, slot, None)
            ret[slot] = to_jsonable(val)
    elif isinstance(obj, list):
        ret = [to_jsonable(a) for a in obj]
    elif isinstance(obj, bytes):
        ret = obj.hex()
    else:
        ret = obj
    return ret


def process_file(path: Path, messages: List[Any], recv: bool) -> None:
    with open(path, 'rb') as f_in:
        while True:
            tmp_header = f_in.read(TIME_SIZE + LENGTH_SIZE + COMMAND_SIZE)
            if not tmp_header:
                break
            tmp_header = BytesIO(tmp_header)
            time = int.from_bytes(tmp_header.read(TIME_SIZE), "little") # type: int
            command = tmp_header.read(COMMAND_SIZE).split(b'\x00', 1)[0]  # type: bytes
            length = int.from_bytes(tmp_header.read(LENGTH_SIZE), "little") # type: int
            if command not in MESSAGEMAP:
                continue    # For now just skip unrecognized messages
            msg = MESSAGEMAP[command]()
            msg.deserialize(f_in)
            msg_dict = to_jsonable(msg)
            msg_dict["time"] = time
            msg_dict["length"] = length
            msg_dict["recv"] = recv
            messages.append(msg_dict)


def main():
    """Main"""
    # Run with, say, `python contrib/peer_logging/peer-logging-parser.py contrib/peer_logging/**/*.dat`
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "logpaths", nargs='+',
        help="binary message dump files to parse.")
    parser.add_argument("-o", "--output", help="output file.  If unset print to stdout")
    args = parser.parse_args()
    logpaths = [Path(logpath).resolve() for logpath in args.logpaths]
    output = Path(args.output).resolve() if args.output else False

    messages = [] # type: List[Any]
    for log in logpaths:
        process_file(log, messages, "recv" in log.stem)

    messages.sort(key=lambda msg: msg['time']) # Sorting after is faster

    jsonrep = json.dumps(messages)
    if output:
        with open(output, 'w+') as f_out:
            f_out.write(jsonrep)
    else:
        print(jsonrep)

if __name__ == "__main__":
    main()
