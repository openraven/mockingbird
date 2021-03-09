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
from mockingbird.structured_data_document import __all_classes__ as _structured_data_all
from mockingbird.unstructured_data_document import __all_classes__ as _unstructured_data_all


class Mockingbird(__BaseDocument):
    """
    Mockingbird aims to be a tool to help test data-discovery tools, by largely automating the process of
    generating sensitive-documents. Mockingbird makes it possible to convert structured data in the form of
    lists, then inject it into a series of structured and unstructured filetypes and extensions.
    """

    # A list of all possible classes Mockingbird can generate
    all_documents = []
    all_documents.extend(_structured_data_all)
    all_documents.extend(_unstructured_data_all)

    def __init__(self, file_minimum=100):
        super().__init__(extension="mockingbird")

        # Create a list of key to classes mappings
        self.__extension_to_classes = {}
        for document_type in Mockingbird.all_documents:
            # Need to instantiate the class to get the extension string.
            instantiated_document = document_type()
            assert instantiated_document.extension not in self.__extension_to_classes, \
                "overlapping extensions! %s " % instantiated_document.extension

            self.__extension_to_classes[instantiated_document.extension] = document_type

        self._file_extensions = []
        self._file_minimum = file_minimum

    def save(self, save_path: str) -> None:
        """
        Saves all the selected file extensions to a given path.
        @param save_path: A system path where the fabricated-documents will go.
        """
        assert len(self._file_extensions) > 0, "No extensions set!"

        """
        Create and add a list of instantiated objects this Mockingbird object will output. _file_extensions
        is set by the user / developer.
        """
        doc_array = []
        for ext in self._file_extensions:
            doc_array.append(self.__extension_to_classes.get(ext))

        while len(self._meta_data_object) < self._file_minimum:
            """
            Keep repeating the process until we've reached our _file_minimum. This probably over-generates, but over
            generating is easier than under. 
            """
            for x in range(len(doc_array)):
                """
                Copy the sensitive-data inputted into this Mockingbird instance, and inject it into each child-object
                in this for loop. Since every object all inherits from the same __BaseDocument type, polymorphism
                is invoked here so each child-object will have the same sensitive-information as it's parent 
                Mockingbird instance. 
                """

                # Create an object for each class selected
                child_class = doc_array[x]
                child_object = child_class()

                # Clone over the sensitive-data in "self" into all the children objects.
                child_object.clone_sensitive_data(other=self)

                # Save each child object
                child_object.save(save_path)

                # Update Mockingbird's meta-data to now include the meta-data of it's child-objects
                self._meta_data_object.add_other_meta_data(child_object._meta_data_object)

    @final
    def set_file_extensions(self, extensions: list) -> None:
        """
        Sets the output extension types.
        """
        for ext in extensions:
            assert ext in self.__extension_to_classes, "extension %s not found in Mockingbird" % ext

        self._file_extensions = extensions

    @final
    def set_all_extensions(self) -> None:
        """
        Enables all extensions.
        """
        all_extensions = list(self.__extension_to_classes.keys())
        self._file_extensions = all_extensions
