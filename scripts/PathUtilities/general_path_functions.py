from pathlib import Path, PureWindowsPath


def normalize_path(path):
    if path:
        if '\\' in path:
            windows_path = PureWindowsPath(path)
            normalized = Path(windows_path.as_posix())
        else:
            normalized = Path(path)
        return normalized
    else:
        return None


def create_path(directory, file_name, extension='.csv', folder=None):
    '''
    Creates a path from directory and file name inputs.
    Any folder that does not exist is made into a directory.
    '''        

    if folder:
        output_path = directory / folder
    else:
        output_path = directory
    
    if not output_path.is_dir():
        output_path.mkdir(parents=True)

    if file_name:
        file_path = output_path / file_name 
        path_with_extension = file_path.with_suffix(extension)
        return path_with_extension
    else:
        return output_path


def create_output_directory(user_input):
    output_dir_path = user_input['output_directory_path']
    output_folder = user_input['output_folder_name']

    if not output_folder:
        output_folder = 'processed_data'
    if not output_dir_path:
        full_output_dir = normalize_path(output_folder)
    else:
        full_output_dir = output_dir_path / output_folder
    if not full_output_dir.is_dir():
        full_output_dir.mkdir(parents=True)

    user_input['output_directory_path'] = full_output_dir
    return user_input