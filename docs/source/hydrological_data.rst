Hydrological data
-------------------------------------------------------------------------------

Ground Stations - ANA (Agência Nacional de Águas)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`ANA <https://www.gov.br/ana/pt-br>`_ (Agência Nacional de Águas) provides 
access to both real-time and historical telemetry data for the ground stations
(e.g. stream gauges) collecting hydrology data such as streamflow and
precipitation.

To download data for a single station you can just run:

.. code-block:: bash

    rscl hydro-gs download-year 86895000 \
        --start_year 2014 \
        --end_year 2018 \
        --filename dataset.parquet

And ``rscl`` will download the data from the years 2014 up to 2018 for the 
ground station code 86895000.

.. seealso:: You can find more information and station codes at the
             govt `ANA website <https://www.snirh.gov.br/hidroweb/mapa>`_.

Merging multiple datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It is very common to work with the data from multiple stream gauges at the
same time, therefore we also have a command to merge the data from multiple
downloaded datasets. To do that, use the ``rscl hydro-gs merge-datasets``
command as in the example below:

.. code-block:: bash

    rscl hydro-gs merge-datasets \
        --output merged_datasets.parquet "*.parquet"

The command above will generate the file ``merged_datasets.parquet`` with
the data from all the ``parquet`` files you specified.