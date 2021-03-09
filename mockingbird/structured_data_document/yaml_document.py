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

import random
from typing import final

import yaml

from mockingbird.structured_data_document.__base import __BaseStructuredDataType


class YAMLDocument(__BaseStructuredDataType):

    @final
    def __init__(self):
        super().__init__(extension="yaml")
        self.indent = random.randint(0, 25)  # formatting stuff

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)

        structured_array = self._get_structured_data()

        with open(save_file, 'w') as file:
            documents = yaml.dump(structured_array, file)

        self._log_save(save_file)
