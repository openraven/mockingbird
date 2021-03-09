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
import random
from typing import final

from mockingbird.structured_data_document.__base import __BaseStructuredDataType


class JSONDocument(__BaseStructuredDataType):

    @final
    def __init__(self):
        super().__init__(extension="json")

        # todo, add to configurable
        self.indent = random.randint(0, 25)  # formatting stuff

    @final
    def save(self, save_path: str) -> None:
        """
        Saves the structured array into various json formats
        """

        json_save_file_1 = self.setup_save_file(save_path=save_path, extension=self.extension, optional_decorator="1")
        json_save_file_2 = self.setup_save_file(save_path=save_path, extension=self.extension, optional_decorator="2")

        structured_array = self._get_structured_data()
        self._save_style_1(structured_array, json_save_file_1)
        self._save_style_2(structured_array, json_save_file_2)

    def _save_style_1(self, json_object: list, save_dir: str):
        """
        Saves the json in a pretty-print way.
        """

        with open(save_dir, "w") as f:
            json.dump(json_object, f, indent=self.indent)

        self._log_save(save_dir)

    def _save_style_2(self, json_object: list, save_dir: str):
        """
        "Incorrectly" save the json, no pretty printing and incorrect escape characters. Saves the way logs sometimes
        print in kubernetes logs.
        """

        with open(save_dir, "a") as f:
            string_rep = json.dumps(json.dumps(json_object), indent=self.indent)
            f.write(string_rep)

        self._log_save(save_dir)
