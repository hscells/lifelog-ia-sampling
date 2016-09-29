#!/usr/bin/python
import os
import sys


def main(args):
    if len(args) > 1:
        with open(args[2], 'wb') as f:
            for root, dirs, files in os.walk(args[1]):
                path = root.split('/')
                for file in files:
                    if file.split('.')[-1] == 'jpg' and ' ' not in file and '[' not in file and ']' not in file:
                        o =  root + '/' + file
                        f.write(o + '\n')
                        print(o)
    else:
        print('Please provide a directory to walk.')

if __name__ == '__main__':
    main(sys.argv)
