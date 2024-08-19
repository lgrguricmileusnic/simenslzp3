import sys
import argparse


def errx(status: int, msg: str) -> None:
    """Displays passed message on standard error output and exits with passed status.

    :param status: exit status
    :param msg: error message
    :return: None
    """
    print(msg, file=sys.stderr)
    exit(status)

def parse_argv() -> argparse.Namespace:
    """Constructs ArgumentParser and parses arguments.

    :return: argparse Namespace object with parsed arguments
    """
    parser = argparse.ArgumentParser(allow_abbrev=True)
    parser.add_argument("input_file", type=str, help="compressed firmware file name")
    parser.add_argument("output_file", type=str, help="decompressed firmware output file name")
    parser.add_argument("-k", "--keep-output", action="store_true", help="keep output in case of failure", dest="keep_output")
    return parser.parse_args()



