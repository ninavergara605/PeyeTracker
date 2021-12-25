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
