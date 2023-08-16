import os
from argparse import ArgumentParser
from csv import writer as csvwriter
from time import time
from datetime import timedelta

#parse given directory
# print in console ant text file size data  in format:
# -dir1             (size)
#   -subdir1        (size)
#   -subdir2        (size)
#       -file1      (size)
#       -file2      (size)
# -dir2
#...

DEBUG_LOGS = False
OUTPUT_TXT_FILE_NAME = "result.txt"
OUTPUT_CSV_FILE_NAME = "result.csv"

class Constants:
    # scan dict structure
    # key - full system path to item
    # value - list:
    # 0 - child files
    # 1 - child directories
    # 2 - item size (including children)
    # 3 - child files count
    # 4 - child directories count
    CHILD_FILES = 0
    CHILD_DIRS = 1
    SIZE = 2
    CHILD_FILES_COUNT = 3
    CHILD_DIRS_COUNT = 4


    def CreateEmptyDictItem():
        return [[],[], 0, 0, 0]
        

class DirScanner:
    def __init__(self, path = ""):
        self.scan_dir_path = path
        self.scan_dict = None


    def StartScan(self, scan_path = ""):
        if scan_path != "":
            self.scan_dir_path = scan_path

        if self.scan_dir_path == "":
            print (f"Scan path is not set. Canceled")

        self.scan_dict = {}

        self.CalcSize(self.scan_dir_path)


    def CalcSize(self, scan_path):     
        # create temporary dict item
        current_dir_item = Constants.CreateEmptyDictItem()

        try:
            for item in os.scandir(scan_path):
                # create full system path for item. use it as key in dictionary
                item_key = os.path.join(scan_path, item)

                # for file: calc size, add size to parent dir, add file to dict
                if os.path.isfile(item):
                    self.scan_dict[item_key] = Constants.CreateEmptyDictItem()
                    self.scan_dict[item_key][Constants.SIZE] = os.stat(item).st_size

                    current_dir_item[Constants.SIZE] = current_dir_item[Constants.SIZE] + self.scan_dict[item_key][Constants.SIZE]
                    current_dir_item[Constants.CHILD_FILES].append(item_key)
                    current_dir_item[Constants.CHILD_FILES_COUNT] = current_dir_item[Constants.CHILD_FILES_COUNT] + 1

                # for directory: recursive calc size, add dir in child dirs, sum size, child dirs and files
                elif os.path.isdir(item):
                    self.CalcSize(item_key)
                    if item_key not in self.scan_dict:
                        continue
                    current_dir_item[Constants.SIZE] = current_dir_item[Constants.SIZE] + self.scan_dict[item_key][Constants.SIZE]
                    current_dir_item[Constants.CHILD_FILES_COUNT] = current_dir_item[Constants.CHILD_FILES_COUNT] + \
                                                                    self.scan_dict[item_key][Constants.CHILD_FILES_COUNT]
                    current_dir_item[Constants.CHILD_DIRS_COUNT] = current_dir_item[Constants.CHILD_DIRS_COUNT] + \
                                                                    self.scan_dict[item_key][Constants.CHILD_DIRS_COUNT] + 1
                    current_dir_item[Constants.CHILD_DIRS].append(item_key)

            self.scan_dict[scan_path] = current_dir_item
        except PermissionError:
            if __name__ == '__main__':
                print (f"No permision for scaning directory or file: {scan_path}. Skip")
            return


    def BuildReadableString(self, name, indent_count, size):
        width = 1
        max_file_name_len = 100
        indent_str = "{0:>{width}}".format("", width = indent_count * width)
        name_str = "{0:<{width}}".format(name, width = max_file_name_len - (indent_count * width))
        size_str = "{0:>50,}".format(size)
        return indent_str + name_str + size_str


    def SaveTxt(self, path):
        tabs_count = 0
        stack = []
        stack.append((self.scan_dir_path, tabs_count))
        with open(path, "w", encoding="UTF-8") as txt_file:
            while len(stack) != 0:
                current_item, indent = stack.pop()

                short_name = os.path.split(current_item)[1]
                line = self.BuildReadableString(short_name, indent, self.scan_dict[current_item][Constants.SIZE])

                if (txt_file is not None):
                    txt_file.write(line + "\n")

                for subdir in self.scan_dict[current_item][Constants.CHILD_DIRS][::-1]:
                    stack.append((subdir, indent + 1))
                for subfile in self.scan_dict[current_item][Constants.CHILD_FILES][::-1]:
                    stack.append((subfile, indent + 1))


    def SaveCsv(self, path):
        tabs_count = 0
        stack = []
        stack.append((self.scan_dir_path, tabs_count))

        with open(path, 'w', encoding="UTF-8", newline='') as csv_file:
            csv_writer = csvwriter(csv_file)
            csv_writer.writerow(["full path","type","size (bytes)"])

            while len(stack) != 0:
                current_item, indent = stack.pop()
                if (csv_file is not None):
                    item_type = ""
                    if os.path.isfile(current_item):
                        item_type = 'file'
                    else:
                        item_type = 'dir' 
                    csv_writer.writerow([current_item, item_type, self.scan_dict[current_item][Constants.SIZE]])

                for subdir in self.scan_dict[current_item][Constants.CHILD_DIRS][::-1]:
                    stack.append((subdir, indent + 1))
                for subfile in self.scan_dict[current_item][Constants.CHILD_FILES][::-1]:
                    stack.append((subfile, indent + 1))
        


    def PrintConsole(self):
        for item_key, item_value in self.scan_dict.items():
            print(f"key: {item_key}")
            print(f"files: {item_value[Constants.CHILD_FILES]}")
            print(f"dirs: {item_value[Constants.CHILD_DIRS]}")
            print(f"size: {item_value[Constants.SIZE]}")
            print()

    
    def GetDict(self):
        return self.scan_dict


    def GetBaseInfo(self):
        base_info = []
        base_info.append(self.scan_dir_path)
        base_info.append(self.scan_dict[self.scan_dir_path][Constants.SIZE])
        base_info.append(self.scan_dict[self.scan_dir_path][Constants.CHILD_FILES_COUNT])
        base_info.append(self.scan_dict[self.scan_dir_path][Constants.CHILD_DIRS_COUNT])
        return base_info        



