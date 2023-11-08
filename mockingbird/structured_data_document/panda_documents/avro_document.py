#
# Copyright 2021 Open Raven Inc. and the Mockingbird project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import numpy as np
import avro.schema
from avro.io import DatumWriter
from avro.datafile import DataFileWriter

from typing import final

from .__base import __BasePandaDocument


AVRO_TYPES = {
    np.dtype('?'): 'boolean',
    np.int8: 'int',
    np.int16: 'int',
    np.int32: 'int',
    np.uint8: {'type': 'int', 'unsigned': True},
    np.uint16: {'type': 'int', 'unsigned': True},
    np.uint32: {'type': 'int', 'unsigned': True},
    np.int64: 'long',
    np.uint64: {'type': 'long', 'unsigned': True},
    np.dtype('O'): 'string',
    np.unicode_: 'string',
    np.float32: 'float',
    np.float64: 'double',
}


class AvroDocument(__BasePandaDocument):
    EXT = "avro"

    def __init__(self, config_file=None):
        super().__init__(extension=AvroDocument.EXT, config_file=config_file)

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension="avro")

        df = self._get_data_frame()

        schema = {
            "type": "record",
            "name": "TestData",
            "fields": [
                {'name': key, 'type': AVRO_TYPES[np_type]}
                for key, np_type in df.dtypes.items()
            ]
        }

        with open(save_file, 'wb') as f:
            writer = DataFileWriter(f, DatumWriter(), avro.schema.parse(json.dumps(schema)))
            for i, row in df.iterrows():
                writer.append(row.to_dict())
            writer.close()

        self._log_save(save_file)
