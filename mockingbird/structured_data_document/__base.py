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

from abc import ABC, abstractmethod
from collections import OrderedDict
from random import randint
from typing import List

from mockingbird.__base import __BaseDocument


class __BaseStructuredDataType(__BaseDocument, ABC):
    """
    Create an array of dictionaries which can be used to organized structured-data documents. Since most structured
    data-types (csv, json, etc) are there to store key / value pairs, so this abstract-class facilitates those
    repeated functions.
    """

    @abstractmethod
    def __init__(self, extension=None):

        super().__init__(extension=extension)
        # member variables declaration
        self._dictionary_size: int
        self._entries_range: int
        self._random_position: int

        # how many entries each dictionary gets
        dictionary_range = (self._configurable_dict["base_structured_data"]["dictionary_range"])
        self._dictionary_size = randint(dictionary_range[0], dictionary_range[1])

        # how many dictionary-entries to include
        entries_range = (self._configurable_dict["base_structured_data"]["entries_range"])
        self._entries_range = randint(entries_range[0], entries_range[1])

    # Abstract Methods #

    @abstractmethod
    def save(self, save_path: str) -> None:
        pass

    # Protected Methods #

    def _get_structured_data(self) -> List[dict]:
        """
        Create a list of dictionaries containing sensitive-data in one of the locations. Each dictionary is well ordered
        in order to ensure charts / spreadsheet's rows will be consistent across.
        """

        structured_array = []
        pii_entries = self._get_embedded_positions()

        # keep each row having the same keyword entry
        header_keywords = []
        for x in range(self._entries_range):
            header_keywords.append(self._get_random_word())

        for item in range(self._entries_range):

            ordered_dict = OrderedDict()
            for x in range(self._entries_range):

                if x in pii_entries:
                    keyword = pii_entries[x]
                    ordered_dict[keyword] = self._get_sensitive_data(keyword=keyword)

                else:
                    ordered_dict[header_keywords[x]] = self._get_random_word()

            structured_array.append(ordered_dict)

        return structured_array

    def _get_structured_data_no_sensitive_info(self) -> list:
        """
        Used to create empty tables - returns a junk dictionary containing no sensitive information.
        """

        structured_array = []

        header_keywords = []
        for x in range(self._entries_range):
            header_keywords.append(self._get_random_word())

        for item in range(self._entries_range):

            ordered_dict = OrderedDict()
            for x in range(self._entries_range):
                ordered_dict[header_keywords[x]] = self._get_random_word()

            structured_array.append(ordered_dict)

        return structured_array
