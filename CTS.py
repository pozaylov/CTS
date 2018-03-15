import os
from win32com.client import Dispatch


path_1 = 'C:\Program Files (x86)\Waves\MultiRack'
path_2 = 'C:\Program Files (x86)\Waves\MultiRack ref'

class waves_item(object):
    def __init__(self, path, selected_path):

        self.path = path
        self.view_path = path[len(selected_path):]  # Create view path
        self.version = "None"

        # Mac
        if os.name == 'posix':
            if path.endswith('.plist'):  # Create version
                x = open(path)
                try:
                    for i in x:
                        if i.count('.') == 3 and not i.__contains__('com'):
                            self.version = i[i.find('>') + 1:i.find('</')]
                except: UnicodeDecodeError

            self.name = ""  # Create filename
            if path.endswith('/Contents/Info.plist'):
                tempname = path[:-20]
                self.name = tempname[tempname.rfind(os.sep) + 1:]
            elif path.endswith('.framework/Versions/A/Resources/Info.plist'):
                tempname = path[:-32]
                self.name = tempname[tempname.rfind(os.sep) + 1:]
            elif path.endswith('/Resources/Info.plist'):
                tempname = path[:-21]
                self.name = tempname[tempname.rfind(os.sep) + 1:]



            else:
                self.name = path[path.rfind(os.sep)+1:]

        # Windows
        else:
            if path.endswith('.exe'):  # Create version
                ver_parser = Dispatch('Scripting.FileSystemObject')
                self.version = ver_parser.GetFileVersion(path)


            self.name = ""  # Create filename
            if "\Contents\Resources" in self.path:
                self.name = self.path[:self.path.find("\Contents\Resources")]
                self.name = self.name[self.name.rfind(os.sep)+1:]

            # if path.endswith('/Contents/Info.plist'):
            #     tempname = path[:-20]
            #     self.name = tempname[tempname.rfind(os.sep) + 1:]
            # elif path.endswith('.framework/Versions/A/Resources/Info.plist'):
            #     tempname = path[:-32]
            #     self.name = tempname[tempname.rfind(os.sep) + 1:]
            # elif path.endswith('/Resources/Info.plist'):
            #     tempname = path[:-21]
            #     self.name = tempname[tempname.rfind(os.sep) + 1:]

            else:
                self.name = path[path.rfind(os.sep)+1:]



def get_file_path(path):
    """"Get all files from given path"""
    all_files_path_list = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            files_path = os.path.join(subdir, file)
            if not files_path.endswith('.DS_Store'):  # filter out DS_Store files
                all_files_path_list.append(files_path)
    return all_files_path_list


def create_dict(class_list, version_filter):
    """Create dictionary from class items"""
    adict = {}

    for i in class_list:
        if version_filter:
            if i.version != "None":  # Filter out files without version
                path = i.view_path[:i.view_path.find(i.name)-1]
                adict[path + '@' + i.name] = {'version': i.version}
        if not version_filter:
            path = i.view_path[:i.view_path.find(i.name)-1]
            adict[path + '@' + i.name] = {'version': i.version}
    return adict

def compare_files(a, b):
    missing_files_in_a = []
    missing_files_in_b = []
    unmatch_versions = {}

    for file in a:
        if file not in b.keys():
            missing_files_in_b.append(file)
        elif a[file]['version'] not in b[file]['version']:
            unmatch_versions[file] = {'a version': a[file]['version'], 'b version': b[file]['version']}
    for file in b:
        if file not in a.keys():
            missing_files_in_a.append(file)

    return missing_files_in_a, missing_files_in_b, unmatch_versions


def main(path_1, path_2, version_filter):

    paths = [path_1, path_2]
    data = []

    for waves_path in paths:
        class_list = []

        files_path = get_file_path(waves_path)
        for file_path in files_path:
            file_path = waves_item(file_path, waves_path)
            class_list.append(file_path)

        data.append(create_dict(class_list, version_filter))

    files_a = data[0]
    files_b = data[1]

    missing_a, missing_b, unmatach = compare_files(files_a, files_b)

    # print(missing_a)
    # print(missing_b)
    # print(unmatach)

    return missing_a, missing_b, unmatach


if __name__ == '__main__':
    main(path_1, path_2, False)

