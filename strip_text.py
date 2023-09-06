# -*- coding: utf-8 -*-
import os
import sys
import codecs
import re
import time
import shutil
from pathlib import Path

def read_pattern_string(filename):
    pattern = []
    try:
        with open(filename) as f:
            for line in f:
                # pattern = f.read().split('\n')
                if line[0] != '#' and line[0] != '\n':
                    pattern.append(line.strip())
        # print(filename, " regular pattern are: ", pattern)
        f.close()
        return pattern
    except OSError as exc:
        tb = sys.exc_info()[-1]
        lineno = tb.tb_lineno
        filename = tb.tb_frame.f_code.co_filename
        print('{} at {} line {}.'.format(exc.strerror, filename, lineno))
        time.sleep(5)
        sys.exit(exc.errno)

def read_mac_list(filename):
    pattern = []
    try:
        with open(filename) as f:
            pattern = f.read().split('\n')
        # print(filename, " MAC list are: ", pattern)
        f.close()
        return pattern
    except OSError as exc:
        tb = sys.exc_info()[-1]
        lineno = tb.tb_lineno
        filename = tb.tb_frame.f_code.co_filename
        print('{} at {} line {}.'.format(exc.strerror, filename, lineno))
        time.sleep(5)
        sys.exit(exc.errno)

def process_path(path):
    if len(os.path.dirname(path)) == 0:
        return "./"
    else:
        return os.path.dirname(path) + "/"

def match_pattern(string, ignore_pattern, pass_pattern):
    for x in ignore_pattern:
        if re.match(x, string):
            return False
    for x in pass_pattern:
        if re.match(x, string):
            return True
    return False

def file_size(file):
    try:
        file_size = os.path.getsize(file)
        # print(f"File Size in Bytes is {file_size}")
        return file_size
    except FileNotFoundError:
        print("File not found.")
    except OSError:
        print("OS error occurred.")

    return 0

def delete_file(file):
    try:
        os.remove(file)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

def delete_folder(folder):
    try:
        shutil.rmtree(folder)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

def counts_files_in_folder(folder):
    count = 0
    # Iterate directory
    for path in os.listdir(folder):
        # check if current path is a file
        if os.path.isfile(os.path.join(folder, path)):
            count += 1
    return count

def strip_log(files):
    ignore_pattren = read_pattern_string('ignore_string_pattren')
    pass_pattren   = read_pattern_string('pass_string_pattren')
    t              = time.localtime()
    t_string       = time.strftime("_strip_%Y_%m_%d-%H_%M_%S", t)
    dir_name       = "strip_log" + t_string + "/"

    for droppedFile in files:
        print("Handle the file:" + droppedFile)
        topath = process_path(droppedFile)
        
        # Create the folder if isn't exist.
        if not os.path.isdir(topath + dir_name):
            os.mkdir(topath + dir_name);
        
        writeFile = topath + dir_name + os.path.basename(droppedFile) + t_string + ".log"
        # with open(droppedFile, errors='ignore') as f_read:
        with codecs.open(droppedFile, 'r', encoding='utf-8', errors='ignore') as f_read:
            with codecs.open(writeFile, 'w', encoding='utf-8', errors='ignore') as f_write:
                for line in f_read:
                    if match_pattern(line, ignore_pattren, pass_pattren):
                        f_write.write(line)
        f_read.close()
        f_write.close()

def strip_log_by_mac(files):
    t              = time.localtime()
    t_string       = time.strftime("_strip_%Y_%m_%d-%H_%M_%S", t)
    mac_list       = read_mac_list('mac_list')

    for mac in mac_list:
        ignore_pattren = []
        pass_pattren   = []
        mac_is_in_log  = False
        dir_name       = "strip_log_by_mac" + t_string + "/"
        pass_pattren.append(".+ (WM|SM|BM).+(" + mac + ").+connected.")
        pass_pattren.append(".+ (WM|SM|BM).+(" + mac + ").+disconnected")
        pass_pattren.append(".+ (WM).+(" + mac + ").+disassoc indication")
        pass_pattren.append(".+ (BM).+(" + mac + ").+type=Disassoc, reason=")
        pass_pattren.append(".+ (WM).+topology change: channel")

        for droppedFile in files:
            print("Handle the file:" + droppedFile + ", and filter by MAC:" + mac)
            topath = process_path(droppedFile)

            # Create the folder if isn't exist.
            if not os.path.isdir(topath + dir_name):
                os.mkdir(topath + dir_name);
            if not os.path.isdir(topath + dir_name + mac.replace(":", "_") + "/"):
                os.mkdir(topath + dir_name + mac.replace(":", "_") + "/");

            writeFile = topath + dir_name + mac.replace(":", "_") + "/" + os.path.basename(droppedFile) + t_string + ".log"
            # with open(droppedFile, errors='ignore') as f_read:
            with codecs.open(droppedFile, 'r', encoding='utf-8', errors='ignore') as f_read:
                with codecs.open(writeFile, 'w', encoding='utf-8', errors='ignore') as f_write:
                    for line in f_read:
                        if match_pattern(line, ignore_pattren, pass_pattren):
                            f_write.write(line)
                        if mac_is_in_log != True and match_pattern(line, ignore_pattren, [".+ (WM|SM|BM).+(" + mac + ").+disconnected"]):
                            mac_is_in_log = True
            f_read.close()
            f_write.close()
            if file_size(writeFile) == 0 or mac_is_in_log == False:
                delete_file(writeFile)
            if counts_files_in_folder(topath + dir_name + mac.replace(":", "_")) == 0:
                delete_folder(topath + dir_name + mac.replace(":", "_"))

def main():
    if len(sys.argv) < 2:
        print('No argument')
        sys.exit()

    strip_answer = input("Strip the log by regex rule?")
    if strip_answer == "y":
        strip_log(sys.argv[1:])

    strip_answer = input("Strip the log by clients MAC?")
    if strip_answer == "y":
        print("Stripping log by clinets MAC...")
        strip_log_by_mac(sys.argv[1:])

main()