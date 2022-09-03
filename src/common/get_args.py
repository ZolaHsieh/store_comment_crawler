import argparse

def get_():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', help="Please enter the mode to run", required=True)
    parser.add_argument('-dt', '--db_type', help="Please enter the db type (sqlite, mariadb)", required=True)
    parser.add_argument('-egu', '--exist_g_update', action='store_true', default=False)

    args = parser.parse_args()

    return args