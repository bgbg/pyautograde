"""
These utils are tightly coupled with my own institution, so they are not very useful for other people.
One day, I will remove them from the repository.
"""
import os
import zipfile
import defopt
from tqdm.auto import tqdm


def unzip_all_files_in_directory(
    *, directory: str, remove_zip_files: bool = False, reverse_ids: bool = True
) -> None:
    """Unzips all files in a directory and removes the zip files if remove_zip_files is True."""
    zipfiles = [f for f in os.listdir(directory) if f.lower().endswith(".zip")]
    for file in tqdm(zipfiles, desc="Unzipping files"):
        file_path = os.path.join(directory, file)
        target_directory_name = os.path.splitext(file)[0]
        # create a target directory and unzip the file into it
        target_directory = os.path.join(directory, target_directory_name)
        if reverse_ids:
            raise NotImplementedError("reverse_ids is not implemented yet")
            # toks = d.split("_WorkCode_")
            # assert len(toks) == 2
            # n = f"WorkCode_{toks[1]}_{toks[0]}"
            # print(f"{d} -> {n}")
            # shutil.move(d, n)
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(target_directory)
        if remove_zip_files:
            os.remove(file_path)
