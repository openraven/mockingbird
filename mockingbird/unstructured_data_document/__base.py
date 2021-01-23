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

from abc import ABC, abstractmethod
from typing import List, Tuple

from mockingbird.__base import __BaseDocument


class __BaseUnstructuredDataType(__BaseDocument, ABC):
    """
    Create an array of dictionaries which can be used to organized structured-data documents. Since most structured
    data-types (csv, json, etc) are there to store key / value pairs, so this abstract-class facilitates those
    repeated functions.
    """

    def __init__(self, extension=None):
        super().__init__(extension=extension)

        # todo
        self._enumerated_bounds = 10

    # Abstract Methods #

    @abstractmethod
    def save(self, save_path: str) -> None:
        pass

    # Protected Methods #

    def _get_sensitive_soup(self) -> str:
        """
        Returns a "sensitive soup" of keyword/value pairs mixed between words.
        """

        pii_positions = self._get_embedded_positions()

        sensitive_soup = ""
        for x in range(self._total_entries):
            if x in pii_positions:
                # todo why replace "\n" with "\n\n"? I can't remember the reason. Has something to do with
                # generating certifications.
                sensitive_soup += pii_positions[x] + " " + self._get_sensitive_data(pii_positions[x]).replace("\n",
                                                                                                              "\n\n") + " "
            else:
                sensitive_soup += self._get_random_word() + " "

        return sensitive_soup

    def _get_chat_log(self) -> List[str]:
        """
        Returns a chat-log like list which can be used to simulate how sensitive-data may be leaked in a natural
        conversation.

        Example:
            kuroi_katto, [Jan 6, 2021 at 10:27:10 PM]:
                222 continuity 130864193002679 23318044137046 respirations 82053 22338507 minuses bricks 1
            Trem_Ble_Shin, [Jan 6, 2021 at 10:27:20 PM]:
                garage 98073611 3447848 stencil injectors boils span character landings 2851
            kuroi_katto, [Jan 6, 2021 at 10:27:10 PM]:
                Can you send me the ssn
            Trem_Ble_Shin, [Jan 6, 2021 at 10:27:20 PM]:
                Sure, my ssn is 555-5555
        """
        chat_log: List[str] = []

        pii_positions = self._get_embedded_positions()

        for x in range(self._total_entries):
            if x in pii_positions:
                keyword = pii_positions[x]
                chat_log.append("kuroi_katto, [Jan 6, 2021 at 10:27:10 PM]:")
                chat_log.append("Can you send me the %s" % keyword)

                chat_log.append("Trem_Ble_Shin, [Jan 6, 2021 at 10:27:20 PM]:")
                chat_log.append("Sure, my %s is %s" % (keyword, self._get_sensitive_data(keyword=keyword)))

            else:
                chat_log.append("kuroi_katto, [Jan 6, 2021 at 10:27:10 PM]:")
                chat_log.append(" ".join([self._get_random_word() for _ in range(self._enumerated_bounds)]))

                chat_log.append("Trem_Ble_Shin, [Jan 6, 2021 at 10:27:20 PM]:")
                chat_log.append(" ".join([self._get_random_word() for _ in range(self._enumerated_bounds)]))

        return chat_log

    def _get_enumerated_style(self) -> List[Tuple[str, List[str]]]:
        """
        Returns random-enumerated lists, with some of the enumerated lists containing sensitive-information.

        Example:
            SSN
              * 555-55-5555
              * 333-33-3333
        """

        pii_positions = self._get_embedded_positions()
        enumerations: List[Tuple[str, List[str]]] = []

        for x in range(self._total_entries):
            if x in pii_positions:
                keyword = pii_positions[x]
                sensitive_values = [self._get_sensitive_data(keyword) for _ in range(self._enumerated_bounds)]
                enumerations.append((keyword, sensitive_values))
            else:
                keyword = self._get_random_word()
                enumerated_values = [self._get_random_word() for _ in range(self._enumerated_bounds)]
                enumerations.append((keyword, enumerated_values))

        return enumerations
