#!/usr/bin/env python3
"""
测试HTML文件清理功能
"""

import os
import json
from datetime import date, timedelta
from src.html_generator import cleanup_old_html_files, generate_multi_day_html_with_cleanup


def create_test_html_files(html_dir: str):
    """创建测试用的HTML文件"""
    os.makedirs(html_dir, exist_ok=True)
    
    today = date.today()
    test_files = []
    
    # 创建最近30天的测试文件
    for i in range(30):
        test_date = today - timedelta(days=i)
        filename = f"{test_date.strftime('%Y_%m_%d')}.html"
        filepath = os.path.join(html_dir, filename)
        
        # 创建简单的HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test {test_date}</title>
        </head>
        <body>
            <h1>Test HTML for {test_date}</h1>
            <p>This is a test file for {test_date}</p>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        test_files.append(filename)
        print(f"创建测试文件: {filename}")
    
    # 创建一些多日文件
    multi_day_files = [
        f"{today.strftime('%Y_%m_%d')}_to_{(today - timedelta(days=9)).strftime('%Y_%m_%d')}.html",
        f"{(today - timedelta(days=10)).strftime('%Y_%m_%d')}_to_{(today - timedelta(days=19)).strftime('%Y_%m_%d')}.html",
        f"{(today - timedelta(days=20)).strftime('%Y_%m_%d')}_to_{(today - timedelta(days=29)).strftime('%Y_%m_%d')}.html"
    ]
    
    for filename in multi_day_files:
        filepath = os.path.join(html_dir, filename)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Multi-day {filename}</title>
        </head>
        <body>
            <h1>Multi-day HTML: {filename}</h1>
            <p>This is a multi-day test file</p>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        test_files.append(filename)
        print(f"创建多日测试文件: {filename}")
    
    return test_files


def test_cleanup():
    """测试清理功能"""
    print("开始测试HTML文件清理功能...")
    
    # 创建测试目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_html_dir = os.path.join(project_root, 'test_html')
    
    # 创建测试文件
    print("创建测试HTML文件...")
    test_files = create_test_html_files(test_html_dir)
    
    # 显示清理前的文件数量
    files_before = len([f for f in os.listdir(test_html_dir) if f.endswith('.html')])
    print(f"清理前文件数量: {files_before}")
    
    # 执行清理
    print("\n执行清理...")
    print("注意：现在只清理多日文件，保留所有单日文件")
    cleanup_old_html_files(test_html_dir, keep_days=[10, 20, 30])
    
    # 显示清理后的文件数量
    files_after = len([f for f in os.listdir(test_html_dir) if f.endswith('.html')])
    print(f"清理后文件数量: {files_after}")
    
    # 显示保留的文件
    remaining_files = [f for f in os.listdir(test_html_dir) if f.endswith('.html')]
    remaining_files.sort()
    print(f"\n保留的文件:")
    for filename in remaining_files:
        print(f"  - {filename}")
    
    # 清理测试目录
    import shutil
    shutil.rmtree(test_html_dir)
    print(f"\n已删除测试目录: {test_html_dir}")
    
    print("测试完成!")


if __name__ == "__main__":
    test_cleanup() 