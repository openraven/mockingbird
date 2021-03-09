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

import os
import pathlib
from random import randint
from typing import List

import yaml


def load_yaml_settings(settings_file: str) -> dict:
    """
    Loads the yaml file into a dictionary using the absolute path of this file.
    This eliminates the need of having to manually locate the yaml file, so the file can be loaded from anywhere.

    @return: Dictionary containing tunable settings for document-fabricated items
    """

    file_path = os.path.join(pathlib.Path(__file__).parent.absolute(), settings_file)

    assert os.path.exists(file_path)
    with open(file_path) as fh:
        settings_yaml = yaml.load(fh, Loader=yaml.FullLoader)

    return settings_yaml


def get_int_in_range(bounds: List[int]) -> int:
    """
    A simple function to return a random integer between two ranges.

    We can't specify tuples in the yaml-config file, so instead input an array with two elements,
    representing the lower and upper bound.

    This function exists to reduce the logic in init's / having to do this for every abstract_document subclass
    is error prone / tedious.

    @param bounds: A list containing integers a,b (i.e [a,b])
    @return: A value between (a,b)
    """

    return randint(bounds[0], bounds[1])
