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
from abc import abstractmethod

import pandas

from ..__base import __BaseStructuredDataType


class __BasePandaDocument(__BaseStructuredDataType):
    """
    A wrapper for handling Panda DataFrame styled documents using Mockingbird.

    The list of structured-data dictionaries found in __BaseStructuredDataType needs done in smaller chunks, or else
    Pandas will crash converting it to a DataFrame.
    """

    @abstractmethod
    def __init__(self, extension: str, config_file=None):
        super().__init__(extension=extension, config_file=config_file)

        self.chunk_size = self._configurable_dict["base_document"]["pandas_document"]["chunk_size"]

    def _get_data_frame(self):
        structured_data = self._get_structured_data()

        # chunk the list up into chunk_size lists
        chunked_list = [structured_data[i:i + self.chunk_size] for i in range(0, len(structured_data), self.chunk_size)]
        del structured_data

        data_frame_list = []
        # pop and delete off the list (for memory management), and converting them into DataFrames
        while chunked_list:
            head = chunked_list.pop()
            new_data_frame = pandas.DataFrame.from_dict(head)
            del head
            data_frame_list.append(new_data_frame)

        concatenated_df = pandas.concat(data_frame_list)
        return concatenated_df
