# =====Libraries importation=====
import sys
import os
import time
import logging
import datetime
import argparse
# ===============================

# For the next comments, files and folders will be named files to simplify the comments


def log(filename: str, option: int) -> None:
    """
    Logging to a file
    :param filename: The path to log
    :param option: The option of the logger
    :rtype: None
    """
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date time with format
    # Option 1 for a new file
    if option == 1:
        logging.info(str(date) + " " + filename + " was added.")
    # Option 2 for a removed file
    elif option == 2:
        logging.info(str(date) + " " + filename + " was removed.")
    # Option 3 for a modified file
    elif option == 3:
        logging.info(str(date) + " " + filename + " was modified.")

    # Option 4 for the first crawl
    elif option == 4:
        logging.info(str(date) + " " + filename + " was found.")


class FileList:
    list: list = []  # The list of Files
    debug: bool = False  # The bool to set if the app runs in debug mode
    log_file: str = ""  # The Path of the log file

    def __init__(self, debug: bool, log_file: str) -> None:
        """
        Constructor of the the class
        :rtype: None
        :param debug: to set if the app runs in debug mode
        :param log_file: the path of the log file
        """
        self.debug = debug
        self.log_file = log_file

    def length(self) -> int:
        """
        Return the length of the file list
        :rtype: int
        :return: the length of the list
        """
        return len(self.list)

    def add(self, file: str) -> None:
        """
        Add a file to the list
        :rtype: None
        """
        new_file: File = File(file, os.stat(file))  # We define a new file based on the string passed in argument
        self.list.append(new_file)  # We append the new File variable to the list

    def add_list(self, filelist: list, first: bool) -> None:
        """
        Add a list of file to the list
        :param filelist: A list of str containing path of files and folders
        :param first: A boolean to test if this add_list is for the first crawl
        :rtype: None
        """
        for f in filelist:  # We iterate through the list
            self.add(f)  # We add every file to the list
            if first:
                log(f, 4)  # We use the logger to print all added files if this is the first crawl
            else:
                log(f, 1)  # We use the logger to print all added files if this is not

    def compare(self, filelist: list) -> None:
        """
        Compare the actual list with the one passed in arguments,
        modify the list if needed and display the messages accordingly
        :param filelist: A list of str containing path of folders and files
        :rtype: None
        """
        # If the list is empty we can't compare with something thus we just need to add every file
        if self.length == 0:
            self.add_list(filelist, False)
            return None
        # Else we iterate through the list
        for file in filelist:
            contains = False  # Variable to store the possible match
            corresponding_file: File  # Variable to store the file matched
            for f in self.list:
                if f.same_name(file):  # If the file and the path match
                    contains = True  # We have a match
                    corresponding_file = f  # and we store the matched file to compare the attributes later
            if contains:  # If we have a match
                if not corresponding_file.same_attributes(file):  # but the attributes don't match
                    log(file, 3)  # We log the change
                    corresponding_file.attributes = os.stat(file)  # And we update the attributes of the file
            else:  # If there is no match
                log(file, 1)  # We log the creation of the file
                self.add(file)  # And we add it to
        for f in self.list:  # We also need to compare in the other way to seek for removed files
            if f.path not in filelist:  # If the file has been deleted
                log(f.path, 2)  # We log the removal
                self.list.remove(f)  # And we remove the file from the list


class File:
    path = ""  # The absolute path
    attributes = dict()  # The attributes of the file

    def __init__(self, path: str, attributes: dict) -> None:
        """
        Constructor of the the class
        :rtype: None
        :param path: the absolute path of the file
        :param attributes: the attributes of the file
        """
        self.attributes = attributes
        self.path = path

    def same_name(self, file: str) -> bool:
        """
        Compare the file's path with a path passed in arguments
        :param file: The path to compare
        :rtype: bool
        :return: True is th path match
        """
        return self.path == file

    def same_attributes(self, file: str) -> bool:
        """
        Compare the file's attributes with the ones from a give path
        :param file: The path to compare
        :rtype: bool
        :return: True if the attributes match
        """
        attributes = os.stat(file)
        return attributes == self.attributes


def ask_folder_location() -> str:
    """
    Ask the user for the folder to observe
    :rtype: str
    :return: The path of the folder to observe
    """
    local_folder = input("\nLocation of the local folder: ")
    # While the path isn't found, we ask again
    while not os.path.exists(local_folder):
        local_folder = input("The specified path was not found.\n\nLocal folder of the machine : ")
    return local_folder


def ask_log_file_location() -> str:
    """
    Ask the user for the log file
    :rtype: str
    :return: The log file's path
    """
    log_file_location = input("\nLocation of the log file: ")
    # While the path doesn't exist, we ask again
    while not os.path.exists(log_file_location):
        log_file_location = input("The specified path was not found.\n\nLocation of the log file : ")
    return log_file_location


def folder_analyze(local_folder: str, subfolders_max_number: int) -> list:
    """
    Walk through the local_folder as deeply as the subfolders_max_number value
    :param local_folder: Path of the folder
    :param subfolders_max_number: maximal depth of the walk
    :rtype : list
    :return: a list of path found if the local_folder
    """
    files_list = []
    # We iterate through all the files and folders in the local_folder alphabetically
    for path, dirs, files in os.walk(local_folder, topdown=True):
        # For all the files
        files = [f for f in files if f[0] is not "."]
        for name in files:
            # We add them by their absolute path to the file list
            files_list.append(os.path.join(path, name))
        # For the sub folders
        for name in dirs:
            # We add them by their absolute path to the file list
            files_list.append(os.path.join(path, name))
        # We only register the paths if the depth is less than the maximum depth
        if path.count(os.sep) >= subfolders_max_number:
            del dirs[:]
    return files_list


def main_function() -> None:
    parser = argparse.ArgumentParser(description='Observe a folder and log the changes.')
    parser.add_argument("folder_location", help='the absolute path of the folder to observe')
    parser.add_argument("log_file_location", help='the absolute path of the log file')
    parser.add_argument('-n', dest='new_log_file', help='specify that the log file doesn\'t already exists',
                        action="store_true")
    parser.add_argument('--debug', dest='debug', help='run in debug mode',
                        action="store_true")
    parser.add_argument('-d', dest='depth', const=5, default=5,
                        nargs='?', type=int, help='the numbers of subfolders to take into account.\n'
                                                  'Default 5, main 0, max 10.')
    parser.add_argument('-f', dest='frequency', const=15, default=15,
                        nargs='?', type=int, help='the refresh rate of the crawler in seconds.\n'
                                                  'Default 15, min 1, max 3600')

    args = parser.parse_args()

    if args.new_log_file:
        try:
            open(args.log_file_location, 'a').close()
        except IOError:
            print("Unable to create log file please enter an existing one.")
            args.log_file_location = ask_log_file_location()
    else:
        if not os.path.exists(args.log_file_location):
            print("Unable to find the log file.")
            args.log_file_location = ask_log_file_location()

    if not os.path.exists(args.folder_location):
        print("Unable to find the folder")
        args.folder_location = ask_folder_location()
    args.depth = 5 if args.depth not in range(0,11) else args.depth
    args.frequency = 15 if args.frequency not in range(1, 3601) else args.frequency

    logging.basicConfig(format='[INFO] %(message)s', filename=args.log_file_location, level=logging.INFO)
    files = FileList(args.debug, args.log_file_location)
    files.add_list(folder_analyze(args.folder_location, args.depth), True)
    while True:
        time.sleep(args.frequency)
        files.compare(folder_analyze(args.folder_location, args.depth))


if __name__ == "__main__":
    main_function()

