import pandas as pd
from scripts.ResultContainers.result_containers import create_result_paths


def export(result_dfs, user_input):
    result_paths = create_result_paths(user_input['output_directory_path'])

    for tag, df in result_dfs.items():
        if (not df.empty) and (tag in result_paths.keys()):
            path = result_paths[tag]
            df.to_csv(path)
