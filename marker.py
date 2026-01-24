import sys
from typing import Any, Callable, Literal, cast
import json
import pathlib
import datetime

COMMENT_DELIMITERS: dict[Literal["["], Literal["]"]] = {"[": "]"}

def skip_while(current_current: int, line: str, callback: Callable[[str], bool]) -> int:
    #current_current, line, callback[skips if true] -> new_current
    while len(line) > current_current and callback(line[current_current]):
        current_current += 1
    return current_current

def parse_score(line: str, current_current: int) -> tuple[int, int | Literal[0], bool]:
    #returns new_current, parsed_number | 0, candidate_number_is_score
    start = current_current
    while current_current < len(line) and line[current_current].isnumeric():
        current_current += 1
    if current_current != len(line) and not line[current_current].isspace() and line[current_current] != "+" and line[current_current] not in COMMENT_DELIMITERS.keys():
        current_current += 1
        return current_current, 0, False
    else:
        return current_current, int(line[start:current_current]), True
    

def parse_comment(line: str, current_current: int) -> tuple[int, str]:
    assert line[current_current] in COMMENT_DELIMITERS.keys()
    start = current_current
    stack = 0
    pair_open = line[current_current]
    pair_close = COMMENT_DELIMITERS[pair_open] # type: ignore
    while current_current < len(line):
        if line[current_current] == pair_open:
            stack += 1
        elif line[current_current] == pair_close:
            stack -= 1
        current_current += 1
        if stack == 0:
            break
    return current_current, line[start + 1:current_current]

def parse_marking(mark_script: str, current: int = 0) -> tuple[int, list[str]]:
    if current >= len(mark_script):
        return 0, []
    
    score: int = 0
    comment: list[str] = []

    current = skip_while(current, mark_script, lambda x: (not x.isnumeric()) and (x not in COMMENT_DELIMITERS.keys()))
    if current >= len(mark_script):
        return (0, [])
    elif mark_script[current].isnumeric():
        current, candidate_number, is_number = parse_score(mark_script, current)
        if is_number:
            score = candidate_number
    else:
        #should be a comment
        current, _comment = parse_comment(mark_script, current)
        comment = [_comment]

    rest_score, rest_comment = parse_marking(mark_script, current)
    return rest_score + score, rest_comment + comment

    
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("USAGE: [marking_file (where the scores are stored)] [comment_file (where to output comments)] [data_file (where to log the score and other data)] [max_score]")
        exit(-1)
    
    marking_file = sys.argv[1]
    comment_file = sys.argv[2]
    data_file = sys.argv[3]
    try:
        max_score = int(sys.argv[4])
    except ValueError:
        print("Max_Score must be an integer")
        exit(-1)

    if pathlib.Path(marking_file).suffix != ".marking":
        print("Marking files must have extension .marking")
        exit(-1)
    elif pathlib.Path(data_file).suffix != ".json":
        print("data_file must be a JSON file")
        exit(-1)

    if comment_file == "--auto":
        comment_file = pathlib.Path(marking_file).stem + ".comment"

    with open(marking_file, "r") as file:
        score, comments = parse_marking(file.read())
    
    with open(comment_file, "w") as file:
        file.write("\n".join(comments))
    
    with open(data_file, "r") as file:
        if len(file.read()) == 0:
            current_data = []
        else:
            current_data = cast(list[Any], json.load(file))
    with open(data_file, "w") as file:
        current_data.append(
            {
                "name": pathlib.Path(marking_file).stem,
                "time": str(datetime.datetime.now()),
                "score": score,
                "comment_file": comment_file,
                "max_score": max_score,
                "percentage": round(score/max_score * 100),
                "raw_percentage": score/max_score
            }
        )
        json.dump(current_data,file, indent=4)
    print(f"Score: {score}/{max_score}; {round(score/max_score * 100)}%")
    

    