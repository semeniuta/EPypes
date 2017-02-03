def do_nasty_stuff():
    try:
        res = open('somestuff')
    except Exception as e:
        res = e

    return res

if __name__ == '__main__':
    res = do_nasty_stuff()

