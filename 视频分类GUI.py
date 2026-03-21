#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from collections import defaultdict
import shutil
import 视频分类脚本 as core


class VideoClassifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('视频分类工具')
        self.root.geometry('1200x760')
        self.preview_assignments = []
        self.preview_source_dir = ''
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill=tk.X)

        ttk.Label(top, text='目标目录').grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.dir_var = tk.StringVar(value=str(Path.cwd()))
        ttk.Entry(top, textvariable=self.dir_var).grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(top, text='浏览', command=self.choose_dir).grid(row=0, column=2, padx=(8, 0))

        ttk.Label(top, text='每文件夹最大文件数').grid(row=1, column=0, sticky=tk.W, pady=(8, 0), padx=(0, 8))
        self.max_files_var = tk.StringVar(value='25')
        ttk.Entry(top, textvariable=self.max_files_var, width=12).grid(row=1, column=1, sticky=tk.W, pady=(8, 0))

        ttk.Label(top, text='扩展名').grid(row=1, column=1, sticky=tk.W, pady=(8, 0), padx=(140, 8))
        self.ext_var = tk.StringVar(value='mp4,avi,mkv,mov,wmv,flv,webm')
        ttk.Entry(top, textvariable=self.ext_var).grid(row=1, column=1, sticky=tk.EW, pady=(8, 0), padx=(200, 0))

        btns = ttk.Frame(top)
        btns.grid(row=0, column=3, rowspan=2, padx=(12, 0), sticky=tk.NS)
        ttk.Button(btns, text='预览', command=self.preview).pack(fill=tk.X)
        ttk.Button(btns, text='执行', command=self.execute).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btns, text='清空日志', command=self.clear_log).pack(fill=tk.X, pady=(8, 0))

        top.columnconfigure(1, weight=1)

        summary = ttk.Frame(self.root, padding=(12, 0))
        summary.pack(fill=tk.X)
        self.summary_var = tk.StringVar(value='待预览')
        ttk.Label(summary, textvariable=self.summary_var).pack(anchor=tk.W)

        middle = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        middle.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        left = ttk.Frame(middle)
        right = ttk.Frame(middle)
        middle.add(left, weight=1)
        middle.add(right, weight=2)

        ttk.Label(left, text='目标文件夹').pack(anchor=tk.W)
        self.folder_tree = ttk.Treeview(left, columns=('count',), show='headings', height=18)
        self.folder_tree.heading('count', text='文件夹 / 文件数')
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_select)

        ttk.Label(right, text='文件明细').pack(anchor=tk.W)
        self.file_tree = ttk.Treeview(right, columns=('file', 'key'), show='headings', height=18)
        self.file_tree.heading('file', text='文件名')
        self.file_tree.heading('key', text='开头键')
        self.file_tree.column('file', width=640, anchor=tk.W)
        self.file_tree.column('key', width=220, anchor=tk.W)
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        log_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        log_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(log_frame, text='日志').pack(anchor=tk.W)
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def choose_dir(self):
        selected = filedialog.askdirectory(title='选择视频目录')
        if selected:
            self.dir_var.set(selected)

    def clear_log(self):
        self.log_text.delete('1.0', tk.END)

    def log(self, text):
        self.log_text.insert(tk.END, text + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _validate_inputs(self):
        source_dir = self.dir_var.get().strip()
        if not source_dir:
            messagebox.showerror('错误', '请选择目标目录')
            return None
        try:
            max_files = int(self.max_files_var.get().strip())
        except ValueError:
            messagebox.showerror('错误', '每文件夹最大文件数必须为整数')
            return None
        if max_files <= 0:
            messagebox.showerror('错误', '每文件夹最大文件数必须大于 0')
            return None
        extensions = self.ext_var.get().strip()
        if not extensions:
            messagebox.showerror('错误', '扩展名不能为空')
            return None
        return source_dir, max_files, extensions

    def _render_preview(self):
        self.folder_tree.delete(*self.folder_tree.get_children())
        self.file_tree.delete(*self.file_tree.get_children())
        grouped = defaultdict(list)
        for item in self.preview_assignments:
            grouped[item['target_folder']].append(item)
        for folder in sorted(grouped.keys()):
            display = f'{folder} / {len(grouped[folder])}'
            self.folder_tree.insert('', tk.END, iid=folder, values=(display,))
        if grouped:
            first = sorted(grouped.keys())[0]
            self.folder_tree.selection_set(first)
            self.folder_tree.focus(first)
            self.show_folder_files(first)

    def show_folder_files(self, folder_name):
        self.file_tree.delete(*self.file_tree.get_children())
        rows = [x for x in self.preview_assignments if x['target_folder'] == folder_name]
        for row in rows:
            self.file_tree.insert('', tk.END, values=(row['file_name'], row['group_key']))

    def on_folder_select(self, _event):
        selected = self.folder_tree.selection()
        if not selected:
            return
        folder_name = selected[0]
        self.show_folder_files(folder_name)

    def preview(self):
        validated = self._validate_inputs()
        if not validated:
            return
        source_dir, max_files, extensions = validated
        self.log('开始预览...')
        preview_data = core.build_preview(source_dir, extensions, max_files)
        if not preview_data['ok']:
            self.summary_var.set('预览失败')
            self.log(preview_data['message'])
            messagebox.showwarning('提示', preview_data['message'])
            return
        self.preview_assignments = preview_data['result']['assignments']
        self.preview_source_dir = source_dir
        folder_count = len(set(x['target_folder'] for x in self.preview_assignments))
        file_count = len(self.preview_assignments)
        self.summary_var.set(f'预览完成：共 {file_count} 个可分配视频，分配到 {folder_count} 个文件夹')
        self.log(f'预览完成：共 {file_count} 个可分配视频，分配到 {folder_count} 个文件夹')
        self._render_preview()

    def execute(self):
        if not self.preview_assignments:
            messagebox.showwarning('提示', '请先执行预览')
            return
        validated = self._validate_inputs()
        if not validated:
            return
        source_dir, _, _ = validated
        if source_dir != self.preview_source_dir:
            messagebox.showwarning('提示', '目录已变更，请重新预览后再执行')
            return
        confirmed = messagebox.askyesno('确认执行', '将开始移动文件，是否继续？')
        if not confirmed:
            return
        moved = 0
        skipped = 0
        self.log('开始执行移动...')
        for assignment in self.preview_assignments:
            target_folder_path = Path(source_dir) / assignment['target_folder']
            if not target_folder_path.exists():
                target_folder_path.mkdir(parents=True, exist_ok=True)
                self.log(f'创建文件夹: {assignment["target_folder"]}')
            target_path = target_folder_path / assignment['file_name']
            if target_path.exists():
                skipped += 1
                self.log(f'[跳过] 文件已存在: {assignment["file_name"]}')
                continue
            shutil.move(assignment['source_path'], str(target_path))
            moved += 1
            self.log(f'[移动] {assignment["file_name"]} -> {assignment["target_folder"]}/')
        self.log(f'执行完成：移动 {moved} 个，跳过 {skipped} 个')
        messagebox.showinfo('完成', f'执行完成\n移动: {moved}\n跳过: {skipped}')


def main():
    root = tk.Tk()
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    app = VideoClassifierGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
