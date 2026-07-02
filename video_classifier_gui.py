#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib.util
from pathlib import Path


def load_main():
    script_path = Path(__file__).with_name("视频分类GUI.py")
    spec = importlib.util.spec_from_file_location("video_classifier_gui_cn", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


if __name__ == "__main__":
    load_main()()
