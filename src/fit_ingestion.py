import argparse
import shutil
from pathlib import Path

from fitparse import FitFile

from config import GARMIN_FIT_ACTIVITIES_PATH, PARQUET_ACTIVITIES_PATH
from src.utils import fit as fit_utils

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Garmin .fit activity files into Parquet format."
    )
    parser.add_argument(
        "-s",
        "--source",
        type=Path,
        default=None,
        help="Directory containing .fit files (defaults to GARMIN_FIT_ACTIVITIES_PATH from config).",
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=Path,
        default=None,
        help="Directory to write Parquet files (defaults to PARQUET_ACTIVITIES_PATH from config).",
    )
    parser.add_argument(
        "--mode",
        choices=("replace", "incremental"),
        default="incremental",
        help=(
            "'replace' clears the destination directory before ingesting. "
            "'incremental' only ingests .fit files that are missing in the destination."
        ),
    )
    return parser.parse_args()


def ensure_directories(source_dir: Path, destination_dir: Path, mode: str) -> None:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    if mode == "replace" and destination_dir.exists():
        # Dont delete .gitkeep
        for item in destination_dir.iterdir():
            if item.name != ".gitkeep":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    destination_dir.mkdir(parents=True, exist_ok=True)


def collect_activity_files(source_dir: Path) -> list[Path]:
    activity_files = sorted(source_dir.glob("*.fit"))
    print(f"{len(activity_files)} .fit files found in {source_dir}")
    return activity_files


def existing_parquet_stems(destination_dir: Path) -> set[str]:
    return {parquet_file.stem for parquet_file in destination_dir.glob("*.parquet")}


def ingest_fit_files(
    activity_files: list[Path],
    destination_dir: Path,
    mode: str,
) -> None:
    transformed_count = 0
    skipped_count = 0
    existing_files = existing_parquet_stems(destination_dir) if mode == "incremental" else set()

    for fit_file in activity_files:
        if mode == "incremental" and fit_file.stem in existing_files:
            skipped_count += 1
            continue

        fit = FitFile(str(fit_file))

        df = fit_utils.parse_fit_file(fit)
        df.to_parquet(destination_dir / f"{fit_file.stem}.parquet", index=False)
        transformed_count += 1

    print(
        f"{transformed_count} activities converted to Parquet in {destination_dir}. "
        f"Skipped {skipped_count} files."
    )


def main() -> None:
    args = parse_args()
    source_dir = args.source or GARMIN_FIT_ACTIVITIES_PATH
    destination_dir = args.destination or PARQUET_ACTIVITIES_PATH

    ensure_directories(source_dir, destination_dir, args.mode)
    activity_files = collect_activity_files(source_dir)

    ingest_fit_files(activity_files, destination_dir, args.mode)


if __name__ == "__main__":
    main()
