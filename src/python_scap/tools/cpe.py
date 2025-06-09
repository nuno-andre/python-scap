from typing import Iterator
from functools import cached_property
import json

from python_scap._core.http import NvdClient
from python_scap.schemas.cpe import CpeItem


class NvdCpeClient(NvdClient):
    '''Client for retrieving CPE (Common Platform Enumeration) information
    from the NVD (National Vulnerability Database).
    '''

    @cached_property
    def chunks(self) -> str:
        URL = '/json/cpe/2.0/nvdcpe-2.0.zip'
        return self.get(URL)

    def get_cpe_items(self) -> Iterator[CpeItem]:

        for chunk in self.chunks:
            data = json.loads(chunk['content'])
            for item in data['products']:
                yield CpeItem.model_validate(item['cpe'])
