import os
from concurrent.futures import ThreadPoolExecutor
import subprocess
from datetime import datetime
from typing import Literal

import defopt
from tqdm.auto import tqdm

from assignment_updater import (
    cleanup_grader_notes,
    sum_up_grader_points,
    author_id_from_file,
)

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
    allow_failed_tests: bool = True,
    quiet: bool = False,
    cleanup_first: bool = False,
    cleanup_only: bool = False,
    black_the_solution: bool = True,
    output_file: str = None,
):
    """
    Grades the specified Python file.

    Args:
        file_to_grade: str, the name of the file to be graded.
        file_with_tests: str, the name of the test file to be used.
        starting_points: int, the starting total of grader points.
        quiet: bool, if True, suppress all output.
        cleanup_first: bool, if True, cleanup the grader notes before grading.
        cleanup_only: bool, if True, only cleanup the grader notes and return.
        black_the_solution: bool, if True, run black on the solution file before grading.
        output_file: str, the name of the file to write the output to. The file is jsonl format, each line is appended
        to the file.
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
        if allow_failed_tests:
            author_id = author_id_from_file(file_to_grade)
            result = (author_id, 0)
        else:
            msg = (
                (
                    "Unit tests are not supposed to raise exceptions. "
                    "If your test fails, it should update the assignment, and then continue to the next test. "
                    "Failing tests indicate a problem with the test itself.\n"
                )
                + "File: "
                + file_to_grade
                + "\n"
                + "Stderr:\n"
                + (result.stderr.decode("utf-8"))
                + "\nStdout:\n"
                + (result.stdout.decode("utf-8"))
            )
            raise ValueError(msg)
    else:
        result = sum_up_grader_points(
            file_to_grade,
            starting_points=starting_points,
            quiet=quiet,
            output_file=output_file,
        )
    return result


def _grade_folder(
    *,
    folder: str,
    summary_file_strategy: Literal["overwrite", "append", "cancel"] = "overwrite",
    example_solution_file: str = None,
    file_with_tests: str = None,
    starting_points: int = 100,
    quiet: bool = False,
    cleanup_first: bool = True,
    cleanup_only: bool = False,
    black_the_solution: bool = False,
    output_file: str = None,
):
    fn_summary = os.path.join(folder, "summary.csv")
    if os.path.exists(fn_summary):
        if summary_file_strategy == "cancel":
            raise ValueError(f"File already exists: {fn_summary}")
        if summary_file_strategy == "overwrite":
            os.remove(fn_summary)

    example_solution_file = os.path.abspath(example_solution_file)
    assert os.path.exists(
        example_solution_file
    ), f"File not found: {example_solution_file}"
    files = [f for f in os.listdir(folder) if f.lower().endswith(".py")]
    files = [example_solution_file] + [
        os.path.join(folder, f) for f in files if f != example_solution_file
    ]
    for file in tqdm(files, desc="Grading files"):
        curr = grade_file(
            file_to_grade=file,
            file_with_tests=file_with_tests,
            starting_points=starting_points,
            quiet=quiet,
            cleanup_first=cleanup_first,
            cleanup_only=cleanup_only,
            black_the_solution=black_the_solution,
            output_file=output_file,
        )
        if file == example_solution_file:
            print(f"Example solution: {curr}")
            assert (
                curr[1] >= 100
            ), f"Example solution should have 100 points, but only has {curr[1]}"
        # write to summary file, add column names if necessary
        if not os.path.exists(fn_summary):
            with open(fn_summary, "w") as f_summary:
                f_summary.write("ts,filename,submission_id,student_id,points\n")
        with open(fn_summary, "a") as f_summary:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            basename = os.path.basename(file)
            if "WorkCode" in basename:
                submission_id = (
                    os.path.splitext(basename)[0].split("WorkCode_")[1].split(".")[0]
                )
            else:
                submission_id = "UNKNOWN_SUBMISSION_ID"
            f_summary.write(f"{ts},{basename},{submission_id},{curr[0]},{curr[1]}\n")


def grade_files_in_folder(
    *,
    folder: str,
    file_with_tests: str,
    example_solution_file: str,
    summary_file_strategy: Literal["overwrite", "append", "cancel"] = "overwrite",
    starting_points: int = 100,
    quiet: bool = False,
    output_file: str = None,
    cleanup_first: bool = True,
    cleanup_only: bool = False,
    black_the_solution: bool = False,
    num_threads: int = -1,
):
    if "," in folder:
        folders = folder.split(",")
    else:
        folders = [folder]
    if num_threads < 0:
        n_cpus = os.cpu_count()
        num_threads = max(n_cpus - num_threads, 1)

    #### # override
    if True:
        file_to_grade = "data/submissions/group5/ID_212410104_WorkCode_533293.PY"
        curr = grade_file(
            file_to_grade=file_to_grade,
            file_with_tests=file_with_tests,
            starting_points=starting_points,
            quiet=quiet,
            cleanup_first=cleanup_first,
            cleanup_only=cleanup_only,
            black_the_solution=black_the_solution,
            output_file=output_file,
        )
        print("ts,filename,submission_id,student_id,points\n")

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        basename = os.path.basename(file_to_grade)
        if "WorkCode" in basename:
            submission_id = (
                os.path.splitext(basename)[0].split("WorkCode_")[1].split(".")[0]
            )
        else:
            submission_id = "UNKNOWN_SUBMISSION_ID"
        print(f"{ts},{basename},{submission_id},{curr[0]},{curr[1]}\n")
        print("DONE")
        return

    ####

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                _grade_folder,
                folder=folder,
                summary_file_strategy=summary_file_strategy,
                example_solution_file=example_solution_file,
                file_with_tests=file_with_tests,
                starting_points=starting_points,
                quiet=quiet,
                cleanup_first=cleanup_first,
                cleanup_only=cleanup_only,
                black_the_solution=black_the_solution,
                output_file=output_file,
            )
            for folder in folders
        ]
        for future in futures:
            future.result()  # Wait for each future to complete and handle exceptions if necessary


if __name__ == "__main__":
    defopt.run(
        grade_files_in_folder,
        short={
            "folder": "f",
            "file-with-tests": "t",
            "example-solution-file": "e",
            "cleanup-first": "c",
            "cleanup-only": "C",
            "starting-points": "s",
            "quiet": "q",
            "output-file": "o",
            "black-the-solution": "b",
        },
    )
