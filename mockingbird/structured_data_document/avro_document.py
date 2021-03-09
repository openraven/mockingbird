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

from typing import final

import pandas
import pandavro

from .__base import __BaseStructuredDataType


class AvroDocument(__BaseStructuredDataType):
    EXT = "avro"

    def __init__(self, config_file=None):
        super().__init__(extension=AvroDocument.EXT, config_file=config_file)

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension="avro")

        structured_data = self._get_structured_data()

        dataframe = pandas.DataFrame.from_dict(structured_data)
        pandavro.to_avro(save_file, dataframe)

        self._log_save(save_file)
