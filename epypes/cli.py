import argparse

def parse_pubsub_args(default_pub_address, default_sub_address):

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--pub', '-p')
    arg_parser.add_argument('--sub', '-s')
    args = arg_parser.parse_args()

    if args.pub is None:
        pub_address = default_pub_address
    else:
        pub_address = args.pub

    if args.sub is None:
        sub_address = default_sub_address
    else:
        sub_address = args.sub

    return pub_address, sub_address
