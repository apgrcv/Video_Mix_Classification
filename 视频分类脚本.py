#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}

def get_group_key(filename):
    base_name = Path(filename).stem
    match = re.match(r'^(.*?)开头(\d+)', base_name)
    if match:
        drama_name = match.group(1)
        start_number = match.group(2)
        if drama_name:
            group_key = f"{drama_name}开头{start_number}"
        else:
            group_key = f"开头{start_number}"
        return {
            'drama_name': drama_name,
            'start_number': start_number,
            'group_key': group_key
        }
    return None

def get_video_files(directory):
    video_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in VIDEO_EXTENSIONS:
                video_files.append(Path(root) / file)
    return video_files

def initialize_allocation(video_files):
    group_key_map = defaultdict(list)
    for file_path in video_files:
        info = get_group_key(file_path.name)
        if info:
            key = info['group_key']
            group_key_map[key].append({
                'file': file_path,
                'full_path': str(file_path),
                'group_key': key,
                'drama_name': info['drama_name'],
                'start_number': info['start_number']
            })
    return dict(group_key_map)

def allocate_videos(group_key_map):
    folders = []
    assignments = []
    
    all_videos = []
    for key, videos in group_key_map.items():
        all_videos.extend(videos)
    
    all_videos.sort(key=lambda x: x['group_key'])
    
    for video in all_videos:
        assigned = False
        
        for i, folder in enumerate(folders):
            if video['group_key'] not in folder:
                folder[video['group_key']] = video
                assignments.append({
                    'file_name': video['file'].name,
                    'source_path': video['full_path'],
                    'target_folder': f'分组结果_{i + 1:02d}',
                    'group_key': video['group_key']
                })
                assigned = True
                break
        
        if not assigned:
            new_folder = {video['group_key']: video}
            folders.append(new_folder)
            assignments.append({
                'file_name': video['file'].name,
                'source_path': video['full_path'],
                'target_folder': f'分组结果_{len(folders):02d}',
                'group_key': video['group_key']
            })
    
    return {
        'folders': folders,
        'assignments': assignments
    }

def show_preview(assignments):
    print('\n========== 预览分配结果 ==========\n')
    
    folder_groups = defaultdict(list)
    for a in assignments:
        folder_groups[a['target_folder']].append(a)
    
    for folder_name in sorted(folder_groups.keys()):
        items = folder_groups[folder_name]
        unique_keys = list(set(a['group_key'] for a in items))
        print(f'【{folder_name}】')
        print(f'  包含 {len(items)} 个视频，开头键：{", ".join(unique_keys)}')
        print()
        for item in items:
            print(f'    {item["file_name"]}')
        print()
    
    print('===================================')
    print(f'共 {len(assignments)} 个视频，分配到 {len(folder_groups)} 个目标文件夹')

def execute_move(assignments, base_dir):
    print('\n========== 开始执行移动 ==========\n')
    
    folder_mappings = {}
    
    for assignment in assignments:
        target_folder_path = Path(base_dir) / assignment['target_folder']
        
        if not target_folder_path.exists():
            target_folder_path.mkdir(parents=True, exist_ok=True)
            print(f'创建文件夹: {assignment["target_folder"]}')
        
        target_path = target_folder_path / assignment['file_name']
        
        if target_path.exists():
            print(f'[跳过] 文件已存在: {assignment["file_name"]}')
            continue
        
        shutil.move(assignment['source_path'], str(target_path))
        print(f'[移动] {assignment["file_name"]} -> {assignment["target_folder"]}/')
    
    print('\n===================================')
    print('执行完成！')

def main():
    parser = argparse.ArgumentParser(description='视频分类脚本 - 按开头分组视频')
    parser.add_argument('source_dir', help='视频所在的源目录路径')
    parser.add_argument('--execute', '-e', action='store_true', help='添加此参数才会执行移动，否则只预览')
    parser.add_argument('--extensions', '-ext', default='mp4,avi,mkv,mov,wmv,flv,webm', 
                        help='支持的视频格式，默认为 mp4,avi,mkv,mov,wmv,flv,webm')
    
    args = parser.parse_args()
    
    source_dir = args.source_dir
    
    if not os.path.exists(source_dir):
        print(f'错误: 目录不存在 - {source_dir}')
        return 1
    
    global VIDEO_EXTENSIONS
    VIDEO_EXTENSIONS = {f'.{ext.strip().lower()}' for ext in args.extensions.split(',')}
    
    print(f'扫描目录: {source_dir}')
    print('正在查找视频文件...')
    
    video_files = get_video_files(source_dir)
    
    if not video_files:
        print('未找到任何视频文件')
        return 0
    
    print(f'找到 {len(video_files)} 个视频文件')
    print('正在分析分组键...')
    
    group_key_map = initialize_allocation(video_files)
    
    if not group_key_map:
        print('警告: 未找到符合规则的视频文件（格式：剧名开头数字）')
        print('示例: 三万英尺开头1_xxxx.mp4')
        print('\n[调试信息] 当前目录下发现的部分文件:')
        for f in video_files[:5]:
            print(f'  - {f.name}')
        return 0
    
    print(f'发现 {len(group_key_map)} 个不同的分组键')
    
    result = allocate_videos(group_key_map)
    
    show_preview(result['assignments'])
    
    if args.execute:
        print()
        confirm = input('确认执行移动操作？(输入 y 确认，其他键取消): ')
        if confirm.lower() == 'y':
            execute_move(result['assignments'], source_dir)
        else:
            print('已取消执行')
    else:
        print()
        print('提示: 当前为预览模式，不会实际移动文件')
        print('如需执行移动，请添加 -e 或 --execute 参数')
    
    return 0

if __name__ == '__main__':
    exit(main())
