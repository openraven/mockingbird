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

from ..panda_documents.__base import __BasePandaDocument


class ParquetDocument(__BasePandaDocument):
    EXT = "parquet"

    def __init__(self, config_file=None):
        super().__init__(extension=ParquetDocument.EXT, config_file=config_file)

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)

        dataframe = self._get_data_frame()
        dataframe.to_parquet(save_file)

        self._log_save(save_file)
