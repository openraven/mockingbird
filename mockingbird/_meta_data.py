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

from __future__ import annotations

import io
import json
from collections import defaultdict


class _MetaData:
    """
    A class that helps facilitate the meta-data collected of __BaseDocument-types using a dictionary.

    Each key maps to a file, containing which sensitive-data was placed in each document, and how much. Anytime
    an __BaseDocument saves a file to disk, the developer must record the changes made to the file system.

    This gets more complicated when the oop-hierarchy of __BaseDocument-types are extended beyond simply
    saving a single file to disk, but saves multiple __BaseDocument's to disk, this class allows the meta-data
    to be tracked upstream, so the parent-most __BaseDocument type can record it's child-class's meta-data
    changes.
    """

    def __init__(self):
        self._meta_data_dict = dict()

    def __len__(self):
        return len(self._meta_data_dict)

    def add_data(self, file_name: str, fabricated_count: dict) -> None:
        """
        Add a file to the known-collection of meta-data.

        @param file_name: Location of the outputted file.
        @param fabricated_count: A dictionary containing how many fabricated-types were injected into the file,
                                 i.e {"ssn": 50, "itin": 30}
        """

        assert file_name not in self._meta_data_dict, "Error, filename has already been used."

        self._meta_data_dict[file_name] = fabricated_count

    def add_other_meta_data(self, other: _MetaData) -> None:
        """
        Migrates another _MetaData instance into the current one, by appending the other's dictionary.
        @return:
        """

        for key in other._meta_data_dict.keys():
            self.add_data(key, other._meta_data_dict[key])

    def dump(self, output_file: str) -> None:
        """
        Dumps the meta-data file to a file on disk.

        @param output_file: Location of output file.
        """
        with io.open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_meta_data(), f, ensure_ascii=False, indent=2)

    def consolidate_keywords(self, mappings: dict) -> None:
        """
        Sometimes multiple-keywords can be used to represent a set of sensitive-info, for example,
        "social-security-number" and "ssn" represent the same thing.

        We can consolidate all variations of a keyword into one known string to help organize the data, i.e
            mappings["ssn"] = "ssn;social-security-number"
            mappings["social-security-number"] = "ssn;social-security-number"

        Will change all references of "ssn" and "social-security-number" into the string "ssn;social-security-number".

        This is useful within the context of the MockingbirdFromCSV class, wherein a csv file contains multiple
        keys for the same set of data.

        We can consolidate all variations of a keyword into one known string to help organize the data, i.e

            mappings["ssn"] = "ssn;social-security-number"
            mappings["social-security-number"] = "ssn;social-security-number"

        Example:

            Will change all references of "ssn" and "social-security-number" into the string
            "ssn;social-security-number". In an applied example of this, suppose we have the dictionary

                _meta_data_dict["test.pdf"] = {"ssn": 50}
                _meta_data_dict["file.odt"] = {"social-security-number": 75}

            After consolidating it after using the mappings definition above, we would get

                _meta_data_dict["test.pdf"] = {"ssn;social-security-number": 50}
                _meta_data_dict["file.odt"] = {"ssn;social-security-number": 75}


        @param mappings: A with multiple many-to-one relationships between keywords.
        """

        for file_name in self._meta_data_dict.keys():
            file_mappings = self._meta_data_dict[file_name]
            new_mappings = dict()

            for key in file_mappings:
                parent_key = mappings.get(key)
                new_mappings[parent_key] = file_mappings[key]

            self._meta_data_dict[file_name] = new_mappings

    def get_meta_data(self) -> dict:
        """
        Returns a dictionary containing individual meta-data about files, as well as a meta-meta data about
        all the files.
        @return: A dictionary structured like this:

                {
                 'total_fabricated_files': 2,
                 'total_fabricated_contents': {'ssn': 87, 'itin': 64},
                 'fabricated_files': {'output.pdf': {'ssn': 10, 'itin': 5},
                                      'output.txt': {'ssn': 77, 'itin': 59}}
                 }
        """

        meta_data_dict = dict()
        meta_data_dict["total_fabricated_files"] = len(self._meta_data_dict.keys())

        collective_fabricated_data = defaultdict(lambda: 0, dict())
        for file in self._meta_data_dict.keys():

            file_meta_data = self._meta_data_dict[file]

            for data in file_meta_data:
                collective_fabricated_data[data] += file_meta_data[data]

        meta_data_dict["total_fabricated_entries"] = dict(collective_fabricated_data)
        meta_data_dict["fabricated_files"] = self._meta_data_dict

        return meta_data_dict
