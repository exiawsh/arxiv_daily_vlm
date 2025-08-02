import json
import os
import logging
from datetime import date, datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader


def generate_html_from_json(json_file_path: str, template_dir: str, template_name: str, output_dir: str):
    """Reads paper data from a JSON file and generates an HTML page using a Jinja2 template.

    Args:
        json_file_path: Path to the input JSON file.
        template_dir: Directory containing the Jinja2 template.
        template_name: Name of the Jinja2 template file.
        output_dir: Directory where the generated HTML file will be saved.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
            # Sort papers by overall_priority_score in descending order
            papers.sort(key=lambda x: x.get('overall_priority_score', 0), reverse=True)
    except FileNotFoundError:
        logging.error(f"JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        logging.error(f"Could not decode JSON from {json_file_path}")
        return

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)

    # Extract date from filename (assuming format like YYYY-MM-DD.json)
    try:
        filename = os.path.basename(json_file_path)
        date_str = filename.split('.')[0]
        report_date = date.fromisoformat(date_str)
        formatted_date = report_date.strftime("%Y_%m_%d")
        page_title = f"ArXiv CS.CV Papers (Image/Video Generation) - {report_date.strftime('%B %d, %Y')}"
    except (IndexError, ValueError):
        logging.warning(f"Could not extract date from filename {filename}. Using default.")
        today = date.today()
        formatted_date = today.strftime("%Y_%m_%d")
        page_title = f"ArXiv CS.CV Papers (Image/Video Generation) - {today.strftime('%B %d, %Y')}"


    generation_time = datetime.now(timezone.utc)
    html_content = template.render(papers=papers, title=page_title, report_date=report_date, generation_time=generation_time)

    output_filename = f"{formatted_date}.html"
    output_filepath = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Successfully generated HTML: {output_filepath}")
    except IOError as e:
        logging.error(f"Error writing HTML file {output_filepath}: {e}")


def generate_multi_day_html(json_dir: str, template_dir: str, template_name: str, output_dir: str, days: int = 10):
    """Generates an HTML page containing papers from multiple days (up to specified number of days).
    
    Args:
        json_dir: Directory containing JSON files.
        template_dir: Directory containing the Jinja2 template.
        template_name: Name of the Jinja2 template file.
        output_dir: Directory where the generated HTML file will be saved.
        days: Number of days to include (default 10, max 10).
    """
    # Limit days to maximum of 10
    days = min(days, 10)
    
    # Get all JSON files and sort them by date (newest first)
    json_files = []
    if os.path.exists(json_dir):
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                try:
                    date_str = filename.split('.')[0]
                    file_date = date.fromisoformat(date_str)
                    json_files.append((file_date, filename))
                except (IndexError, ValueError):
                    continue
    
    # Sort by date (newest first) and take the most recent 'days' files
    json_files.sort(reverse=True)
    json_files = json_files[:days]
    
    if not json_files:
        logging.warning("No valid JSON files found for multi-day HTML generation.")
        return
    
    # Calculate the date range for this generation
    date_range = [file_date for file_date, _ in json_files]
    start_date = min(date_range)
    end_date = max(date_range)
    
    # Generate the expected output filename
    if len(date_range) == 1:
        output_filename = f"{date_range[0].strftime('%Y_%m_%d')}.html"
    else:
        output_filename = f"{start_date.strftime('%Y_%m_%d')}_to_{end_date.strftime('%Y_%m_%d')}.html"
    
    output_filepath = os.path.join(output_dir, output_filename)
    
    # Check if the file already exists
    if os.path.exists(output_filepath):
        logging.info(f"Multi-day HTML file already exists: {output_filepath}. Skipping generation.")
        return
    
    # Load and combine papers from all selected days
    all_papers = []
    
    for file_date, filename in json_files:
        json_filepath = os.path.join(json_dir, filename)
        try:
            with open(json_filepath, 'r', encoding='utf-8') as f:
                papers = json.load(f)
                # Add date information to each paper
                for paper in papers:
                    paper['source_date'] = file_date.isoformat()
                    paper['source_date_formatted'] = file_date.strftime('%B %d, %Y')
                all_papers.extend(papers)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Error reading {json_filepath}: {e}")
            continue
    
    if not all_papers:
        logging.warning("No papers found in the selected JSON files.")
        return
    
    # Sort all papers by overall_priority_score in descending order
    all_papers.sort(key=lambda x: x.get('overall_priority_score', 0), reverse=True)
    
    # Create date range string for title
    if len(date_range) == 1:
        date_range_str = date_range[0].strftime('%B %d, %Y')
    else:
        if start_date == end_date:
            date_range_str = start_date.strftime('%B %d, %Y')
        else:
            date_range_str = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    
    page_title = f"ArXiv CS.CV Papers (Image/Video Generation) - {date_range_str}"
    
    # Load template and render
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    
    generation_time = datetime.now(timezone.utc)
    html_content = template.render(
        papers=all_papers, 
        title=page_title, 
        report_date=date_range[0],  # Use the most recent date as primary date
        generation_time=generation_time,
        date_range=date_range,
        total_papers=len(all_papers)
    )
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Successfully generated multi-day HTML: {output_filepath}")
        logging.info(f"Included {len(all_papers)} papers from {len(date_range)} days")
    except IOError as e:
        logging.error(f"Error writing HTML file {output_filepath}: {e}")


def cleanup_old_html_files(html_dir: str, keep_days: list = [10, 20, 30]):
    """定期清理旧的HTML文件，保留所有单日文件，只清理多日文件。
    
    Args:
        html_dir: HTML文件目录
        keep_days: 要保留的多日文件天数列表，默认保留最近10天、10-20天、20-30天的多日文件
    """
    if not os.path.exists(html_dir):
        logging.warning(f"HTML目录不存在: {html_dir}")
        return
    
    today = date.today()
    single_day_files = []
    multi_day_files = []
    
    # 收集所有HTML文件及其日期
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            try:
                # 处理单日文件 (YYYY_MM_DD.html)
                if '_to_' not in filename:
                    date_str = filename.replace('.html', '').replace('_', '-')
                    file_date = date.fromisoformat(date_str)
                    single_day_files.append((file_date, filename))
                # 处理多日文件 (YYYY_MM_DD_to_YYYY_MM_DD.html)
                else:
                    # 提取结束日期作为文件日期
                    end_date_str = filename.split('_to_')[-1].replace('.html', '').replace('_', '-')
                    file_date = date.fromisoformat(end_date_str)
                    multi_day_files.append((file_date, filename))
            except (ValueError, IndexError):
                logging.warning(f"无法解析文件名中的日期: {filename}")
                continue
    
    # 保留所有单日文件
    files_to_keep = set()
    for file_date, filename in single_day_files:
        files_to_keep.add(filename)
    
    logging.info(f"保留所有单日文件: {len(single_day_files)} 个")
    
    # 处理多日文件
    if multi_day_files:
        # 按日期排序
        multi_day_files.sort(key=lambda x: x[0], reverse=True)
        
        # 计算要保留的多日文件
        for keep_day in keep_days:
            cutoff_date = today - timedelta(days=keep_day)
            for file_date, filename in multi_day_files:
                if file_date >= cutoff_date:
                    files_to_keep.add(filename)
        
        logging.info(f"保留多日文件: {len([f for f in files_to_keep if '_to_' in f])} 个")
    else:
        logging.info("没有找到多日文件")
    
    # 删除不在保留列表中的文件（只删除多日文件）
    deleted_count = 0
    for file_date, filename in multi_day_files:
        if filename not in files_to_keep:
            file_path = os.path.join(html_dir, filename)
            try:
                os.remove(file_path)
                logging.info(f"已删除旧的多日文件: {filename} (日期: {file_date})")
                deleted_count += 1
            except OSError as e:
                logging.error(f"删除文件失败 {filename}: {e}")
    
    logging.info(f"清理完成: 删除了 {deleted_count} 个多日文件，保留了 {len(files_to_keep)} 个文件（包含所有单日文件）")


def generate_multi_day_html_with_cleanup(json_dir: str, template_dir: str, template_name: str, 
                                        output_dir: str, days: int = 10, cleanup: bool = True):
    """生成多天HTML文件并可选地清理旧文件。
    
    Args:
        json_dir: JSON文件目录
        template_dir: 模板目录
        template_name: 模板文件名
        output_dir: 输出目录
        days: 包含的天数
        cleanup: 是否在生成后清理旧文件
    """
    # 生成多天HTML
    generate_multi_day_html(json_dir, template_dir, template_name, output_dir, days)
    
    # 如果需要清理，则执行清理
    if cleanup:
        logging.info("开始清理旧的HTML文件...")
        cleanup_old_html_files(output_dir)
        
        # 清理完成后更新 reports.json
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            reports_json_path = os.path.join(project_root, 'reports.json')
            
            if os.path.exists(output_dir) and os.path.isdir(output_dir):
                html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
                html_files.sort(reverse=True)
                with open(reports_json_path, 'w', encoding='utf-8') as f:
                    json.dump(html_files, f, indent=4, ensure_ascii=False)
                logging.info(f"清理后已更新 reports.json，包含 {len(html_files)} 个文件")
        except Exception as e:
            logging.error(f"更新 reports.json 时发生错误: {e}")


# Example usage (for testing purposes):
if __name__ == '__main__':
    # Create dummy data and directories for local testing
    dummy_papers = [
        {
            "title": "Awesome Paper 1 on Image Generation",
            "summary": "This paper introduces a revolutionary technique for generating images...",
            "authors": ["Author A", "Author B"],
            "url": "https://arxiv.org/pdf/2301.00001"
        },
        {
            "title": "Video Generation with Diffusion Models",
            "summary": "Exploring the use of diffusion models for high-fidelity video generation...",
            "authors": ["Author C"],
            "url": "https://arxiv.org/pdf/2301.00002"
        }
    ]
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dummy_json_dir = os.path.join(project_root, 'daily_json')
    dummy_html_dir = os.path.join(project_root, 'daily_html')
    dummy_template_dir = os.path.join(project_root, 'templates')
    dummy_template_name = 'paper_template.html' # Make sure this exists

    os.makedirs(dummy_json_dir, exist_ok=True)
    os.makedirs(dummy_html_dir, exist_ok=True)
    os.makedirs(dummy_template_dir, exist_ok=True)

    # Create a dummy template if it doesn't exist
    dummy_template_path = os.path.join(dummy_template_dir, dummy_template_name)
    if not os.path.exists(dummy_template_path):
        with open(dummy_template_path, 'w') as f:
            f.write("<h1>{{ title }}</h1><ul>{% for paper in papers %}<li><a href=\"{{ paper.url }}\">{{ paper.title }}</a>: {{ paper.summary }}</li>{% endfor %}</ul>")

    today_str = date.today().isoformat()
    dummy_json_filename = f"{today_str}.json"
    dummy_json_filepath = os.path.join(dummy_json_dir, dummy_json_filename)

    with open(dummy_json_filepath, 'w', encoding='utf-8') as f:
        json.dump(dummy_papers, f, indent=4)

    logging.basicConfig(level=logging.INFO) # Add basic config for testing
    logging.info(f"Running example generation...")
    generate_html_from_json(
        json_file_path=dummy_json_filepath,
        template_dir=dummy_template_dir,
        template_name=dummy_template_name,
        output_dir=dummy_html_dir
    )
    logging.info("Example generation finished.")