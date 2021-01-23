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
import os
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

import requests

from mockingbird import Mockingbird
from mockingbird.mb_wrappers import MockingbirdFromCSV, MockingbirdFromMockaroo

"""
A series of scripts for mockingbird_cli to use. Essentially we get the user's command line arguments
and exhaustively determine what the user wants from them. 
"""


def parse_args():
    """
    Returns a ArgumentParser.parse_args() object parsing the CLI's inputs.
    """

    # todo, need help with CLI.
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", action="store", dest="input", type=str,
                        help="Input file depending on Mockingbird session type. See --type for more details.")

    parser.add_argument("-o", "--output", action="store", dest="output", type=str, required=True,
                        help="A directory / path where the generated files will go.")

    parser.add_argument("-t", "--type", action="store", dest="type", type=str, default='dry',
                        choices=['mockaroo', 'csv', 'csv_curl', 'dry'],
                        help="(1) mockaroo: Uses a mockaroo API to source data. Requires a json file as an input. "
                             "Requires --mockaroo_api to be set.\n"
                             "(2) csv: Uses a CSV file as a source of data. Requires a csv file as an input. \n"
                             "(3) csv_curl: Uses a CURL request to source a CSV file. Requires a URL as an input. \n"
                             "(4) dry: Dry run. Requires no input.")

    parser.add_argument("--mockaroo_api", action="store", dest="mockaroo_api", type=str,
                        help="Mockaroo API Key (if using --type mockaroo)")

    parser.add_argument("-m", "--meta", action="store", dest="meta", type=bool,
                        choices=[True, False], default=True,
                        help="Export meta-data on completion. By default is set to True.")

    mockingbird_extensions = [document().extension for document in Mockingbird.all_documents]
    parser.add_argument("--extensions", nargs="+", action="store", dest="extensions", type=list, default=[],
                        choices=mockingbird_extensions,
                        help="Set the file extension types. If none are set, all will be selected.")

    args = parser.parse_args()
    return args


def setup_mockingbird_type_from_args(args):
    """
    Accepts args and will exhaustively return a Mockingbird type based on the type requested.

    @param args: ArgumentParser().parse_args() object.
    @return: Mockingbird type
    """

    if args.type == "csv":
        assert args.input, "csv file not set, use -i [file_name].csv to specify."

        return MockingbirdFromCSV(args.input)

    if args.type == "csv_curl":
        """
        Load a CSV using a curl get request. 
        """
        assert args.input, "No input URL set"
        assert args.output, "No output file set set"

        # todo validate user input
        curl_csv = NamedTemporaryFile(mode="wb")
        response = requests.get(url=args.input)
        curl_csv.write(response.content)

        return MockingbirdFromCSV(curl_csv.name)

    if args.type == "mockaroo":
        assert args.mockaroo_api, "mockaroo api key not set. See --help for more details."
        assert args.input, "Mockaroo JSON not set, use -i [file_name].csv to specify."

        # todo validate user input
        with open(args.input) as json_file:
            schema_request = json.load(json_file)

        return MockingbirdFromMockaroo(api_key=args.mockaroo_api, schema_request=schema_request)

    if args.type == "dry":
        # Instantiate a new Mockingbird Session
        fab = Mockingbird()

        # Add "dry-run" data
        fab.add_sensitive_data("ssn", ["000-000-0000", "999-999-9999"])
        fab.add_sensitive_data("dob", ["01/01/1991", "02/02/1992"])
        return fab


def main() -> int:
    args = parse_args()

    # Create a Mockingbird session based on what the CLI arguments required.
    session = setup_mockingbird_type_from_args(args)

    if not args.extensions:
        """
        If no extensions set, enable all extensions
        """
        session.set_all_extensions()
    else:
        session.set_file_extensions(args.extensions)

    session.save(args.output)

    if args.meta:
        session.dump_meta_data(os.path.join(args.output, "meta-data.json"))

    return 0
