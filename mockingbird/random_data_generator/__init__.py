import glob
import os
import pathlib
import re
import random
from typing import List, Set


class RandomDataGenerator:

    def __init__(self, glob_path=None, random_int_upper_bound=50):
        """
        Loads the files found in folder_path and puts them into memory to be used as random seed data to be embedded
        within various documents.
        """
        if glob_path == None:
            glob_path = os.path.join(pathlib.Path(__file__).parent.absolute(), "./books/*.txt")

        word_set = self.__extract_strings_from_folder(glob_path)
        number_set = self.__generate_number_set(len(word_set), random_int_upper_bound)

        self.data_set = list(word_set.union(number_set))


    @staticmethod
    def __generate_number_set(count: int, upper_bound: int) -> Set[str]:

        number_set = set()

        while len(number_set) < count:
            number_set.add(str(random.getrandbits(random.randint(1, upper_bound))))

        return number_set

    @staticmethod
    def __extract_strings_from_folder(glob_path: str) -> Set[str]:
        """
        Load each glob item into memory, parse into words, and remove anything that's not numerical or alphabetical.
        :param glob_path: A glob styled path
        :return: A set of words from the glob path.
        """
        word_set = set()

        list_of_files = glob.glob(glob_path)

        for file in list_of_files:

            with open(file, "r") as f:
                for line in f:
                    split = line.split(" ")
                    for word in split:
                        word_set.add(re.sub(r'[\W_]+', '', word))

        return word_set
