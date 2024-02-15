import os
import subprocess
from typing import Literal

import defopt

from assignment_updater import cleanup_grader_notes, sum_up_grader_points


def grade_file(
    *,
    fn: str,
    test_fn: str,
    starting_points: int = 100,
    output_format: Literal["readable", "csv", "quiet"] = "readable",
        cleanup_first: bool = False,
    cleanup_only: bool = False,
    black_the_solution: bool = True,
):
    """
    Grades the specified Python file.

    Args:
        fn: str, the name of the file to be graded.
        test_fn: str, the name of the test file to be used.
        starting_points: int, the starting total of grader points.
        output_format: str, the format of the output. Either "readable" or "csv".
        cleanup_first: bool, if True, cleanup the grader notes before grading.
        cleanup_only: bool, if True, only cleanup the grader notes and return.
        black_the_solution: bool, if True, run black on the solution file before grading.
    """

    assert os.path.exists(fn), f"File not found: {fn}"
    assert os.path.exists(test_fn), f"Test file not found: {test_fn}"
    if cleanup_first:
        cleanup_grader_notes(fn)
    if black_the_solution:
        result = subprocess.run(["black", fn], capture_output=True)
        if result.returncode:
            raise ValueError(result.stderr.decode("utf-8"))
    if cleanup_only:
        return


    # use pytest to run tests, specifying the solution file and the test file
    result = subprocess.run(
        ["py.test", test_fn, "--solution", fn, "--exam", test_fn], capture_output=True
    )
    if result.returncode:
        msg = (
            "Unit tests are not supposed to raise exceptions. "
            "If your test fails, it should update the assignment, and then continue to the next test. "
            "Failing tests indicate a problem with the test itself."
        )
        msg += "\n" + result.stderr.decode("utf-8")
        raise ValueError(msg)
    #TODO: add a "interactive" mode to open the file in an editor and let the user manually adjust the points
    
    sum_up_grader_points(
        fn, starting_points=starting_points, output_format=output_format
    )


if __name__ == "__main__":
    defopt.run(
        grade_file,
        short={
            "fn": "f",
            "test-fn": "t",
            "cleanup-first": "c",
            "cleanup-only": "C",
            "starting-points": "s",
            "output-format": "o",
        },
    )
