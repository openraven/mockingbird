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
import textwrap
from typing import final

from .__base import __BaseStructuredDataType


class KubernetesLogDocument(__BaseStructuredDataType):
    EXT = "log"

    @final
    def __init__(self, config_file=None):
        super().__init__(extension=KubernetesLogDocument.EXT, config_file=config_file)
        self.__line_wrap = random.randint(80, 150)

    @final
    def save(self, save_path: str) -> None:
        """
        Dumps a simulated log file in a generic java framework, with the sensitive data being leaked in a
        json-serializable payload.
        """

        log_file = self.setup_save_file(save_path=save_path, extension=self.extension, optional_decorator="1")
        structured_array = self._get_structured_data()

        with open(log_file, "w") as f:
            f.write("""
  ._.  ._.  ___________    _____    .____      .____       ._.   ._. 
  | |  | |  \_   _____/   /  _  \   |    |     |    |      | |   | | 
  |_|  |_|   |    __)    /  /_\  \  |    |     |    |      |_|   |_| 
  |-|  |-|   |     \    /    |    \ |    |___  |    |___   |-|   |-| 
  | |  | |   \___  /    \____|__  / |_______ \ |_______ \  | |   | | 
  |_|  |_|       \/             \/          \/         \/  |_|   |_| 
  
    ;; Fall is booting up... ;;                 v0.3.2 Perpetual Beta
    
     A log file for the "Fall" Application Framework, please ensure that Fall logging is not public.\n\n
                            """)

            f.write("\n")
            for line in structured_array:

                arg_dump = f"Apr 09 08:37:39.828Z | production-env-837-deer-k84 | localhost - - [WARN] Unhandled " \
                           f"exception type IOException: Dumping Object in Exception: \"" \
                           f"payload\": {json.dumps(json.dumps(line))} "

                wrapper = textwrap.TextWrapper(width=self.__line_wrap)

                wrapped_dump = wrapper.wrap(text=arg_dump)

                for wrap_line in wrapped_dump:
                    f.write(wrap_line + "\n")

                for _ in range(random.randint(2, 5)):
                    f.write("Apr 09 08:37:39.828Z | production-env-837-deer-k84 | localhost - - [INFO] All looks "
                            "normal.\n")

        self._log_save(log_file)
