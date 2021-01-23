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

def basic_example():
    from mockingbird import Mockingbird
    """
    Showcases how a Mockingbird session can be made using python code. There's two parts - first an output
    needs to be created, then sensitive-data needs to be added as a key-value pairing, matching strings to lists.
    """

    # Spawn a new Mockingbird session
    fab = Mockingbird()

    # Set which file extensions to output
    fab.set_file_extensions(["html", "docx", "yaml", "xlsx", "odt"])

    # Input the data we want to test / inject into the documents
    fab.add_sensitive_data(keyword="ssn", entries=["000-000-0000", "999-999-9999"])
    fab.add_sensitive_data(keyword="dob", entries=["01/01/1991", "02/02/1992"])

    # Generate and save the fabricated documents
    fab.save(save_path="./output_basic/")
    fab.dump_meta_data(output_file="./output_basic/meta_data.json")


def csv_example():
    from mockingbird.mb_wrappers import MockingbirdFromCSV
    """
    Showcases how CSV's can be loaded into a Mockingbird session, effectively doing what was done in
    basic_example(), plus some added functionality (see MockingbirdFromCSV for documentation).
    """

    # This effectively loads files from the csv and generates a session using each column
    fab = MockingbirdFromCSV("csv_sample.csv")
    fab.set_all_extensions()

    fab.save(save_path="./output_csv/")
    fab.dump_meta_data(output_file="./output_csv/meta_data.json")


if __name__ == "__main__":
    basic_example()
    csv_example()
