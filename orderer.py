import argparse
import pathlib
from py_linq import Enumerable #pyright: ignore
import sys
import json
from contextlib import nullcontext

def get_args(argv: list[str]):
    def is_json(path):
        _path = pathlib.Path(path)
        assert _path.suffix == ".json"
        return _path
    
    parser = argparse.ArgumentParser()
    parser.add_argument("data_source", type=is_json, help="source of the data")
    parser.add_argument("--output", "-o", required=False, help="where to output the ordered data. If ommited, outputs to stdout.", default=None)
    parser.add_argument("--descending", action="store_true", default=False, help="Whether to sort in descending order")
    #TODO: parser.add_argument("--name-only", action="store_true", default=False, help="Output name only?")
    
    return parser.parse_args(argv)

def main():
    args = get_args(sys.argv[1:])
    with open(args.data_source) as file:
        with open(args.output, "w") if args.output is not None else nullcontext(sys.stdout) as out_file:
            json.dump(
                sorted(json.load(file), key=lambda x: x["raw_percentage"], reverse=args.descending),
                out_file,
                indent=4
            )

if __name__ == "__main__":
    main()

