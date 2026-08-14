import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3
import shutil

"""Logging Functions"""
def warn(msg):  print(f"\033[93m⚠ {msg}\033[0m")
def error(msg): print(f"\033[91m✗ {msg}\033[0m")
def ok(msg):    print(f"\033[92m✓ {msg}\033[0m")
def info(msg):  print(f"\033[94m→ {msg}\033[0m")
def get_table(db: Path | str, table: str) -> pd.DataFrame:
    """Read a table from a MaSim SQLite database into a DataFrame.

    Parameters
    ----------∂
    db
        Path to the `.db` file.
    table
        Table name to read (e.g. ``monthlysitedata``, ``genotype``).

    Returns
    -------
    pandas.DataFrame
        Contents of the requested table.

    Raises
    ------
    FileNotFoundError
        If the database file does not exist.
    ValueError
        If the requested table is not present in the database.
    """
    # Validate input file path
    db_path = Path(db)
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db}")
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

    return df

def read_raster(file: Path | str, nodata: int = -9999) -> tuple[np.ndarray, dict]:
    """Read asc file into np array"""
    file_path = Path(file)
    if not file_path.is_file():
        raise FileNotFoundError(f"Raster file not found: {file}")

    with open(file_path, "r") as f:
        lines = f.read().splitlines()

    header = lines[:6]
    body = lines[6:]

    meta_raw = {}
    for line in header:
        k, v = line.split()
        meta_raw[k.lower()] = v

    metadata = {
        "ncols": int(float(meta_raw["ncols"])),
        "nrows": int(float(meta_raw["nrows"])),
        "xllcorner": float(meta_raw["xllcorner"]),
        "yllcorner": float(meta_raw["yllcorner"]),
        "cellsize": float(meta_raw["cellsize"]),
        "NODATA_value": int(float(meta_raw.get("nodata_value", nodata))),
    }
    nd = metadata["NODATA_value"]

    nrows, ncols = metadata["nrows"], metadata["ncols"]
    raster = np.zeros((nrows, ncols), dtype=float)

    for i, line in enumerate(body):
        vals = np.fromstring(line, sep=" ", dtype=float)
        if vals.size != ncols:
            raise ValueError(f"Row {i} has {vals.size} cols; expected {ncols}")
        raster[i, :] = vals

    # DO NOT convert nodata to NaN
    # raster[raster == nd] = np.nan

    return raster, metadata

def write_raster(
    raster: np.ndarray,
    file: Path | str,
    xllcorner: float,
    yllcorner: float,
    cellsize: int = 5000,
    mask_raster: np.ndarray | None = None,
    nodata: int = -9999,
    fmt: str = "%.5f",          # ← add this
) -> None:
    file_path = Path(file)
    if not file_path.parent.exists():
        raise FileNotFoundError(f"Directory does not exist: {file_path.parent}")

    nrows, ncols = raster.shape
    nd = float(nodata)

    raster_out = raster.astype(float, copy=True)
    raster_out[~np.isfinite(raster_out)] = nd

    if mask_raster is not None:
        if mask_raster.shape != raster_out.shape:
            raise ValueError(
                f"mask_raster shape {mask_raster.shape} does not match raster shape {raster_out.shape}"
            )
        mask = mask_raster.astype(float, copy=False)
        mask_nodata = (mask == nd) | ~np.isfinite(mask)
        raster_out[mask_nodata] = nd

    with open(file_path, "w") as f:
        f.write(f"ncols\t{ncols}\n")
        f.write(f"nrows\t{nrows}\n")
        f.write(f"xllcorner\t{xllcorner}\n")
        f.write(f"yllcorner\t{yllcorner}\n")
        f.write(f"cellsize\t{cellsize}\n")
        f.write(f"NODATA_value\t{nodata}\n")

        for row in raster_out:
            line = [str(nodata) if v == nd else fmt % v for v in row]  # ← use fmt
            f.write(" ".join(line) + "\n")

def clean_directory(cleanup_path):
    print(f"Number of items in {cleanup_path}: {len(list(Path(cleanup_path).iterdir()))}")
    removed = 0
    for item in cleanup_path.iterdir():
        if item.is_file():
            item.unlink()
            removed += 1
        elif item.is_dir():
            shutil.rmtree(item)
            removed += 1
    print(f"Removed {removed} items from {cleanup_path}")

def build_simulation_commands(input_df, replicates, calibration_run_inputs_dir, output_path, log_path, calibration_path):
    """Build MalaSim simulation commands for all input/replicate combinations."""
    cmds = []
    for idx, row in input_df.iterrows():
        for rep in range(1, replicates + 1):
            input_rel = calibration_run_inputs_dir.replace(f'{calibration_path}/', '')
            cmd = (
                f"./bin/MalaSim"
                f" -i {input_rel}/{row['input_file']}"
                f" -r SQLiteMonthlyReporter"
                f" -j {rep}"
                f" -o {output_path}/calibration_beta_{row['beta']}_access_{row['access_rate']}"
                f"_district_{row['district_id']}_pop_{row['population_bin']}_"
                f" -v 1"
                f" > {log_path}/calibration_beta_{row['beta']}_access_{row['access_rate']}"
                f"_district_{row['district_id']}_pop_{row['population_bin']}_rep_{rep}.log 2>&1"
            )
            cmds.append(cmd)
    return cmds

