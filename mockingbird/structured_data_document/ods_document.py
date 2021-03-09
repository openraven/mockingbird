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

from pyexcel_ods import save_data

from mockingbird.structured_data_document.__base import __BaseStructuredDataType


class ODSDocument(__BaseStructuredDataType):

    @final
    def __init__(self):
        super().__init__(extension="ods")

    @final
    def save(self, save_path: str) -> None:

        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)
        structured_array = self._get_structured_data()

        formatted_array = []
        first_row = True

        for line in structured_array:
            if first_row:
                # write header first
                header = list(line.keys())
                formatted_array.append(header)
                first_row = False

            formatted_array.append(list(line.values()))

        save_data(save_file, formatted_array)
        self._log_save(save_file)
