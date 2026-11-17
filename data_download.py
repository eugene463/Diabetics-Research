"""
Created on Sun Nov 15 20:58:24 2026

@author: eoa
"""



"""
download_data.py

Download the Diabetes 130-US hospitals for years 1999-2008 dataset and create
the project folders.

Dataset
    Clore, J., Cios, K., DeShazo, J. and Strack, B. (2014) Diabetes 130-US
    hospitals for years 1999-2008 [Dataset]. UCI Machine Learning Repository.
    https://doi.org/10.24432/C5230J
    The dataset is released under the CC BY 4.0 licence. It accompanies Strack
    et al. (2014), BioMed Research International, 2014, 781670,
    https://doi.org/10.1155/2014/781670

What the script does
    1 Creates the data, results and figures folders next to this file.
    2 Downloads the dataset zip into memory and extracts it into the data folder.
      No zip file is saved so there is nothing to clean up.
    3 Skips the download if data/diabetic_data.csv already exists.

Folders produced
    data/diabetic_data.csv    the file the analysis reads
    data/IDS_mapping.csv      lookup table for the ID columns
    results/                  tables written by the analysis
    figures/                  plots written by the analysis

How to run
    Spyder     open the file and press F5. Running a selection with F9 also
               works and uses the current working directory.
    Terminal   python download_data.py

How to test
    The doctests need no internet connection because they use a small fake zip.
    Spyder     set the working directory to this folder then run in the console
                   import doctest, download_data
                   doctest.testmod(download_data, verbose=True)
               or add --test under Run, Configuration per file, Command line options.
    Terminal   python -m doctest -v download_data.py
"""
import doctest
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://archive.ics.uci.edu/static/public/296/"
       "diabetes+130-us+hospitals+for+years+1999-2008.zip")
DATA_FILE = "diabetic_data.csv"
FOLDERS = ("data", "results", "figures")


def get_base_dir():
    """Return the project folder: the folder holding this script.

    Falls back to the current working directory when __file__ does not
    exist, which happens when a selection is run with F9 in Spyder or code is
    pasted into a console.

    >>> get_base_dir().is_dir()
    True
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


def create_folders(base):
    """Create the project folders under base and return them by name.

    Existing folders are left untouched, so this is safe to run repeatedly.

    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     made = create_folders(Path(tmp))
    ...     sorted(made), all(p.is_dir() for p in made.values())
    (['data', 'figures', 'results'], True)

    Running it twice does not raise an error:

    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     _ = create_folders(Path(tmp))
    ...     len(create_folders(Path(tmp)))
    3
    """
    made = {}
    for name in FOLDERS:
        folder = Path(base) / name
        folder.mkdir(parents=True, exist_ok=True)
        made[name] = folder
    return made


def extract_zip_bytes(content, dest):
    r"""Extract a zip archive held in memory into dest.

    Parameters
    ----------
    content : bytes
        The raw bytes of a zip file.
    dest : pathlib.Path
        Folder to extract into (must already exist).

    Returns
    -------
    list of str
        Names of the extracted files.

    Raises
    ------
    ValueError
        If any archive member would be written outside dest
        as in a zip slip attack.

    >>> import tempfile
    >>> buf = io.BytesIO()
    >>> with zipfile.ZipFile(buf, "w") as zf:
    ...     zf.writestr("diabetic_data.csv", "a,b\n1,2\n")
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     names = extract_zip_bytes(buf.getvalue(), Path(tmp))
    ...     (names, (Path(tmp) / "diabetic_data.csv").read_text())
    (['diabetic_data.csv'], 'a,b\n1,2\n')

    Members that try to escape the destination folder are rejected:

    >>> bad = io.BytesIO()
    >>> with zipfile.ZipFile(bad, "w") as zf:
    ...     zf.writestr("../evil.txt", "x")
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     extract_zip_bytes(bad.getvalue(), Path(tmp))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: unsafe path in zip: ../evil.txt
    """
    dest = Path(dest).resolve()
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for member in zf.namelist():
            try:
                (dest / member).resolve().relative_to(dest)
            except ValueError:
                raise ValueError(f"unsafe path in zip: {member}") from None
        zf.extractall(dest)
        return [n for n in zf.namelist() if not n.endswith("/")]


def download_dataset(base=None, url=URL, force=False):
    """Create the folders, download the dataset and return the CSV path.

    Parameters
    ----------
    base : pathlib.Path, optional
        Project folder. Defaults to the folder containing this script.
    url : str, optional
        Location of the dataset zip.
    force : bool, optional
        Download again even if data/diabetic_data.csv already exists.

    Returns
    -------
    pathlib.Path
        Path to data/diabetic_data.csv.

    Raises
    ------
    RuntimeError
        If the download or extraction fails, or the expected CSV is missing
        from the archive. The message says how to download it manually.

    If the file is already present, nothing is downloaded:

    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     _ = create_folders(Path(tmp))
    ...     _ = (Path(tmp) / "data" / DATA_FILE).write_text("x")
    ...     download_dataset(Path(tmp)).name
    'diabetic_data.csv'

    A failed download gives a clear error (an unreachable file:// URL is
    used so the test never touches the network):

    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     download_dataset(Path(tmp), url="file:///no/such/file.zip")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    RuntimeError: Automatic download failed
    """
    base = get_base_dir() if base is None else Path(base)
    folders = create_folders(base)
    target = folders["data"] / DATA_FILE
    if target.exists() and not force:
        return target

    manual = ("Download it manually from https://archive.ics.uci.edu/dataset/296 "
              f"and put {DATA_FILE} in {folders['data']}")
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            extract_zip_bytes(response.read(), folders["data"])
    except Exception as exc:
        raise RuntimeError(f"Automatic download failed ({exc}). {manual}") from exc
    if not target.exists():
        raise RuntimeError(f"{DATA_FILE} was not found in the downloaded archive. {manual}")
    return target


def run_tests(verbose=False):
    """Run this module's doctests and return the number of failures."""
    result = doctest.testmod(sys.modules[__name__], verbose=verbose)
    print(f"Doctests: {result.attempted} run, {result.failed} failed")
    return result.failed


def main(argv=None):
    """Command-line entry point. Use --test to run the doctests instead."""
    argv = sys.argv[1:] if argv is None else argv
    if "--test" in argv:
        return run_tests(verbose="-v" in argv)
    try:
        path = download_dataset()
    except RuntimeError as exc:
        print(exc)
        return 1
    print(f"Dataset ready: {path}")
    return 0


if __name__ == "__main__":
    main()