def write_commands_to_script_file(cmds, script_path, job_name):
    """Write simulation commands to a text file, one per line. Returns the file path."""
    script_file = Path(script_path) / f"cmds_{job_name}.txt"
    with open(script_file, "w", encoding="utf-8") as f:
        for cmd in cmds:
            f.write(cmd + "\n")
    print(f"Wrote {len(cmds)} commands to {script_file}")
    return script_file

def prepare_job_script_and_submit_jobs_script(queue_name, host_name, script_path, job_name, max_active_jobs = None, jobs_template_path = Path("_templates")):
    with open(f"{jobs_template_path}/job_template.template", "r", encoding="utf-8") as f:
        job_template_text = f.read()
        job_template_text = job_template_text.replace("#QUEUE_NAME#", queue_name).replace("#HOST_NAME#", host_name)
        job_template_text = job_template_text.replace("#JOB_NAME#", job_name)
        
    with open(script_path / f"job_template_{job_name}.pbs", "w", encoding="utf-8") as f:
        f.write(job_template_text)
        
    with open(f"{jobs_template_path}/submit_jobs.template", "r", encoding="utf-8") as f:
        submit_template_text = f.read()
        submit_template_text = submit_template_text.replace("#QUEUE_NAME#", queue_name).replace("#HOST_NAME#", host_name)
        submit_template_text = submit_template_text.replace("#JOB_NAME#", job_name)
        submit_template_text = submit_template_text.replace("cmds.txt", f"{job_name}_cmds.txt")
        submit_template_text = submit_template_text.replace("job_template.pbs", f"job_template_{job_name}.pbs")
        if max_active_jobs is not None:
            submit_template_text = submit_template_text.replace("MAX_ACTIVE_JOBS=1230", "MAX_ACTIVE_JOBS=" + str(max_active_jobs))

    with open(script_path / f"submit_jobs_{job_name}.pbs", "w", encoding="utf-8") as f:
        f.write(submit_template_text)
        
    ok(f"Prepared job script and submit jobs script for job: {job_name}")

def read_raster_to_df_like_masim(file: str | Path, *, dtype=np.float64) -> tuple[pd.DataFrame, dict]:
    """
    Read an ESRI ASCII grid (.asc) like MaSim AND generate the C++-style location list,
    returning a DataFrame with columns: index, location_id, value

    - 'index'      = flat cell index in row-major order: row * ncols + col
    - 'location_id'= sequential ID assigned only to valid (non-nodata) cells, row-major
    - 'value'      = raster value at that cell

    Returns:
      (df, metadata_dict)
    """
    file_path = Path(file)
    if not file_path.is_file():
        raise FileNotFoundError(f"Raster file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        header_lines = [next(f).strip() for _ in range(6)]
        header = {}
        for line in header_lines:
            k, v = line.split()
            header[k.lower()] = v

        ncols = int(float(header["ncols"]))
        nrows = int(float(header["nrows"]))
        nodata = float(header["nodata_value"])

        # Read grid from the remaining lines; keep nodata numeric (no NaN conversion)
        grid = np.loadtxt(f, dtype=dtype)

    if grid.ndim == 1:
        # handle nrows==1 edge case
        if nrows == 1 and grid.shape[0] == ncols:
            grid = grid.reshape(1, ncols)
        else:
            raise ValueError(f"Parsed grid is 1D {grid.shape}, expected ({nrows},{ncols})")

    if grid.shape != (nrows, ncols):
        raise ValueError(f"Grid shape {grid.shape} != header ({nrows},{ncols})")

    # MaSim/C++ logic: skip cells where value == nodata
    valid_mask = (grid != nodata)

    # Row-major order coordinates of valid cells
    rows, cols = np.nonzero(valid_mask)
    order = np.lexsort((cols, rows))
    rows, cols = rows[order], cols[order]

    # Build outputs
    flat_index = rows * ncols + cols                      # 'index' column
    location_id = np.arange(rows.size, dtype=np.int64)    # sequential IDs like C++

    values = grid[rows, cols]

    df = pd.DataFrame({
        # "raster_index": flat_index.astype(np.int64),
        "location_id": location_id,
        "value": values.astype(np.float64),
    })

    metadata = {
        "ncols": ncols,
        "nrows": nrows,
        "xllcorner": float(header["xllcorner"]),
        "yllcorner": float(header["yllcorner"]),
        "cellsize": float(header["cellsize"]),
        "NODATA_value": nodata,
    }

    max_size = nrows * ncols
    if len(df) == 0:
        raise RuntimeError("No valid locations found in raster")

    print(
        f"Generated {len(df)} locations from {max_size} total cells, "
        f"{max_size - len(df)} cells with no data"
    )
    return df, metadata

def read_raster_with_nodata(file: Path | str) -> tuple[np.ndarray, dict]:
    """
    Read in a raster file and return the raster array and metadata.

    Parameters
    ----------
    file : str
        Path to the raster file.

    Returns
    -------
    tuple
        A tuple containing the raster array (numpy.typing.NDArray) and metadata dictionary (dict).
    """
    raster, metadata = read_raster(file)

    nd = metadata["NODATA_value"]
    raster = raster.copy()  # avoid mutating any array read_raster may have cached/returned elsewhere
    raster[raster == nd] = np.nan
    return raster, metadata
