#!/usr/bin/env python3
"""
测试多天HTML生成功能
"""

import os
import json
from datetime import date, timedelta
from src.html_generator import generate_multi_day_html

def create_test_data():
    """创建测试用的JSON文件"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(project_root, 'daily_json')
    template_dir = os.path.join(project_root, 'templates')
    html_dir = os.path.join(project_root, 'daily_html')
    
    # 确保目录存在
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    
    # 创建测试数据
    test_papers = [
        {
            "title": f"Test Paper {i} on Image Generation",
            "summary": f"This is test paper {i} about image generation techniques...",
            "authors": [f"Author {i}A", f"Author {i}B"],
            "url": f"https://arxiv.org/pdf/2301.0000{i}",
            "overall_priority_score": 8.5 - i * 0.5
        }
        for i in range(1, 6)
    ]
    
    # 创建过去5天的测试文件
    for i in range(5):
        test_date = date.today() - timedelta(days=i)
        filename = f"{test_date.isoformat()}.json"
        filepath = os.path.join(json_dir, filename)
        
        # 为每天创建不同的论文
        daily_papers = []
        for j, paper in enumerate(test_papers):
            daily_paper = paper.copy()
            daily_paper["title"] = f"Day {i+1} - {paper['title']}"
            daily_paper["overall_priority_score"] = paper["overall_priority_score"] - i * 0.1
            daily_papers.append(daily_paper)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(daily_papers, f, indent=4, ensure_ascii=False)
        
        print(f"Created test file: {filename}")
    
    return json_dir, template_dir, html_dir

def test_multi_day_generation():
    """测试多天HTML生成"""
    print("开始测试多天HTML生成...")
    
    # 创建测试数据
    json_dir, template_dir, html_dir = create_test_data()
    
    # 生成多天HTML
    try:
        generate_multi_day_html(
            json_dir=json_dir,
            template_dir=template_dir,
            template_name='paper_template.html',
            output_dir=html_dir,
            days=10
        )
        print("✅ 多天HTML生成成功！")
        
        # 检查生成的文件
        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
        print(f"生成的HTML文件: {html_files}")
        
    except Exception as e:
        print(f"❌ 多天HTML生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_day_generation() 