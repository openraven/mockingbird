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


class PDFDocument(__BaseDocument):
    """
    Writes PDF's containing sensitive-text to a single page. This will be expanded on in the future, as it's
    functionality is fairly limited.
    """

    @final
    def __init__(self):
        super().__init__(extension="pdf")

        # Create a list of docx formats we're going to export.
        self._docx_styles = []
        active_styles = self._configurable_dict["unstructured_data"]["pdf_document"]["active_styles"]

        if active_styles["paragraph_style"]:
            self._docx_styles.append(_PDFParagraphStyle)

        if active_styles["chat_style"]:
            self._docx_styles.append(_PDFChatStyle)

    @final
    def save(self, save_path: str) -> None:

        for style in self._docx_styles:
            instantiated_style = style()
            instantiated_style.clone_sensitive_data(other=self)
            instantiated_style.save(save_path=save_path)
            self._meta_data_object.add_other_meta_data(instantiated_style._meta_data_object)


class _PDF_Wrapper():
    """
    A really basic wrapper to write text to pdf's. Very limited functionality.
    """

    def __init__(self, pdf_path: str):
        from reportlab.pdfgen import canvas

        self._current_line = 1
        self._font_size = 12

        self.width = 750
        self.height = 1200
        pagesize = (self.width, self.height)

        self.canvas = canvas.Canvas(pdf_path, pagesize=pagesize)
        self.canvas.setLineWidth(.3)
        self.canvas.setFont('Helvetica', self._font_size)

    def __split_every_n(self, n: int, to_split: str):
        return [to_split[i:i + n] for i in range(0, len(to_split), n)]

    def save_pdf(self):
        self.canvas.save()

    def write_line(self, text: str):
        lines_to_write = self.__split_every_n(80, text)

        for line in lines_to_write:
            assert self.height - (self._font_size * self._current_line) > 0, "We broke the page."

            self._current_line += 1
            self.canvas.drawString(30, self.height - (self._font_size * self._current_line), line)


class _PDFParagraphStyle(__BaseUnstructuredDataType):
    """
    Writes a simple paragraph containing sensitive-soup.
    """

    def __init__(self):
        super().__init__(extension="pdf")

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)

        sensitive_soup = self._get_sensitive_soup()

        pdf = _PDF_Wrapper(save_file)
        pdf.write_line(sensitive_soup)

        pdf.save_pdf()
        self._log_save(save_file)


class _PDFChatStyle(__BaseUnstructuredDataType):
    """
    Writes a basic chat-log styled format.
    """

    def __init__(self):
        super().__init__(extension="pdf")

    @final
    def save(self, save_path: str) -> None:
        save_file = self.setup_save_file(save_path=save_path, extension=self.extension)
        chat_log = self._get_chat_log()
        pdf = _PDF_Wrapper(save_file)

        for line in chat_log:
            pdf.write_line(line)

        pdf.save_pdf()
        self._log_save(save_file)
