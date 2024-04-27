import json
import logging
import os
from enum import Enum
from glob import glob


def _read_segments_specs(path_to_segments_specs: str):
    assert os.path.isdir(path_to_segments_specs), "Path does not exist"

    segments = []
    for segments_spec_path in glob(os.path.join(path_to_segments_specs, "*")):
        segment_name = segments_spec_path.split('_')[-1].rstrip('.json')
        with open(segments_spec_path, 'r') as seg_f:
            segments.append({"name": segment_name,
                             "specs": json.load(seg_f)})

    return segments


segments = _read_segments_specs('segments')

def _get_user_data(path_to_user_data: str):
    assert os.path.isdir(path_to_user_data), "Path does not exist"

    user_data = dict()

    for single_user_data_path in glob(os.path.join(path_to_user_data, "*")):
        with open(single_user_data_path,'r') as f:
            single_user_data = json.load(f)
            user_data[single_user_data['name'].lower()] = single_user_data

    return user_data


user_data = _get_user_data('profiles')
