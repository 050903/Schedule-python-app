import json
import os

def render_cv_to_html(cv_data, output_filename="cv.html", profile_image_url=""):
    """
    Render CV data from a JSON object into an HTML file,
    mimicking the layout with sections for personal info, experience, skills, etc.
    Includes placeholders for a profile image and social links.
    """
    
    # Extract data from the JSON
    personal_info = cv_data.get('personal_info', {})
    objective_summary = cv_data.get('objective_summary', 'A highly motivated individual seeking new opportunities.')
    skills = cv_data.get('skills', {})
    project_experience = cv_data.get('project_experience', [])
    education = cv_data.get('education', [])
    awards_certifications = cv_data.get('awards_certifications', [])
    recommendations = cv_data.get('recommendations_for_growth', '')

    # Basic HTML Structure
    html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV của {personal_info.get('name', 'Bạn')}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="cv-container">
        <div class="left-column">
            <div class="profile-section">
                <img src="{profile_image_url}" alt="Ảnh đại diện" class="profile-pic" onerror="this.onerror=null; this.src='placeholder.png';">
                <h2>{personal_info.get('name', 'Tên của bạn').upper()}</h2>
                <p class="title">{personal_info.get('career_goal', 'Lập trình viên')}</p>
            </div>
            
            <div class="contact-section">
                <h3><i class="fas fa-address-card icon"></i> THÔNG TIN LIÊN HỆ</h3>
                <p><i class="fas fa-phone-alt icon"></i> <a href="tel:{personal_info.get('phone', '#')}">{personal_info.get('phone', 'N/A')}</a></p>
                <p><i class="fas fa-envelope icon"></i> <a href="mailto:{personal_info.get('email', '#')}">{personal_info.get('email', 'N/A')}</a></p>
                <p><i class="fab fa-github icon"></i> <a href="{personal_info.get('github', '#')}" target="_blank">{os.path.basename(personal_info.get('github', 'github.com/username'))}</a></p>
                <p><i class="fab fa-linkedin icon"></i> <a href="{personal_info.get('linkedin', '#')}" target="_blank">LinkedIn Profile</a></p>
                <p><i class="fas fa-map-marker-alt icon"></i> {personal_info.get('location', 'Ho Chi Minh City')}</p>
            </div>

            <div class="skills-section">
                <h3><i class="fas fa-laptop-code icon"></i> KỸ NĂNG</h3>
                <h4>Ngôn ngữ</h4>
                <ul>
                    {generate_list_items(skills.get('languages', []))}
                </ul>
                <h4>Frameworks & Công cụ</h4>
                <ul>
                    {generate_list_items(skills.get('frameworks_tools', []))}
                </ul>
                <h4>Cơ sở dữ liệu</h4>
                <ul>
                    {generate_list_items(skills.get('databases', []))}
                </ul>
                <h4>Khái niệm & Lĩnh vực</h4>
                <ul>
                    {generate_list_items(skills.get('concepts', []))}
                </ul>
            </div>

            <div class="education-section">
                <h3><i class="fas fa-graduation-cap icon"></i> HỌC VẤN</h3>
                {generate_education_html(education)}
            </div>

            <div class="awards-section">
                <h3><i class="fas fa-award icon"></i> CHỨNG CHỈ & GIẢI THƯỞNG</h3>
                {generate_awards_html(awards_certifications)}
            </div>
            
            <div class="recommendations-section">
                <h3><i class="fas fa-lightbulb icon"></i> LỜI KHUYÊN PHÁT TRIỂN</h3>
                <p>{recommendations}</p>
            </div>
        </div>

        <div class="right-column">
            <div class="summary-section">
                <h3><i class="fas fa-user-alt icon"></i> TÓM TẮT</h3>
                <p>{objective_summary}</p>
            </div>

            <div class="experience-section">
                <h3><i class="fas fa-briefcase icon"></i> KINH NGHIỆM DỰ ÁN</h3>
                {generate_project_html(project_experience)}
            </div>

            </div>
    </div>
</body>
</html>
"""

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"CV HTML đã được tạo và lưu vào file: {output_filename}")

def generate_list_items(items):
    """Helper function to generate <li> elements from a list."""
    return "".join([f"<li>{item}</li>" for item in items])

def generate_education_html(education_data):
    """Generates HTML for education section."""
    html = ""
    for edu in education_data:
        html += f"""
        <div class="education-item">
            <h4>{edu.get('degree', 'N/A')}</h4>
            <p>{edu.get('institution', '')} - {edu.get('year', '')}</p>
            <p>{edu.get('details', '')}</p>
        </div>
        """
    return html

def generate_awards_html(awards_data):
    """Generates HTML for awards/certifications section."""
    html = ""
    for award in awards_data:
        html += f"""
        <div class="award-item">
            <h4>{award.get('name', 'N/A')}</h4>
            <p>{award.get('details', '')}</p>
        </div>
        """
    return html

def generate_project_html(projects_data):
    """Generates HTML for project experience section."""
    html = ""
    for project in projects_data:
        html += f"""
        <div class="project-item">
            <h4><a href="{project.get('url', '#')}" target="_blank">{project.get('name', 'N/A')}</a></h4>
            <p>{project.get('summary', 'No summary available.')}</p>
        </div>
        """
    return html

if __name__ == "__main__":
    print("--- Bước 5: Render CV thành HTML ---")
    github_username = input("Nhập lại tên người dùng GitHub của bạn (ví dụ: 050903): ")
    
    cv_json_filepath = f"{github_username}_cv_content.json"
    
    if not os.path.exists(cv_json_filepath):
        print(f"Lỗi: Không tìm thấy tệp nội dung CV tại '{cv_json_filepath}'.")
        print("Vui lòng đảm bảo bạn đã chạy cv_analyzer_gemini.py trước đó.")
        exit()

    try:
        with open(cv_json_filepath, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Lỗi: Không thể đọc tệp JSON tại '{cv_json_filepath}'. Dữ liệu có thể bị hỏng.")
        exit()

    # Hỏi người dùng về URL ảnh đại diện
    profile_image_url_input = input("Nhập URL ảnh đại diện của bạn (để trống để dùng ảnh placeholder): ")

    # Tên file HTML đầu ra
    output_html_filename = f"{github_username}_cv.html"
    
    # Render CV ra HTML
    render_cv_to_html(cv_data, output_html_filename, profile_image_url_input)

    print(f"\nCV HTML đã sẵn sàng. Mở file '{output_html_filename}' trong trình duyệt để xem.")