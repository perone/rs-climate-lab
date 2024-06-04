import importlib.resources
import logging
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List

import cdsapi
import click
import geopandas as gpd
import pandas as pd
import yaml
from dask.distributed import Client, LocalCluster
from distributed.utils import silence_logging_cmgr
from pydantic import BaseModel
from rich.console import Console
from rich.progress import (BarColumn, Progress, SpinnerColumn,
                           TaskProgressColumn, TextColumn, TimeElapsedColumn)

from rsclimatelab import ecmwf
from rsclimatelab.dask_util import dask_futures_stats
from rsclimatelab.hydrogs import get_hidrometeorological_data

console = Console()
ASSETS_PATH = importlib.resources.files(__package__) / "assets"


class DownloadRange(BaseModel):
    start: int
    end: int


class ERA5DownloadConfig(BaseModel):
    parallel_jobs: int
    variables: List[str]
    years: DownloadRange

    @staticmethod
    def load_config(file_path: Path) -> 'ERA5DownloadConfig':
        with file_path.open("r") as fhandle:
            config_dict = yaml.safe_load(fhandle)
        return ERA5DownloadConfig(**config_dict)


@click.group()
def cli() -> None:
    pass


@cli.group()
def era5() -> None:
    pass


@cli.group()
def hydro_gs() -> None:
    """Hydrological Ground Stations (hydro-gs)"""
    pass


@era5.command()
@click.option("--config-file",
              required=True,
              help="ERA5 download config.",
              type=click.Path(file_okay=True, exists=True,
                              resolve_path=True, readable=True,
                              path_type=Path))
@click.argument(
    'output-dir',
    type=click.Path(exists=False, file_okay=False,
                    dir_okay=True, writable=True,
                    readable=True, resolve_path=True,
                    path_type=Path),
    required=True)
def download(config_file: Path, output_dir: Path) -> None:
    """Download ERA5 data."""
    console.log('Downloading ERA5 data...')
    output_dir.mkdir(parents=True, exist_ok=True)

    config = ERA5DownloadConfig.load_config(config_file)
    console.log("Loaded configuration: ")
    console.log(config)

    console.log("Loading RS state shape...")
    rs_state_shapefile = ASSETS_PATH / "rs_state.shp"
    gdf = gpd.read_file(rs_state_shapefile, engine="pyogrio")
    state_bounds = gdf.geometry.bounds.values.ravel().tolist()
    state_bounds_nwse = (
        state_bounds[3], state_bounds[0],
        state_bounds[1], state_bounds[2]
    )

    with console.status("Starting Dask scheduler and workers..."):
        cluster = LocalCluster(n_workers=config.parallel_jobs, threads_per_worker=1,
                               processes=True, dashboard_address="0.0.0.0:8786")
        client = Client(cluster, name="RSClimateLab")
        console.log('Dask scheduler and workers started.')

    console.log(f"Dask dashboard at: {client.dashboard_link}.")
    console.log("Follow your jobs at: https://cds.climate.copernicus.eu/")

    cds_client = cdsapi.Client(progress=False)

    futures = []
    for year in range(config.years.start, config.years.end + 1):
        file_path = output_dir / f"era5-{year}-jan-jun.grib"
        if not file_path.exists():
            future = client.submit(ecmwf.era_download_year, cds_client,
                                   config.variables, year, True,
                                   file_path, state_bounds_nwse, key=f"rscl-job-{year}-jan-jun")
            futures.append(future)
        else:
            console.log(f"File {file_path} exists, skipping.")

        file_path = output_dir / f"era5-{year}-jul-dec.grib"
        if not file_path.exists():
            future = client.submit(ecmwf.era_download_year, cds_client,
                                   config.variables, config.years.start, False,
                                   file_path, state_bounds_nwse, key=f"rscl-job-{year}-jul-dec")
            futures.append(future)
        else:
            console.log(f"File {file_path} exists, skipping.")

    console.log(f"Waiting for {len(futures)} jobs. ERA5 jobs can take many hours to complete.")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(show_speed=True),
        TimeElapsedColumn()
    ) as progress:
        overall_task = progress.add_task("[green]All Jobs []", total=len(futures))
        while not progress.finished:
            job_stats = dask_futures_stats(futures)
            count_pending = job_stats["pending"]
            count_finished = job_stats["finished"]
            count_error = job_stats["error"]
            prog_count = count_error + count_finished
            progress.update(overall_task, completed=prog_count,
                            description=f"All jobs: [yellow]Pending [{count_pending}], "
                                        f"[green]Finished [{count_finished}], "
                                        f"[red]Error [{count_error}]")
            time.sleep(1.0)

    with console.status("Shutting down Dask..."):
        time.sleep(2)
        with silence_logging_cmgr(logging.CRITICAL):
            client.close()
        console.log("Dask shut down.")


@hydro_gs.command()
@click.argument('code')
@click.option('--start_date', required=True, help='Start date in format dd/mm/yyyy')
@click.option('--end_date', required=True, help='End date in format dd/mm/yyyy')
@click.option('--filename', required=True, help='Output filename for the downloaded data')
def download_range(code: str, start_date: str,
                   end_date: str, filename: str) -> None:
    """Downloads hydrological data from ground stations from ANA (https://www.gov.br/ana)."""
    console.log(f"Downloading telemetry data for {code} from {start_date} to {end_date}...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(show_speed=True),
        TimeElapsedColumn()
    ) as progress:
        _ = progress.add_task("[green]Downloading", total=None)
        df = get_hidrometeorological_data(code, start_date, end_date)

    console.log(f"Downloaded {len(df)} rows, saving to {filename}.")
    df.to_parquet(filename)
    console.log(f"File {filename} saved.")
    console.log(f"Sample data:\n{df.tail(4)}")


@hydro_gs.command()
@click.argument('code')
@click.option('--start_year', required=True, help='Start date in format yyyy')
@click.option('--end_year', required=True, help='End date in format yyyy')
@click.option('--filename', required=True, help='Output filename for the downloaded data')
def download_year(code: str, start_year: str,
                  end_year: str, filename: str) -> None:
    """Downloads hydrological data from ground stations from ANA (https://www.gov.br/ana)."""
    start_year_range = int(start_year)
    end_year_range = int(end_year)

    dfs = []
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(get_hidrometeorological_data, code,
                            f"01/01/{year}", f"31/12/{year}"): year
            for year in range(start_year_range, end_year_range + 1)
        }
        console.log(f"Submitted {len(futures)} download jobs, downloading...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(show_speed=True),
            TimeElapsedColumn(), console=console
        ) as progress:
            overall_task = progress.add_task("[green]All Jobs []", total=len(futures))

            finished = []
            while not progress.finished:
                for future in as_completed(futures):
                    finished.append(future)
                    progress.update(overall_task, completed=len(finished))

                    year = futures[future]
                    try:
                        df = future.result()
                        console.log(f"Downloaded {len(df)} rows for year {year}.")
                        dfs.append(df)
                    except Exception as exc:
                        console.log(f"Failed to download data for year "
                                    f"{year} with exception: {exc}")

    concat_df = pd.concat(dfs)
    concat_df = concat_df.sort_values(by=["data_hora"])
    concat_df.to_parquet(filename)

    console.log(f"File {filename} saved.")
    console.log(f"Sample data:\n{concat_df.tail(4)}")


if __name__ == '__main__':
    cli()
