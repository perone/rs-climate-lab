from pathlib import Path
from typing import Any, List

import cdsapi


def era_download_year(client: cdsapi.Client,
                      variables: List[str],
                      year: int, first_half: bool,
                      output_file: Path,
                      area_nwse: tuple) -> Any:
    """Downloads ERA5 single level dataset for half of a year.

    :param client: the CDSAPI client already configured
    :param variables: the list of ERA5 variables to download
    :param year: the year that will be downloaded
    :param first_half: True (from Jan -> Jun), False (Jul -> Dec)
    :param output_file: The output file to download
    :param area_nwse: the area to download
    """
    if first_half:
        months = [str(m) for m in range(1, 7)]
    else:
        months = [str(m) for m in range(7, 13)]

    result = client.retrieve(
        "reanalysis-era5-single-levels",
        {
            'variable': variables,
            'product_type': 'reanalysis',
            'year': str(year),
            'month': months,
            'area': area_nwse,
            'day': [str(d) for d in range(1, 32)],
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00',
            ],
            'format': 'grib',
        },
        str(output_file)
    )
    return result
