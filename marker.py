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
    return current_current, line[start + 1:current_current - 1]

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

import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    def get_validator(suffix: str):
        def validate(value: str):
            assert pathlib.Path(value).suffix == suffix
            return value
        return validate

    parser.add_argument("--marking-file", "-m", type=get_validator(".marking"), required=True)
    parser.add_argument("--comment-file", "-c", required=False)
    parser.add_argument("--data-file", "-d", type=get_validator(".json"), required=True)
    parser.add_argument("--max-score", "-s", type=int, required=True)
    parser.add_argument("--auto", "-a", action="store_true", default=False, required=False)
    arguments = parser.parse_args(sys.argv[1:])
    
    marking_file = arguments.marking_file
    comment_file = arguments.comment_file
    data_file = arguments.data_file
    max_score = arguments.max_score


    if arguments.auto:
        comment_file = str(pathlib.Path(marking_file).with_suffix(".comment"))

    with open(marking_file, "r", encoding="UTF8") as file:
        score, comments = parse_marking(file.read())
    
    with open(comment_file, "w", encoding="UTF8") as file:
        file.write("\n".join(comments))
    
    with open(data_file, "r", encoding="UTF8") as file:
        if len(s:= file.read()) == 0:
            current_data = []
        else:
            current_data = cast(list[Any], json.loads(s))
    with open(data_file, "w", encoding="UTF8") as file:
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
    

    