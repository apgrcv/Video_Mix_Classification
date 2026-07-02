#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib.util
from pathlib import Path
import sys


def load_main():
    script_path = Path(__file__).with_name("视频分类脚本.py")
    spec = importlib.util.spec_from_file_location("video_classifier_core", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


if __name__ == "__main__":
    sys.exit(load_main()())
