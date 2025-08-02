#!/usr/bin/env python3
"""
简单测试新的清理逻辑：保留所有单日文件，只清理多日文件
"""

import os
import logging
from datetime import date, timedelta
from src.html_generator import cleanup_old_html_files

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_files(html_dir: str):
    """创建测试文件"""
    os.makedirs(html_dir, exist_ok=True)
    
    today = date.today()
    
    # 创建单日文件（应该全部保留）
    single_day_files = []
    for i in range(50):  # 创建50个单日文件
        test_date = today - timedelta(days=i)
        filename = f"{test_date.strftime('%Y_%m_%d')}.html"
        filepath = os.path.join(html_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"<html><body>Single day file for {test_date}</body></html>")
        single_day_files.append(filename)
        print(f"创建单日文件: {filename}")
    
    # 创建多日文件（应该按规则清理）
    multi_day_files = []
    for i in range(0, 40, 10):  # 创建4个多日文件
        end_date = today - timedelta(days=i)
        start_date = end_date - timedelta(days=9)
        filename = f"{start_date.strftime('%Y_%m_%d')}_to_{end_date.strftime('%Y_%m_%d')}.html"
        filepath = os.path.join(html_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"<html><body>Multi-day file from {start_date} to {end_date}</body></html>")
        multi_day_files.append(filename)
        print(f"创建多日文件: {filename}")
    
    return single_day_files, multi_day_files

def test_new_cleanup_logic():
    """测试新的清理逻辑"""
    print("=== 测试新的清理逻辑 ===")
    print("规则：保留所有单日文件，只清理多日文件")
    
    # 创建测试目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_html_dir = os.path.join(project_root, 'test_cleanup_simple')
    
    # 创建测试文件
    print("\n1. 创建测试文件...")
    single_files, multi_files = create_test_files(test_html_dir)
    
    # 显示清理前的文件
    all_files = [f for f in os.listdir(test_html_dir) if f.endswith('.html')]
    print(f"\n2. 清理前文件总数: {len(all_files)}")
    print(f"   单日文件: {len(single_files)}")
    print(f"   多日文件: {len(multi_files)}")
    
    # 执行清理
    print("\n3. 执行清理...")
    cleanup_old_html_files(test_html_dir, keep_days=[10, 20, 30])
    
    # 显示清理后的文件
    remaining_files = [f for f in os.listdir(test_html_dir) if f.endswith('.html')]
    remaining_single = [f for f in remaining_files if '_to_' not in f]
    remaining_multi = [f for f in remaining_files if '_to_' in f]
    
    print(f"\n4. 清理后文件总数: {len(remaining_files)}")
    print(f"   保留的单日文件: {len(remaining_single)}")
    print(f"   保留的多日文件: {len(remaining_multi)}")
    
    # 验证结果
    print(f"\n5. 验证结果:")
    print(f"   单日文件是否全部保留: {'✓' if len(remaining_single) == len(single_files) else '✗'}")
    print(f"   多日文件是否按规则清理: {'✓' if len(remaining_multi) < len(multi_files) else '✗'}")
    
    # 清理测试目录
    import shutil
    shutil.rmtree(test_html_dir)
    print(f"\n6. 已删除测试目录: {test_html_dir}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_new_cleanup_logic() 