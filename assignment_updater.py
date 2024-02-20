import ast
import os
import re
from typing import Literal
import numpy as np

AUTHOR_ID_TOKEN = "# AUTHOR_ID:"
GRADER_TOKEN = "# GRADER:"


def update_assignment(solution, function, message, score_fixture, points):
    raise NotImplementedError(
        "need to implement logic to add grader notes to the solution file, not a function"
    )
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
            insertion_point = func_node.body[0].lineno + docstring_lines - 1
        else:
            insertion_point = func_node.lineno

        lines = content.splitlines()
        func_indent = len(re.match(r"\s*", lines[func_node.lineno - 1]).group(0))
        indent_str = " " * func_indent
        err_lines = [
            indent_str + GRADER_TOKEN + line for line in str(message).split("\n")
        ]
        points = np.round(points, 1)
        points = -points

        err_lines.append(indent_str + f"{GRADER_TOKEN} {points} points")
        score_fixture["total"] += points

        # Adjust for multi-line function definitions and decorators
        while not lines[insertion_point - 1].strip().endswith(":"):
            insertion_point += 1

        for line in reversed(err_lines):
            lines.insert(insertion_point, line)

        with open(solution_file, "w") as file:
            file.write("\n".join(lines))


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


def sum_up_grader_points(
    fn: str,
    starting_points=100,
    output_format: Literal["readable", "csv", "quiet"] = "readable",
) -> (str, float):
    """
    Sums up the grader points in the specified Python file.

    Args:
        fn: str, the name of the file to be checked.
        starting_points: int, the starting total of grader points.
        output_format: str, the format of the output. Either "readable" or "csv".

    Returns:
        int, the total number of grader points in the file.
    """
    with open(fn, "r") as file:
        lines = file.readlines()

    author_id = "UNKNOWN"
    total = starting_points
    for line in lines:
        rex = re.escape(GRADER_TOKEN) + r".*?(-?\d+(\.\d+)?)(?=\s*points)"
        match = re.search(rex, line)
        if match:
            d = float(match.group(1))
            total += d
        else:
            # find the AUTHOR_ID token
            match = re.search(re.escape(AUTHOR_ID_TOKEN) + r"(.*)", line)
            if match:
                author_id = match.group(1).strip()
    fn_str = os.path.splitext(os.path.basename(fn))[0]
    if output_format == "readable":
        print(f"{fn_str:<30s}, author_id: {author_id:<20s}, total: {total:.1f}")
    elif output_format == "csv":
        print(f"{fn_str},{author_id},{total:.1f}")
    elif output_format == "quiet":
        pass
    else:
        raise ValueError("Invalid output format")
    return (author_id, total)


if __name__ == "__main__":
    fn = "sample_solution.py"
    sum_up_grader_points(fn)
