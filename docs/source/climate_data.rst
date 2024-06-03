Climate data
-------------------------------------------------------------------------------

ECMWF - ERA5 Reanalysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The ERA5 reanalysis dataset is a comprehensive, high-resolution global climate dataset
produced by the European Centre for Medium-Range Weather Forecasts (ECMWF).
Covering the period from January 1950 to the present, ERA5 assimilates a wide
range of observational data using advanced modeling techniques, providing hourly
estimates of atmospheric, oceanic, and land surface conditions.

This dataset is crucial for climate analysis, offering detailed insights
into weather patterns, climate variability, and long-term trends. It is widely
used for research in meteorology, hydrology, and environmental science.
In RS Climate labe you will find tools enable seamless downloading
and processing of ERA5 data.

RS Climate Lab offers tooling to submit download jobs to Climate Data Store (CDS).
Downloading data from CDS is not a trivial task, it can take hours (sometimes days)
for you to have access to the data after submitting a job, so you need to orchestrate
download jobs and keep monitoring them.

You can use the ``rscl`` CLI tool from RS Climate Lab to download data. The first step
is to define a configuration file such as the example below:

.. code-block:: yaml

    parallel_jobs: 10
    variables:
        - total_precipitation
        - 2m_temperature
        - minimum_2m_air_temperature
        - maximum_2m_air_temperature
        - potential_evaporation
        - surface_net_solar_radiation
    years:
        start: 2020
        end: 2022

.. note:: Note that RS Climate Lab (rscl) is focused in Rio Grande do Sul (RS)
          in Brazil, therefore it will automatically download only data for the 
          state. We are planning to support other areas in near future.

After that you can run the following to download the data for the specified
years:

.. code-block:: bash

    rscl era5 download --config-file config.yml output-dir

This command will start and monitor the download jobs for the specified ECMWF
ERA5 climate data from the CDS servers. It will also do that in parallel and
keep track of errors so if some file fails, you can re-run the same command and
it will download only the missing files.

.. note:: It is important to note that ``rscl`` will download the year data
          splitting the year in two parts (Jan to Jun and then Jul to Dec).

