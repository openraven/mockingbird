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

from mockingbird.__base import __BaseDocument
from .__base import __BaseUnstructuredDataType


class TXTDocument(__BaseDocument):
    def __init__(self):
        super().__init__(extension="txt")

        # Create a list of docx formats we're going to export.
        self._styles = []
        active_styles = self._configurable_dict["unstructured_data"]["txt_document"]["active_styles"]

        if active_styles["paragraph_style"]:
            self._styles.append(_TxtParagraphStyle)

        if active_styles["bullet_point_style"]:
            self._styles.append(_TxtBulletPointStyle)

        if active_styles["chat_style"]:
            self._styles.append(_TxtChatStyle)

    @final
    def save(self, save_path: str) -> None:

        for style in self._styles:
            instantiated_style = style()
            instantiated_style.clone_sensitive_data(other=self)
            instantiated_style.save(save_path=save_path)
            self._meta_data_object.add_other_meta_data(instantiated_style._meta_data_object)


class _TxtParagraphStyle(__BaseUnstructuredDataType):

    def __init__(self):
        super().__init__(extension="txt")

    @final
    def save(self, save_path: str) -> None:
        """

        """
        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)

        sensitive_soup = self._get_sensitive_soup()

        with open(save_file, "w") as f:
            f.write(sensitive_soup)

        self._log_save(save_file)


class _TxtBulletPointStyle(__BaseUnstructuredDataType):
    def __init__(self):
        super().__init__(extension="txt")

    @final
    def save(self, save_path: str) -> None:

        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)
        enumerated_groups = self._get_enumerated_style()

        with open(save_file, "w") as f:
            for group in enumerated_groups:
                key, enumerated_items = group

                f.write(key + "\n")

                for item in enumerated_items:
                    f.write("- %s \n" % item)

        self._log_save(save_file)


class _TxtChatStyle(__BaseUnstructuredDataType):

    def __init__(self):
        super().__init__(extension="txt")

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)
        chat_log = self._get_chat_log()

        with open(save_file, "w") as f:
            for line in chat_log:
                f.write("%s \n" % line)

        self._log_save(save_file)
