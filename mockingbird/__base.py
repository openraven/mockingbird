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

import os
import random
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import final, List, Dict

from random_words import RandomWords

from mockingbird._meta_data import _MetaData
from mockingbird.configurable.yaml_settings_loader import load_yaml_settings


class __BaseDocument(ABC):
    """
    The most abstract-document that Mockingbird will produce. Any sensitive-data containing documents will
    have to implement and use the functions defined in this class. Furthermore, this class helps keep track
    of how much sensitive-data is placed in each document, making benchmarking / comparisons easier to measure.
    """

    # Static variables
    rw = RandomWords()

    @abstractmethod
    def __init__(self, extension=None):

        if not extension:
            raise Exception("__BaseDocument extension not set")

        # meta-properties
        self.extension = extension  # to be defined in inherited classes
        self.document_name = str(random.getrandbits(25))

        self._sensitive_data_mappings = dict()

        # lower and upper bounds for _total_entries
        self._configurable_settings_name = "_default_config.yml"
        self._configurable_dict: Dict[str, str]
        self.__upper_bound_delta: int
        self._total_entries: int = 0

        self.__fabricated_count = defaultdict(lambda: 0, dict())  # Set zero's for every value in dict
        self.__init_bounds()

        self._meta_data_object = _MetaData()

    # Public Methods #

    @abstractmethod
    def save(self, save_path: str) -> None:
        """
        Every fabricated-document has a save feature, and this implementation varies depending on how the inherited
        class wants to save files.

        :param save_path: The root-path of where saved files will go.
        """
        raise NotImplementedError

    @final
    def add_sensitive_data(self, keyword: str, entries: List[str]) -> None:
        """
        Adds a keyword / entry-list pair to the dictionary representing a one-to-many mappings of sensitive-data.

        Updating this affects the "_total_entries" value, since the lower bound for _total_entries changes dependent
        on the amount of sensitive-data in the document.


        @param keyword: String representing the keyword to be injected
        @param entries: List containing sample sensitive-data-entries to be added.
        @raises AssertionError: if keyword is not present in the _sensitive_data_mappings
        """
        assert (keyword not in self._sensitive_data_mappings.keys())

        self._sensitive_data_mappings[keyword] = entries
        self._total_entries = self._get_random_bounded_value()

    @final
    def clone_sensitive_data(self, other: __BaseDocument) -> None:
        """
        Clones the sensitive-data from another __BaseDocument into this.
        """

        for sensitive_keyword in other._sensitive_data_mappings.keys():
            self.add_sensitive_data(keyword=sensitive_keyword,
                                    entries=other._sensitive_data_mappings[sensitive_keyword])

    @final
    def dump_meta_data(self, output_file: str) -> None:
        """
        This documents meta-data to disk.
        """
        self._meta_data_object.dump(output_file=output_file)

    @final
    def setup_save_file(self, save_path: str, extension: str, optional_decorator="") -> str:
        """
        Handles the logic required to save files. This method accepts a path and an extension, and this will
        handle the logic in making sure there's a folder for the file to go in, and returns a string that will be
        the position the subclass of this instance should save it's files.

        @param save_path: A path pointing where the files should go.
        @param extension: The extension of the file, which will be used to help name the folder it'll go in, as well
                          as generating the file name.
        @param optional_decorator: An optional flag if the inherited class saves multiple files.
        @return: A string telling the program / developer where the output file will go.
        """

        extension_folder = os.path.join(save_path, extension)
        os.makedirs(extension_folder, exist_ok=True)
        save_file_path = os.path.join(extension_folder, self.document_name + optional_decorator + "." + extension)
        return save_file_path

    # Protected Methods #

    @final
    def _log_save(self, output_file: str) -> None:
        """
        Records the saved file's meta-data into a dictionary, where keys are the file names, and the values are
        how many sensitive-data were injected into the said file. This should be called whenever this program saves
        a file to disk that contains sensitive-data.
        """

        self._meta_data_object.add_data(output_file, dict(self.__fabricated_count))

    @final
    def _set_upper_bound_delta(self, delta: int) -> None:
        """
        Update the class with the new upper-bound delta, re-assign the total number of entries to reflect the changes.
        """

        self.__upper_bound_delta = delta
        self._total_entries = self._get_random_bounded_value()

    @final
    def _get_sensitive_data(self, keyword: str) -> str:
        """
        Returns a sensitive-data value using a keyword, and logs the amount of times the mapping was accessed, in order
        to automate the tracking of meta-data files.

        @raises AssertionError: if keyword is not present in the _sensitive_data_mappings
        @param keyword: A string entry contained in _sensitive_data_mappings
        @return: A random value contained in the keyword's respective mapping file.
        """
        assert keyword in self._sensitive_data_mappings, "Keyword %s not in self._sensitive_data_mappings" % keyword

        self.__fabricated_count[keyword] += 1

        return random.choice(self._sensitive_data_mappings[keyword])

    @final
    def _get_embedded_positions(self) -> dict:
        """
        This method requires some explaining:

        Abstractly speaking, every fabricated-document will have a bunch of other random clutter, with sensitive-data
        hidden somewhere in said clutter. Let K = amount of clutter, and N = amount of sensitive-data.

        In order to both make sure every sensitive-data is put into the document, and that it's positions are randomly
        placed between clutter, this method gives mappings for the sensitive data such that all N keywords have a
        unique placement between the bounds [0, K + N].

        Inherited classes of __BaseDocument can use these placements to know where to place clutter /
        sensitive-data without having to generate the placements in their respective implementations.

        @return: A list of tuples (int, str) containing where to put PII, and which PII keyword.
                  Example: [(5, "ssn"), (7, "itin"), ... ]
        """

        pii_keywords = self._sensitive_data_mappings.keys()
        random_sampling = random.sample(range(self._total_entries), len(pii_keywords))

        return dict(zip(random_sampling, pii_keywords))

    @final
    def _get_random_bounded_value(self) -> int:
        """
        A utility function to bound the limits of randomness in the inherited classes. Currently this function is set
        to return random values between [_sensitive_data_entries + 1, _sensitive_data_entries + 1 + upper_bound]
        to ensure random-values used in the document-fabrication process gets too large.
        """

        pii_mapping_length = len(self._sensitive_data_mappings.keys())
        return random.randint(pii_mapping_length + 1, pii_mapping_length + self.__upper_bound_delta)

    @final
    def _get_random_word(self) -> str:
        """
        Returns a random word / random bounded integer containing nothing of interest. This is used to fill
        documents with clutter where necessary.

        @return: String containing random non-sensitive information.
        """
        if random.randint(0, 1) == 0:
            return self.rw.random_word()

        return str(random.getrandbits(random.randint(1, 50)))

    # Private Methods #

    @final
    def __init_bounds(self) -> None:
        """
        Initialize the bounds. This may be done multiple times / isn't only called by the constructor, since
        the bounds can be updated if more sensitive-data is added, or if a different configuration-file is loaded.
        """
        self._configurable_dict = load_yaml_settings(self._configurable_settings_name)

        self.__upper_bound_delta = self._configurable_dict["base_document"]["upper_bounds_delta"]
        self._total_entries = self._get_random_bounded_value()
