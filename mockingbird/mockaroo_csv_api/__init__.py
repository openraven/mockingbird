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

import requests


class MockarooCsvAPI:
    """
    A wrapper to help make getting CSV files from mockaroo easier.
    """

    def __init__(self,
                 api_key: str,
                 row_count=10,
                 mockaroo_api_endpoint='https://api.mockaroo.com/api/generate.csv') -> None:
        """

        @param api_key: Mockaroo Access Key
        @param row_count: How many rows to request from Mockaroo
        @param mockaroo_api_endpoint: Mockaroo's API-Endpoint (this shouldn't change, but it might in the future).
        """
        self.api_key = api_key
        self.row_count = row_count
        self.mockaroo_api_endpoint = mockaroo_api_endpoint

    def post_and_save_from_dict(self, fields: list, output_path: str) -> None:
        """

        @param fields: A list of dictionaries for mockaroo's schema. See https://www.mockaroo.com/api/docs for more
        information.

        Example:
        schema_request = [
            {
                "name": "ssn;social security;number",
                "type": "SSN"
            },
            {
                "name": "cc;credit card",
                "type": "Credit Card #"
            }
            ]

        @param output_path: Where to put the csv file.
        """

        post_url = self.mockaroo_api_endpoint + "?key=" + self.api_key + '&count=' + str(self.row_count)
        post_request = requests.post(url=post_url, json=fields)

        # todo, some error checking here. Perhaps some engineers know how to check for error codes better.
        if post_request.status_code != 200:
            print("Warning mockaroo http code error'd: %s" % str(post_request.status_code), file=sys.stderr)

        # Write CSV to disk.
        with open(output_path, 'wb') as f:
            f.write(post_request.content)