def validate_path(dir_path):
    # check if path exist and it is directory
    if (os.path.isdir(dir_path)):
        return True
    else:
        return False


def setup_arguments():
    parser = ArgumentParser()
    parser.add_argument("path")
    #parser.add_argument("-f", required=False, action='store_true', help="Ignore files in result output", dest='ignore_files')
    #parser.add_argument("-z", required=False, action='store_true', help="Ignore objects with zero size in result output", dest='ignore_zero_size')
    parser.add_argument("-no_csv", required=False, action='store_true', help="Do not save result to CSV file", dest='not_save_csv')
    parser.add_argument("-no_txt", required=False, action='store_true', help="Do not save result to TXT file", dest='not_save_txt')

    return parser


def log_time(start_time, end_time, line):
    diff = end_time - start_time
    time_str = str(timedelta(seconds=diff))
    print (line + time_str)


if __name__ == '__main__':
    script_start_time = time()
    #parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    print(args)

    dir_path = args.path
    # check if path exist and it is directory
    if (validate_path(dir_path)):
        print(f"{dir_path} is real path")
    else:
        print(f"{dir_path} is not real path")
        exit()

    scanner = DirScanner(dir_path)

    #print all directories and size data
    print(f"Start parsing: {dir_path}\n")

    calc_start_time = time()
    scanner.StartScan()
    calc_end_time = time()
    

    print_start_time = time()

    try:
        if args.not_save_csv == False:
            scanner.SaveCsv(OUTPUT_CSV_FILE_NAME)
    except IOError as e:
        print("Cannot save CSV file: " + e.strerror)
    
    try:
        if args.not_save_txt == False:
            scanner.SaveTxt(OUTPUT_TXT_FILE_NAME)
    except IOError as e:
        print("Cannot save TXT file: " + e.strerror)

    print_end_time = time()
    
    if DEBUG_LOGS:
        scanner.PrintConsole()
        scan_result_info = scanner.GetBaseInfo()
        print(f"Scan path: {scan_result_info[0]}\n\
              Dir size: {scan_result_info[1]}\n\
              Files count: {scan_result_info[2]}\n\
              Dirs count: {scan_result_info[3]}\n")

    script_end_time = time()

    log_time(calc_start_time, calc_end_time, "Size calculations time: ")
    log_time(print_start_time, print_end_time, "Print time: ")
    log_time(script_start_time, script_end_time, "Full script time: ")
