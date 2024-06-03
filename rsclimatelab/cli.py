import importlib.resources
import logging
import time
from pathlib import Path
from typing import List

import cdsapi
import click
import geopandas as gpd
import yaml
from dask.distributed import Client, LocalCluster
from distributed.utils import silence_logging_cmgr
from pydantic import BaseModel
from rich.console import Console
from rich.progress import (BarColumn, Progress, SpinnerColumn,
                           TaskProgressColumn, TextColumn, TimeElapsedColumn)

from rsclimatelab import ecmwf
from rsclimatelab.dask_util import dask_futures_stats

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


if __name__ == '__main__':
    cli()
