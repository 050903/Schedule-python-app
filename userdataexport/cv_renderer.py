import json
import os

def load_cv_content(username):
    """
    Tải nội dung CV đã được tạo từ file JSON.
    """
    filepath = f"{username}_cv_content.json"
    if not os.path.exists(filepath):
        print(f"Lỗi: Không tìm thấy tệp nội dung CV tại '{filepath}'.")
        print("Vui lòng đảm bảo bạn đã chạy công cụ tạo CV trước đó.")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print(f"Lỗi: Không thể đọc tệp JSON tại '{filepath}'. Dữ liệu có thể bị hỏng.")
        return None

def render_cv_to_markdown(cv_data):
    """
    Chuyển đổi dữ liệu CV từ JSON sang định dạng Markdown.
    """
    markdown_output = []

    # Tiêu đề và Thông tin cá nhân
    personal_info = cv_data.get('personal_info', {})
    name = personal_info.get('name', 'Tên của bạn')
    
    markdown_output.append(f"# {name}")
    markdown_output.append("---")
    
    contact_details = []
    if personal_info.get('email') and personal_info['email'] != 'your.email@example.com':
        contact_details.append(f"**Email:** {personal_info['email']}")
    if personal_info.get('phone') and personal_info['phone'] != 'Your Phone Number':
        contact_details.append(f"**Điện thoại:** {personal_info['phone']}")
    if personal_info.get('linkedin') and personal_info['linkedin'] != 'Your LinkedIn Profile':
        contact_details.append(f"**LinkedIn:** [{personal_info['linkedin'].replace('https://', '')}]({personal_info['linkedin']})")
    if personal_info.get('github'):
        contact_details.append(f"**GitHub:** [{personal_info['github'].replace('https://github.com/', '')}]({personal_info['github']})")
    
    markdown_output.append(" | ".join(contact_details))
    markdown_output.append("\n")

    # Tóm tắt Mục tiêu/Hồ sơ
    objective_summary = cv_data.get('objective_summary', '')
    if objective_summary:
        markdown_output.append("## Tóm tắt Hồ sơ")
        markdown_output.append("---")
        markdown_output.append(f"{objective_summary}\n")

    # Kỹ năng
    skills = cv_data.get('skills', {})
    has_skills = any(skills.get(key) for key in ['languages', 'frameworks_tools', 'databases', 'concepts'])
    if has_skills:
        markdown_output.append("## Kỹ năng")
        markdown_output.append("---")
        if skills.get('languages'):
            markdown_output.append(f"**Ngôn ngữ lập trình:** {', '.join(skills['languages'])}")
        if skills.get('frameworks_tools'):
            markdown_output.append(f"**Frameworks & Công cụ:** {', '.join(skills['frameworks_tools'])}")
        if skills.get('databases'):
            markdown_output.append(f"**Cơ sở dữ liệu:** {', '.join(skills['databases'])}")
        if skills.get('concepts'):
            markdown_output.append(f"**Khái niệm & Lĩnh vực:** {', '.join(skills['concepts'])}")
        markdown_output.append("\n")

    # Kinh nghiệm Dự án
    project_experience = cv_data.get('project_experience', [])
    if project_experience:
        markdown_output.append("## Kinh nghiệm Dự án")
        markdown_output.append("---")
        for project in project_experience:
            name = project.get('name', 'Tên dự án')
            url = project.get('url', '#')
            summary = project.get('summary', 'Mô tả dự án.')
            
            markdown_output.append(f"### [{name}]({url})")
            markdown_output.append(f"- {summary}")
            markdown_output.append("\n")

    # Học vấn
    education = cv_data.get('education', [])
    if education:
        markdown_output.append("## Học vấn")
        markdown_output.append("---")
        for edu in education:
            degree = edu.get('degree', 'Bằng cấp/Chương trình')
            details = edu.get('details', '')
            markdown_output.append(f"- **{degree}**")
            if details:
                markdown_output.append(f"  {details}")
            markdown_output.append("\n")

    # Chứng chỉ & Giải thưởng
    certifications = cv_data.get('awards_certifications', [])
    if certifications:
        markdown_output.append("## Chứng chỉ & Giải thưởng")
        markdown_output.append("---")
        for cert in certifications:
            name = cert.get('name', 'Tên chứng chỉ/Giải thưởng')
            details = cert.get('details', '')
            markdown_output.append(f"- **{name}**")
            if details:
                markdown_output.append(f"  {details}")
            markdown_output.append("\n")
    
    # Khuyến nghị phát triển
    recommendations = cv_data.get('recommendations_for_growth', '')
    if recommendations and recommendations != "Tiếp tục học hỏi và xây dựng dự án để phát triển.": # Only show if AI provided meaningful advice
        markdown_output.append("## Khuyến nghị Phát triển Cá nhân")
        markdown_output.append("---")
        markdown_output.append(f"{recommendations}\n")


    return "\n".join(markdown_output)

if __name__ == "__main__":
    print("--- Bước 4: Render CV từ Dữ liệu JSON ---")
    github_username = input("Nhập lại tên người dùng GitHub đã dùng để tạo tệp CV (ví dụ: 050903): ")
    
    # Tải nội dung CV đã tạo
    cv_data = load_cv_content(github_username)
    if not cv_data:
        exit()

    # Render CV sang Markdown
    markdown_cv = render_cv_to_markdown(cv_data)

    output_markdown_filename = f"{github_username}_cv.md"
    with open(output_markdown_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_cv)

    print(f"\nCV của bạn đã được tạo và lưu vào file: {output_markdown_filename}")
    print("\n--- Nội dung CV đã Render (Markdown) ---")
    print(markdown_cv)
    print("\nBạn có thể mở file .md này bằng bất kỳ trình soạn thảo văn bản nào.")
    print("Để chuyển sang PDF, bạn có thể sử dụng các công cụ trực tuyến hoặc plugin trong VS Code (ví dụ: Markdown PDF, Pandoc).")