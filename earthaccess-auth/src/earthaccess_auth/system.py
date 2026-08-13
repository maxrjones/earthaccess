"""Earthdata systems (production and UAT).

Moves from `earthaccess/system.py` (35 lines) with one change: main's version
does `from cmr import CMR_OPS, CMR_UAT`, which would drag python-cmr into this
otherwise requests-only package. The two CMR base URLs are inlined as literals
instead (values verified against python-cmr). The field set is kept intact —
including the CMR/status fields auth itself never touches — so earthaccess can
re-export this System unchanged and pass it everywhere it does today.

Complete as written; small enough to be real code in the sketch.
"""

from dataclasses import dataclass
from typing import NewType

CMRBaseURL = NewType("CMRBaseURL", str)
EDLHostname = NewType("EDLHostname", str)
StatusURL = NewType("StatusURL", str)
StatusApiURL = NewType("StatusApiURL", str)


@dataclass(frozen=True)
class System:
    """Host URL options, for different Earthdata domains."""

    cmr_base_url: CMRBaseURL
    status_url: StatusURL
    status_api_url: StatusApiURL
    edl_hostname: EDLHostname


PROD = System(
    CMRBaseURL("https://cmr.earthdata.nasa.gov/search/"),
    StatusURL("https://status.earthdata.nasa.gov/"),
    StatusApiURL("https://status.earthdata.nasa.gov/api/v1/statuses"),
    EDLHostname("urs.earthdata.nasa.gov"),
)
UAT = System(
    CMRBaseURL("https://cmr.uat.earthdata.nasa.gov/search/"),
    StatusURL("https://status.uat.earthdata.nasa.gov/"),
    StatusApiURL("https://status.uat.earthdata.nasa.gov/api/v1/statuses"),
    EDLHostname("uat.urs.earthdata.nasa.gov"),
)
