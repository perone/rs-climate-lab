from typing import Dict, List

from dask.distributed import Future


def dask_futures_stats(future_list: List[Future]) -> Dict[str, int]:
    """Grabs the status of each Dask future and return a dictionary
    with aggregated results.

    :param future_list: list of Dask Futures
    """
    count_stats = {
        "error": 0,
        "finished": 0,
        "pending": 0,
    }
    for future in future_list:
        count_stats[future.status] += 1
    return count_stats
