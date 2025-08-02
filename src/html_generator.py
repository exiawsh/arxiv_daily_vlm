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
    
    # Load and combine papers from all selected days
    all_papers = []
    date_range = []
    
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
                date_range.append(file_date)
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
        start_date = min(date_range)
        end_date = max(date_range)
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
    
    # Generate output filename
    if len(date_range) == 1:
        output_filename = f"{date_range[0].strftime('%Y_%m_%d')}.html"
    else:
        start_date = min(date_range)
        end_date = max(date_range)
        output_filename = f"{start_date.strftime('%Y_%m_%d')}_to_{end_date.strftime('%Y_%m_%d')}.html"
    
    output_filepath = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Successfully generated multi-day HTML: {output_filepath}")
        logging.info(f"Included {len(all_papers)} papers from {len(date_range)} days")
    except IOError as e:
        logging.error(f"Error writing HTML file {output_filepath}: {e}")


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