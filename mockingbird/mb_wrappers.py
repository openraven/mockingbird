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
from collections import defaultdict
from itertools import product
from tempfile import NamedTemporaryFile
from typing import List

from mockingbird import Mockingbird
from mockingbird.configurable.yaml_settings_loader import load_yaml_settings
from mockingbird.mockaroo_csv_api import MockarooCsvAPI


class MockingbirdFromCSV(Mockingbird):
    """
    Loads a csv file formatted in a Mockingbird specific way. The way these csv files should be formatted
    can be found in the "sample_csv" folder found in the root directory, with each column header divided with a ;.

    This class will split each the column headers with ";" into multiple keywords, and treats each keyword as their own
    column, i.e

        ssn;social security
        355-555-555
        222-222-222

        ->

        ssn
        355-555-555
        222-222-222

        &

        social security
        355-555-555
        222-222-222

    This is used to ensure that each keyword gets tested individually, and each keyword in the column header gets
    its own set of documents. This class will take the product of all tuples of keywords, one from each original
    column. For example,

        ssn;social-security,    credit
        305-222-222,            512032138213
        305-222-222,            512032138213

        ->

        (ssn, credit) & (social-security, credit)

    These tuples will all get their own set of documents to generate, ensuring that each unique keyword combination
    gets tested against every other set of keywords. As for meta-data for all these files, once finished,
    the meta-data object will somewhat undo this process (in the meta-data), by consolidating split keywords back into
    their original ";" separated form.

    Once loaded, each column will be loaded into key-value pairs, with the key being the column header, and the values
    being sensitive-data to be injected into documents, and will generate documents for each unique permutation of
    keys.
    """

    def __init__(self, csv_file: str) -> None:
        """
        @param csv_file: String pointing to a csv file.
        """

        # Parse the csv into a dictionary, such that column headers == keys, and values == remainder of the column.
        super().__init__()
        csv_dictionary = self.__parse_csv_into_dictionary(csv_file)

        """
        Split each key up into subkeys using the ; delimiter (this is how csv's are to be inputted), then
        assign each subkey to the same value as it's parent key. (i.e "ssn;code" -> ["305-9353"] gets converted into
        "ssn" -> ["305-9353"], "code"-> ["305-9353"]) 
        """
        self.__pii_dictionary = dict()
        for key in csv_dictionary.keys():
            keywords = key.split(";")

            for subkey in keywords:
                self.__pii_dictionary[subkey] = csv_dictionary[key]

        """
        Generate a cross-product list of every keyword combination (one from each grouping). This ensures each keyword
        gets tested individually in it's own set of documents.
        """
        keywords_groupings = []
        self.__reverse_mapping = dict()  # Used for collecting meta-data
        for key in csv_dictionary.keys():
            keywords = key.split(";")
            keywords_groupings.append(keywords)

            for subkey in keywords:
                self.__reverse_mapping[subkey] = key

        self.keyword_permutations = list(product(*keywords_groupings))

    def save(self, save_path: str) -> None:

        # Run and create a Mockingbird instance for every keyword permutation produced, to test each
        # keyword against all possible keyword combinations.
        for keyword_group in self.keyword_permutations:
            session = Mockingbird()
            session.set_file_extensions(self._file_extensions)

            for keyword in keyword_group:
                session.add_sensitive_data(keyword=keyword, entries=self.__pii_dictionary[keyword])

            session.save(save_path=save_path)

            # record each sessions meta-data into a even bigger meta-data object
            self._meta_data_object.add_other_meta_data(session._meta_data_object)

        self._meta_data_object.consolidate_keywords(self.__reverse_mapping)

    @staticmethod
    def __parse_csv_into_dictionary(csv_file: str) -> dict:
        """
        Loads the csv file into a dictionary of arrays, removing empty string entries, i.e,

            1 social security
            2 355-555-555
            3 222-222-222

            ->

            {"social security": ["355-555-555", "222-222-222"], ...}
        """

        csv_dictionary = defaultdict(lambda: [], dict())
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for name in reader.fieldnames:
                    row_value = row[name]
                    if row_value != "":
                        csv_dictionary[name].append(row[name])

        return csv_dictionary


class MockingbirdFromMockaroo(MockingbirdFromCSV):
    """
    MockingbirdFromMockaroo wraps around MockingbirdFromCSV - we simply request a set of mockaroo data using mockaroo's
    api, get back a CSV file, and plug it right into MockingbirdFromCSV.
    """

    def __init__(self, api_key: str, schema_request: List[dict]):
        # Load Config
        mockaroo_config = load_yaml_settings("_default_config.yml")
        csv_endpoint = mockaroo_config["external_api"]["mockaroo_api"]["csv_endpoint"]
        row_count = mockaroo_config["external_api"]["mockaroo_api"]["row_count"]

        # CSV file to feed into MockingbirdFromCSV
        temp = NamedTemporaryFile(mode="wb")

        # Making a Mockaroo Session
        mockaroo = MockarooCsvAPI(api_key=api_key, row_count=row_count, mockaroo_api_endpoint=csv_endpoint)
        mockaroo.post_and_save_from_dict(fields=schema_request,
                                         output_path=temp.name)  # Get CSV file from mockaroo and save to temp.name

        # Call Super with the now-saved temporary CSV file
        super(MockingbirdFromMockaroo, self).__init__(csv_file=temp.name)
        temp.close()
