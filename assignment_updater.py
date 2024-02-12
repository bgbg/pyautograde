import ast
import re
from typing import Literal

AUTHOR_ID_TOKEN = "# AUTHOR_ID:"
GRADER_TOKEN = "# GRADER:"


def update_assignment(solution, function, err, score_fixture, points):
    """
    Inserts a formatted error message as a comment immediately after the function's header and docstring but before
    the function's code in the specified Python file. This is intended for providing automated feedback in an
    educational context.

    Args:
        solution: A module object, representing the student's solution file loaded with importlib.
        function: A function object, specifying the target function within the solution file for feedback insertion.
        err: str, the error message to be inserted as feedback.
        score_fixture: Unused in this function, included for API consistency.
        points: Unused in this function, included for API consistency.
    """
    solution_file = solution.__file__

    with open(solution_file, "r") as file:
        content = file.read()

    # Parse the file into an AST tree
    tree = ast.parse(content)

    def find_function(node, target):
        """Recursively searches for the specified function in the AST tree."""
        if isinstance(node, ast.FunctionDef) and node.name == target.__name__:
            return node
        for child in ast.iter_child_nodes(node):
            result = find_function(child, target)
            if result is not None:
                return result

    func_node = find_function(tree, function)

    if func_node:
        insertion_point = (
            func_node.body[0].lineno
            if ast.get_docstring(func_node)
            else func_node.lineno
        )
        lines = content.splitlines()

        # Find the function's indentation level
        func_indent = len(re.match(r"\s*", lines[func_node.lineno - 1]).group(0))
        indent_str = " " * func_indent

        # Prepare the error message with the correct indentation
        err_lines = [
            indent_str + f"{GRADER_TOKEN} " + line for line in str(err).split("\n")
        ]
        err_lines.append(indent_str + f"{GRADER_TOKEN} -{points} points")
        score_fixture["total"] -= points

        # Adjust for decorators and multi-line definitions
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
    if output_format == "readable":
        print(f"author_id: {author_id:<20s}, total: {total:.1f}")
    elif output_format == "csv":
        print(f"{author_id},{total:.1f}")
    elif output_format is "quiet":
        pass
    else:
        raise ValueError("Invalid output format")
    return (author_id, total)


if __name__ == "__main__":
    fn = "sample_solution.py"
    sum_up_grader_points(fn)
