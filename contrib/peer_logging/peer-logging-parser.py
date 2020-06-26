#!/usr/bin/env python3
# Copyright and whatever
"""
Dostring here

"""

from typing import Any
import json
import pathlib
from io import BytesIO

import sys
sys.path.append('test/functional')

from test_framework.messages import *
from test_framework.mininode import MESSAGEMAP

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


def process_file(path: pathlib.Path) -> None:
    messages = [] # type: List[Message]
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
            messages.append(msg_dict)
    jsonrep = json.dumps(messages)
    with open(path.with_suffix(".json"), 'w+') as f_out:
        f_out.write(jsonrep)


def main():
    """Main"""
    # This module lives in contrib/peer_logging
    # But should be run from the root directory.
    # And should take basedir as an argument
    basedir = pathlib.Path('peer_logging')
    peerdirs = [peer for peer in basedir.iterdir() if (peer.is_dir() and peer.name != "__pycache__")]
    for peerdir in peerdirs:
        process_file(peerdir / "msgs_recv.dat")
        process_file(peerdir / "msgs_sent.dat")



if __name__ == "__main__":
    main()
