import os

def cleanup_temp_files(*file_paths):
    """
    Cleanup temporary files after use.

    Parameters
    ----------
    file_paths : str
        Paths to the files to be removed.

    Returns
    -------
    None
    """
    
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
