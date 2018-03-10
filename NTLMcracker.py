#!/usr/bin/env python3

import itertools
import string
import os
import hashlib
import time
import multiprocessing


class Cracker(object):
    ALPHA_LOWER = (string.ascii_lowercase,)
    ALPHA_UPPER = (string.ascii_uppercase,)
    ALPHA_MIXED = (string.ascii_lowercase, string.ascii_uppercase)
    PUNCTUATION = (string.punctuation,)
    NUMERIC = (''.join(map(str, range(0, 10))),)
    ALPHA_LOWER_NUMERIC = (string.ascii_lowercase, ''.join(map(str, range(0, 10))))
    ALPHA_UPPER_NUMERIC = (string.ascii_uppercase, ''.join(map(str, range(0, 10))))
    ALPHA_MIXED_NUMERIC = (string.ascii_lowercase, string.ascii_uppercase, ''.join(map(str, range(0, 10))))
    ALPHA_LOWER_PUNCTUATION = (string.ascii_lowercase, string.punctuation)
    ALPHA_UPPER_PUNCTUATION = (string.ascii_uppercase, string.punctuation)
    ALPHA_MIXED_PUNCTUATION = (string.ascii_lowercase, string.ascii_uppercase, string.punctuation)
    NUMERIC_PUNCTUATION = (''.join(map(str, range(0, 10))), string.punctuation)
    ALPHA_LOWER_NUMERIC_PUNCTUATION = (string.ascii_lowercase, ''.join(map(str, range(0, 10))), string.punctuation)
    ALPHA_UPPER_NUMERIC_PUNCTUATION = (string.ascii_uppercase, ''.join(map(str, range(0, 10))), string.punctuation)
    ALPHA_MIXED_NUMERIC_PUNCTUATION = (
        string.ascii_lowercase, string.ascii_uppercase, ''.join(map(str, range(0, 10))), string.punctuation
    )

    def __init__(self, hash_type, hash):
      
        self.__hash_type = hash_type
        self.__hash = hash

    def generate_hash(self, data):
     
        if self.__hash_type == "ntlm":
            return hashlib.new("md4", data.encode("utf-16le")).hexdigest()

        return hashlib.new(self.__hash_type, data.encode("utf-8")).hexdigest()

    @staticmethod
    def __search_space(charset, maxlength):
       
        return (
            ''.join(candidate) for candidate in
            itertools.chain.from_iterable(
                itertools.product(charset, repeat=i) for i in
                range(1, maxlength + 1)
            )
        )

    def attack(self, q, charset, maxlength):
     
        for attempt in self.__search_space(charset, maxlength):
            if not q.empty():
                return

            if self.__hash == self.generate_hash(attempt):
                q.put("FOUND")
                q.put("{}Match found! Password is {}{}".format(os.linesep, attempt, os.linesep))
                return
        q.put("NOT FOUND")

    @staticmethod
    def work(work_queue, done_queue, charset, maxlength):
      
        obj = work_queue.get()
        obj.attack(done_queue, charset, maxlength)


if __name__ == "__main__":
    character_sets = {
        "01": Cracker.ALPHA_LOWER,
        "02": Cracker.ALPHA_UPPER,
        "03": Cracker.ALPHA_MIXED,
        "04": Cracker.NUMERIC,
        "05": Cracker.ALPHA_LOWER_NUMERIC,
        "06": Cracker.ALPHA_UPPER_NUMERIC,
        "07": Cracker.ALPHA_MIXED_NUMERIC,
        "08": Cracker.PUNCTUATION,
        "09": Cracker.ALPHA_LOWER_PUNCTUATION,
        "10": Cracker.ALPHA_UPPER_PUNCTUATION,
        "11": Cracker.ALPHA_MIXED_PUNCTUATION,
        "12": Cracker.NUMERIC_PUNCTUATION,
        "13": Cracker.ALPHA_MIXED_NUMERIC_PUNCTUATION
    }

    hashes = {
        "01": "MD5",
        "02": "MD4",
        "03": "LM",
        "04": "NTLM",
        "05": "SHA1"
            }

    prompt = "Specify the character set to use:{}{}".format(os.linesep, os.linesep)
    for key, value in sorted(character_sets.items()):
        prompt += "{}. {}{}".format(key, ''.join(value), os.linesep)

    while True:
        try:
            charset = input(prompt).zfill(2)
            selected_charset = character_sets[charset]
        except KeyError:
            print("{}Please select a valid character set{}".format(os.linesep, os.linesep))
            continue
        else:
            break

    prompt = "{}Specify the maximum possible length of the password: ".format(os.linesep)

    while True:
        try:
            password_length = int(input(prompt))
        except ValueError:
            print("{}Password length must be an integer".format(os.linesep))
            continue
        else:
            break

    prompt = "{}Specify the hash's type:{}".format(os.linesep, os.linesep)
    for key, value in sorted(hashes.items()):
        prompt += "{}. {}{}".format(key, value, os.linesep)

    while True:
        try:
            hash_type = hashes[input(prompt).zfill(2)]
        except KeyError:
            print("{}Please select a supported hash type".format(os.linesep))
            continue
        else:
            break

    prompt = "{}Specify the hash to be attacked: ".format(os.linesep)

    while True:
        try:
            user_hash = input(prompt)
        except ValueError:
            print("{}Something is wrong with the format of the hash. Please enter a valid hash".format(os.linesep))
            continue
        else:
            break

    print("{}Cracking...{}".format(os.linesep, os.linesep), flush=True)

    processes = []
    work_queue = multiprocessing.Queue()
    done_queue = multiprocessing.Queue()
    cracker = Cracker(hash_type.lower(), user_hash.lower())

    start_time = time.time()

    p = multiprocessing.Process(target=Cracker.work,
                                args=(work_queue, done_queue, ''.join(selected_charset), password_length))
    processes.append(p)
    work_queue.put(cracker)
    p.start()

    if len(selected_charset) > 1:
        for i in range(len(selected_charset)):
            p = multiprocessing.Process(target=Cracker.work,
                                        args=(work_queue, done_queue, selected_charset[i], password_length))
            processes.append(p)
            work_queue.put(cracker)
            p.start()

    failures = 0
    while True:
        data = done_queue.get()
        if data == "NOT FOUND":
            failures += 1
        elif data == "FOUND":
            print(done_queue.get())
            done_queue.put("DONE")
            break

        if failures == len(processes):
            print("{}No matches found{}".format(os.linesep, os.linesep))
            break

    print("Took {} seconds".format(time.time() - start_time))
    print("Thanks To D@nt3")
