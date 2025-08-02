#!/usr/bin/env python3
"""
修复 reports.json 文件，确保它只包含实际存在的HTML文件
"""

import os
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_reports_json():
    """修复 reports.json 文件，确保只包含实际存在的HTML文件"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    html_dir = os.path.join(project_root, 'daily_html')
    reports_json_path = os.path.join(project_root, 'reports.json')
    
    # 检查HTML目录是否存在
    if not os.path.exists(html_dir):
        logging.error(f"HTML目录不存在: {html_dir}")
        return
    
    # 获取实际存在的HTML文件
    actual_html_files = []
    if os.path.exists(html_dir):
        for filename in os.listdir(html_dir):
            if filename.endswith('.html'):
                # 验证文件确实存在且可读
                file_path = os.path.join(html_dir, filename)
                if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                    actual_html_files.append(filename)
                else:
                    logging.warning(f"文件存在但无法访问: {filename}")
    
    # 按文件名（日期）降序排序
    actual_html_files.sort(reverse=True)
    
    logging.info(f"找到 {len(actual_html_files)} 个实际存在且可访问的HTML文件")
    
    # 读取当前的 reports.json
    current_reports = []
    if os.path.exists(reports_json_path):
        try:
            with open(reports_json_path, 'r', encoding='utf-8') as f:
                current_reports = json.load(f)
            logging.info(f"当前 reports.json 包含 {len(current_reports)} 个文件")
        except (json.JSONDecodeError, FileNotFoundError):
            logging.warning("无法读取当前的 reports.json 文件")
    
    # 找出不存在的文件
    missing_files = [f for f in current_reports if f not in actual_html_files]
    if missing_files:
        logging.warning(f"发现 {len(missing_files)} 个不存在的文件:")
        for filename in missing_files:
            logging.warning(f"  - {filename}")
    
    # 找出新增的文件
    new_files = [f for f in actual_html_files if f not in current_reports]
    if new_files:
        logging.info(f"发现 {len(new_files)} 个新增的文件:")
        for filename in new_files:
            logging.info(f"  - {filename}")
    
    # 更新 reports.json
    try:
        with open(reports_json_path, 'w', encoding='utf-8') as f:
            json.dump(actual_html_files, f, indent=4, ensure_ascii=False)
        logging.info(f"已更新 reports.json，现在包含 {len(actual_html_files)} 个实际存在的文件")
        
        if missing_files:
            logging.info(f"已移除 {len(missing_files)} 个不存在的文件引用")
        if new_files:
            logging.info(f"已添加 {len(new_files)} 个新文件")
        if not missing_files and not new_files:
            logging.info("所有文件都存在且列表是最新的，无需修复")
            
    except Exception as e:
        logging.error(f"更新 reports.json 时发生错误: {e}")
    
    # 显示更新后的文件列表
    logging.info("更新后的文件列表:")
    for filename in actual_html_files:
        logging.info(f"  - {filename}")
    
    # 验证修复结果
    logging.info("\n验证修复结果:")
    logging.info(f"reports.json 中的文件数量: {len(actual_html_files)}")
    logging.info(f"实际存在的HTML文件数量: {len([f for f in os.listdir(html_dir) if f.endswith('.html')])}")
    
    # 检查是否还有不匹配
    remaining_mismatch = False
    for filename in actual_html_files:
        file_path = os.path.join(html_dir, filename)
        if not os.path.exists(file_path):
            logging.error(f"验证失败: {filename} 在reports.json中但文件不存在")
            remaining_mismatch = True
    
    if not remaining_mismatch:
        logging.info("✅ 修复验证成功：所有在reports.json中的文件都实际存在")
    else:
        logging.error("❌ 修复验证失败：仍有文件不匹配")

if __name__ == "__main__":
    fix_reports_json() 