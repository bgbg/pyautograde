import os
import subprocess
from typing import Literal

import defopt
from tqdm.auto import tqdm

from assignment_updater import cleanup_grader_notes, sum_up_grader_points


#########

import os
from contextlib import contextmanager


@contextmanager
def change_dir(destination):
    prev_dir = os.getcwd()
    os.chdir(destination)
    try:
        yield
    finally:
        os.chdir(prev_dir)


def grade_file(
    *,
    file_to_grade: str,
    file_with_tests: str,
    starting_points: int = 100,
    output_format: Literal["readable", "csv", "quiet"] = "readable",
    cleanup_first: bool = False,
    cleanup_only: bool = False,
    black_the_solution: bool = True,
):
    """
    Grades the specified Python file.

    Args:
        file_to_grade: str, the name of the file to be graded.
        file_with_tests: str, the name of the test file to be used.
        starting_points: int, the starting total of grader points.
        output_format: str, the format of the output. Either "readable" or "csv".
        cleanup_first: bool, if True, cleanup the grader notes before grading.
        cleanup_only: bool, if True, only cleanup the grader notes and return.
        black_the_solution: bool, if True, run black on the solution file before grading.
    """

    file_to_grade = os.path.abspath(file_to_grade)
    assert os.path.exists(file_to_grade), f"File not found: {file_to_grade}"
    assert os.path.exists(file_with_tests), f"Test file not found: {file_with_tests}"
    if cleanup_first:
        cleanup_grader_notes(file_to_grade)
    if black_the_solution:
        result = subprocess.run(["black", file_to_grade], capture_output=True)
        if result.returncode:
            raise ValueError(result.stderr.decode("utf-8"))
    if cleanup_only:
        return

    result = subprocess.run(
        [
            "py.test",
            file_with_tests,
            "--solution",
            file_to_grade,
        ],
        capture_output=True,
    )
    if result.returncode:
        msg = (
            (
                "Unit tests are not supposed to raise exceptions. "
                "If your test fails, it should update the assignment, and then continue to the next test. "
                "Failing tests indicate a problem with the test itself.\n"
            )
            + "Stderr:\n"
            + (result.stderr.decode("utf-8"))
            + "\nStdout:\n"
            + (result.stdout.decode("utf-8"))
        )

        raise ValueError(msg)
    # TODO: add a "interactive" mode to open the file in an editor and let the user manually adjust the points

    sum_up_grader_points(
        file_to_grade, starting_points=starting_points, output_format=output_format
    )


def grade_files_in_folder(
    *,
    folder: str,
    file_with_tests: str,
    starting_points: int = 100,
    output_format: Literal["readable", "csv", "quiet"] = "readable",
    cleanup_first: bool = True,
    cleanup_only: bool = False,
    black_the_solution: bool = True,
):
    files = [f for f in os.listdir(folder) if f.lower().endswith(".py")]
    for file in tqdm(files, desc="Grading files"):
        grade_file(
            file_to_grade=os.path.join(folder, file),
            file_with_tests=file_with_tests,
            starting_points=starting_points,
            output_format=output_format,
            cleanup_first=cleanup_first,
            cleanup_only=cleanup_only,
            black_the_solution=black_the_solution,
        )


if __name__ == "__main__":
    defopt.run(
        grade_files_in_folder,
        short={
            "folder": "f",
            "file-with-tests": "t",
            "cleanup-first": "c",
            "cleanup-only": "C",
            "starting-points": "s",
            "output-format": "o",
        },
    )
