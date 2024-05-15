import ast
import json
import os
import re
from datetime import datetime
from typing import Literal
import numpy as np
import csv

from conftest import load_source

AUTHOR_ID_TOKEN = "# AUTHOR_ID:"
GRADER_TOKEN = "# GRADER:"


def _update_assignment_function(
    solution, function, message, score_fixture, points_to_reduce
):
    solution_file = solution.__file__

    with open(solution_file, "r") as file:
        content = file.read()

    tree = ast.parse(content)

    def find_function(node, target):
        if isinstance(node, ast.FunctionDef) and node.name == target.__name__:
            return node
        for child in ast.iter_child_nodes(node):
            result = find_function(child, target)
            if result is not None:
                return result

    func_node = find_function(tree, function)

    if func_node:
        docstring = ast.get_docstring(func_node)
        if docstring:
            docstring_lines = len(docstring.splitlines())
            insertion_point = func_node.body[0].lineno + docstring_lines + 1
        else:
            insertion_point = func_node.body[0].lineno + 1

        lines = content.splitlines()
        func_indent = len(re.match(r"\s*", lines[func_node.lineno - 1]).group(0))
        indent_str = " " * func_indent
        err_lines = [
            indent_str + GRADER_TOKEN + line for line in str(message).split("\n")
        ]
        points_to_reduce = np.round(points_to_reduce, 1)
        points = -points_to_reduce

        err_lines.append(indent_str + f"{GRADER_TOKEN} {points} points")
        score_fixture["total"] += points

        for line in reversed(err_lines):
            lines.insert(insertion_point + 1, line)

        with open(solution_file, "w") as file:
            file.write("\n".join(lines))


def _update_assignment_file(solution, message, score_fixture, points_to_reduce):
    solution_file = solution.__file__

    with open(solution_file, "r") as file:
        content = file.read()

    lines = content.splitlines()
    err_lines = [f"{GRADER_TOKEN} {line}" for line in str(message).split("\n")]
    points_to_reduce = np.round(points_to_reduce, 1)
    points = -points_to_reduce
    err_lines.append(f"{GRADER_TOKEN} {points} points")
    score_fixture["total"] += points
    lines.extend(err_lines)

    with open(solution_file, "w") as file:
        file.write("\n".join(lines))


def update_assignment(
    solution, function, message, score_fixture, points_to_reduce: float
):
    if function is not None:
        _update_assignment_function(
            solution,
            function,
            message,
            score_fixture,
            points_to_reduce=points_to_reduce,
        )
    elif hasattr(solution, "__file__"):
        # update the entire file
        _update_assignment_file(
            solution, message, score_fixture, points_to_reduce=points_to_reduce
        )


def cleanup_grader_notes(fn: str) -> str:
    """
    Removes all grader notes from the specified function in the specified Python file.

    Args:
        fn: str, the name of the function to be cleaned.

    Returns:
        str, the cleaned function code.
    """
    with open(fn, "r") as file:
        lines_in = file.readlines()
    lines_out = []
    for line in lines_in:
        if GRADER_TOKEN not in line:
            lines_out.append(line)
            continue
        if line.strip().startswith(GRADER_TOKEN):
            continue
        else:
            # remove the grader note
            lines_out.append(line.split(GRADER_TOKEN)[0])
    with open(fn, "w") as file:
        file.write("".join(lines_out))
    return "".join(lines_out)


def author_id_from_file(fn: str) -> str:
    author_id = "UNKNOWN"
    lines = open(fn, "r").readlines()
    for line in lines:
        # find the AUTHOR_ID token
        match = re.search(re.escape(AUTHOR_ID_TOKEN) + r"(.*)", line)
        if match:
            author_id = match.group(1).strip()
    if author_id == "UNKNOWN":
        # try loading the get_id_number function
        try:
            solution = load_source("solution", fn)
            author_id = str(solution.get_id_number())
        except Exception as e:
            # guess from the file name
            toks = os.path.basename(fn).split("_")
            if len(toks) > 1 and toks[0].lower() == "id":
                author_id = toks[1]
    return author_id


def sum_up_grader_points(
    fn: str,
    starting_points=100,
    quiet=False,
    output_file: str = None,
) -> (str, float):
    """
    Sums up the grader points in the specified Python file.

    Args:
        fn: str, the name of the file to be checked.
        starting_points: int, the starting total of grader points.
        quiet: bool, if True, suppress all output.
        output_file: str, the name of the file to write the output to. The file is csv format, each line is appended
        to the file.
    Returns:
        int, the total number of grader points in the file.
    """
    with open(fn, "r") as file:
        lines = file.readlines()

    author_id = author_id_from_file(fn)
    total = starting_points
    for line in lines:
        rex = re.escape(GRADER_TOKEN) + r".*?(-?\d+(\.\d+)?)(?=\s*points)"
        match = re.search(rex, line)
        if match:
            d = float(match.group(1))
            total += d
    fn_str = os.path.splitext(os.path.basename(fn))[0]
    total = int(np.round(total, 0))
    if not quiet:
        print(f"{fn_str:<30s}, author_id: {author_id:<20s}, total: {total}")
    if output_file:
        write_header = not os.path.exists(output_file)
        with open(output_file, "a") as file:
            writer = csv.DictWriter(
                file, fieldnames=["timestamp", "fn", "author_id", "total"]
            )
            if write_header:
                writer.writeheader()
            writer.writerow(
                {
                    "timestamp": datetime.now(),
                    "fn": fn_str,
                    "author_id": author_id,
                    "total": total,
                }
            )
    return author_id, total


if __name__ == "__main__":
    fn = "sample_solution.py"
    sum_up_grader_points(fn)
