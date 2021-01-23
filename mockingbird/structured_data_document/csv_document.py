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

import csv
from typing import final

from mockingbird.structured_data_document.__base import __BaseStructuredDataType


class CSVDocument(__BaseStructuredDataType):

    @final
    def __init__(self):
        super().__init__(extension="csv")

    @final
    def save(self, save_path: str) -> None:
        """
        Writes the structured data into a csv file.
        """

        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)

        output_file = open(save_file, 'w')
        csv_output = csv.writer(output_file)

        first_row = True
        structured_array = self._get_structured_data()

        for line in structured_array:
            if first_row:
                # write header first
                header = line.keys()
                csv_output.writerow(header)
                first_row = False

            # export all line's values
            csv_output.writerow(line.values())

        output_file.close()
        self._log_save(save_file)
