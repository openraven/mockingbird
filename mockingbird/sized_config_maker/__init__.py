import copy
import math
import os
import pathlib
from tempfile import TemporaryDirectory
from typing import Dict, Tuple

import numpy as np

from .. import Mockingbird


def mb_to_b_conversion(size: float) -> float:
    return round(size * (1024 * 1024), 3)


def _parse_config(path: str) -> Dict[str, Tuple[list, list]]:
    """
    Loads the lookup table of pre-computed sizes. Note that if self._start_at changes, The table may not be accurate.
    :param path: Path of CSV file containing pre-computed step sizes.
    :return: A dictionary mapping file extensions to their steps and respective sizes.
    """

    loaded_dict = dict()
    with open(path, "r") as f:
        for line in f:
            ext, step, size = line.split(",")

            if ext not in loaded_dict:
                loaded_dict[ext] = [], []

            X, Y = loaded_dict[ext]
            X.append(float(step))
            Y.append(float(size))

    return loaded_dict


class SizedConfigMaker:
    """
    A class to create Mockingbird configurations that will match a users input size. It does this by making
    linear regressions and tracking the slope of how the file size changes with respect to how the config changes.

    Pre-computed lookup tables are provided, but they can always be re-computed by the user, should the versioning
    change.
    """

    def __init__(self, lookup_table_path=None):
        """
        :param lookup_table_path: Optional, a path pointing to a custom lookup table.
        """
        self.lookup_table = True

        self._sample_size = 15
        self._sample_distance = 4
        self._start_at = 50
        self._base_config = Mockingbird()._configurable_dict

        if not lookup_table_path:
            self._lookup_table_path = os.path.join(pathlib.Path(__file__).parent.absolute(), "lookup_table.csv")
        else:
            self._lookup_table_path = lookup_table_path

        self._dump_recompute_values = False
        self._loaded_lookup_table = _parse_config(self._lookup_table_path)
        self._workspace = TemporaryDirectory()

    def get_sized_config(self, ext: str, desired_MB: float) -> dict:
        """
        Returns a dictionary that will try to generate files of a given extension within the magnitude of desired_MB.

        :param ext: Selected extension. Notice that only a single extension here is selectable, not a list.
        :param desired_MB: The desired size in megabytes of the file.
        :return: A dictionary mapping file extensions to their steps and respective sizes.
        """

        if self.lookup_table and ext in self._loaded_lookup_table:
            X, Y = self._loaded_lookup_table[ext]
        else:
            X, Y = self._re_compute(ext)

        m, b = np.polyfit(X, Y, 1)

        """
        Formula Derivation
        y = mx + b
        y - b = mx
        (y - b) / m = x
        """
        # Converting above formula into a lambda function
        find_x = lambda y: (y - b) / m

        # Plug in x into the re-arranged linear regression having converted the user input from MB to bytes
        # then floor the result.
        scale_factor = math.floor(find_x(mb_to_b_conversion(desired_MB)))

        # Return a new config with the scaled config.
        return self._apply_delta_to_config(scale_factor)

    def _re_compute_all_extensions(self) -> None:
        """
        A nifty script to generate lookup charts for all extensions.

        Be sure to enable _dump_recompute_values if you're trying to use this method generating a new re-compute set.
        """

        # Get a list of all the extensions Mockingbird currently supports.
        for item in Mockingbird().all_documents:

            if not self._dump_recompute_values:
                print("warn: self._dump_recompute_values is false.")

            self._re_compute(item.EXT)

    def _re_compute(self, ext: str) -> Tuple[list, list]:
        """
        Re-computes the lookup table for a given extension. Modify the '_dump_recompute_values' variable to True
        to re-dump the lookup table (for development purposes only).

        :param ext: extension string.
        :return: An sk-learn ready (X,Y) tuple of ordered lists ready to be trained.
        """

        x_axis = []
        y_axis = []

        for x in range(self._sample_size):
            print("%d of %d" % (len(x_axis), self._sample_size))
            delta = x * self._sample_distance
            x_axis.append(delta)
            y_axis.append(self._get_size_of_step(delta=delta, extension=ext))

        if self._dump_recompute_values:

            with open(self._lookup_table_path, "a+") as f:
                for x in range(0, len(y_axis)):
                    f.write("%s,%s,%s\n" % (ext, x_axis[x], y_axis[x]))

        return x_axis, y_axis

    def _get_size_of_step(self, delta: int, extension: str) -> float:
        """
        Given an arbitrary "delta" integer, create a new Mockingbird instance with the configuration scaled by that
        "delta". Find the average file size over 10 files, and that will be considered the size of the delta.

        :param delta: Some integer to scale the configuration by a scalar value.
        :param extension: File extension.
        :return: A float containing the average file size.
        """

        with TemporaryDirectory() as temp_dir:
            new_config = self._apply_delta_to_config(delta)

            mockingbird_test = Mockingbird(config_file=new_config, file_minimum=90)
            mockingbird_test.add_sensitive_data("ssn", ["555-02-3333"])
            mockingbird_test.set_file_extensions(extensions=[extension])
            mockingbird_test.save(temp_dir)

            meta_data_dict = mockingbird_test.metadata

            size = meta_data_dict["total_size_bytes"]
            length = len(meta_data_dict["file_sizes_bytes"])
            average_bytes = int(size / length)

            return average_bytes

    def _apply_delta_to_config(self, delta: int) -> dict:
        """
        Returns a configuration that changes the tunable parameters by a "delta" amount.

        :param delta: How much to scale the parameters by.
        :return: A configuration with adjustable parameters scaled by a "delta" amount.
        """
        new_config = copy.copy(self._base_config)
        new_config["base_structured_data"]["entries_range"] = [self._start_at + (delta * 100),
                                                               self._start_at + 1 + (delta * 100)]
        new_config["base_structured_data"]["dictionary_range"] = [50, 51]  # note, this can be adjusted as well.
        new_config["base_document"]["upper_bounds_delta"] = self._start_at + (delta * 100)

        return new_config
