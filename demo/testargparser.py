import sys, os
sys.path.append(os.getcwd())

import argparse

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", "--pub")
    arg_parser.add_argument("-s", "--sub")

    args = arg_parser.parse_args()

    print(args)
