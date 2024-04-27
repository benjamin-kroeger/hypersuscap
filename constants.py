import json
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
