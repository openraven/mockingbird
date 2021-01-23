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

from typing import final

from mockingbird.structured_data_document.__base import __BaseStructuredDataType


class KubernetesLogDocument(__BaseStructuredDataType):

    @final
    def __init__(self):
        super().__init__(extension="log")

    @final
    def save(self, save_path: str) -> None:
        """
        Saves the structured array into various json formats
        """

        log_file = self.setup_save_file(save_path=save_path, extension=self.extension, optional_decorator="1")
        structured_array = self._get_structured_data()

        with open(log_file, "w") as f:
            for line in structured_array:
                f.writelines("Apr 09 08:37:39.828Z | production-env-837-deer-k84 | localhost - - [WARN] Unhandled "
                             "exception type IOException: Dumping Object in Exception %s \n" % str(line))

        self._log_save(log_file)
