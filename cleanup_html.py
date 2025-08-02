#!/usr/bin/env python3
"""
独立的HTML文件清理脚本
可以单独运行来清理旧的多日HTML文件，保留所有单日HTML文件
"""

import os
import sys
import logging
from datetime import date
from src.html_generator import cleanup_old_html_files

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """主函数"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    html_dir = os.path.join(project_root, 'daily_html')
    
    # 检查HTML目录是否存在
    if not os.path.exists(html_dir):
        logging.error(f"HTML目录不存在: {html_dir}")
        sys.exit(1)
    
    # 显示清理前的文件信息
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    logging.info(f"清理前HTML文件数量: {len(html_files)}")
    
    if html_files:
        logging.info("当前HTML文件:")
        for filename in sorted(html_files):
            logging.info(f"  - {filename}")
    
    # 执行清理
    logging.info("开始清理旧的多日HTML文件（保留所有单日文件）...")
    cleanup_old_html_files(html_dir, keep_days=[10, 20, 30])
    
    # 清理完成后更新 reports.json
    try:
        reports_json_path = os.path.join(project_root, 'reports.json')
        if os.path.exists(html_dir) and os.path.isdir(html_dir):
            html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
            html_files.sort(reverse=True)
            with open(reports_json_path, 'w', encoding='utf-8') as f:
                json.dump(html_files, f, indent=4, ensure_ascii=False)
            logging.info(f"清理后已更新 reports.json，包含 {len(html_files)} 个文件")
    except Exception as e:
        logging.error(f"更新 reports.json 时发生错误: {e}")
    
    # 显示清理后的文件信息
    remaining_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    logging.info(f"清理后HTML文件数量: {len(remaining_files)}")
    
    if remaining_files:
        logging.info("保留的HTML文件:")
        for filename in sorted(remaining_files):
            logging.info(f"  - {filename}")
    
    logging.info("清理完成!")


if __name__ == "__main__":
    main() 