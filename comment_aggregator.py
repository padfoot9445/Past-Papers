import argparse
from pathlib import Path
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("--prior", action="store")
    parser.add_argument("--create", action="store_true")
    parser.add_argument("-o", "--out", action="store")
    parser.add_argument('--comment-files', nargs='+', required=False, default=None)
    args = parser.parse_args(sys.argv[1:])
    
    rootdir = Path()

    if args.create is True:
        if args.prior is None:
            args.prior = "comments.prior"
        with open(args.prior, "w", encoding="UTF8") as f:
            f.write("")

    if args.prior is None:
        
        priors: list[str] = []
        prior_files = list(rootdir.glob("*.prior"))
        assert len(prior_files) == 1
        args.prior = prior_files[0]
    
    with open(args.prior, "r", encoding="UTF8") as f:
        priors = f.readlines()

    
    if args.comment_files is None:
        files = list(rootdir.glob("**/*.comment"))
        if args.all is not True:
            s_priors = set(priors)
            files = list(filter(lambda x: x not in s_priors, files))
    else:
        files = args.comment_files
    
    out_file: str = "comments.aggregate" if args.out is None else args.out
    with open(out_file, "w", encoding="UTF8") as file: # type: ignore
        file.write("")
    with open(out_file, "a", encoding="UTF8") as file:
        for f in files:
            with open(f, "r", encoding="UTF8") as r_file:
                file.write(r_file.read())
                file.write("\n")
    if args.all is not True:
        with open(args.prior, "a", encoding="UTF8") as f:
            for file in files:
                f.write(str(file) + "\n")
