import json
import os
import google.generativeai as genai
import textwrap # For formatting long text
from utils import extract_skills_from_github_data

# --- CẤU HÌNH API KEY CỦA GEMINI ---
# Bạn cần đặt API Key của Gemini ở đây hoặc từ biến môi trường
# KHUYẾN NGHỊ: Sử dụng biến môi trường để bảo mật tốt hơn
# os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"
# genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
# Hoặc trực tiếp nếu bạn hiểu rủi ro (chỉ để thử nghiệm nhanh):
genai.configure(api_key="AIzaSyA19pNhYXBOTvIxe1W7fc9SGwT4HjajDiQ") # <--- THAY THẾ BẰNG API KEY CỦA BẠN

# Khởi tạo mô hình Gemini
# Chọn model phù hợp. "gemini-pro" thường là lựa chọn tốt cho tác vụ này.
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def load_github_data(username):
    """
    Tải dữ liệu GitHub đã được thu thập từ file JSON.
    """
    filepath = f"{username}_github_data_enhanced.json"
    if not os.path.exists(filepath):
        print(f"Lỗi: Không tìm thấy tệp dữ liệu GitHub tại '{filepath}'.")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print(f"Lỗi: Không thể đọc tệp JSON tại '{filepath}'. Dữ liệu có thể bị hỏng.")
        return None

def analyze_and_summarize_project(repo_data, career_goal):
    """
    Sử dụng Gemini để phân tích một kho lưu trữ và tạo tóm tắt phù hợp cho CV.
    """
    repo_name = repo_data.get('name', 'Unknown Project')
    description = repo_data.get('description', 'No description provided.')
    main_language = repo_data.get('main_language', 'N/A')
    languages_detail = repo_data.get('languages_detail', {})
    html_url = repo_data.get('html_url', '#')
    
    # Chuyển chi tiết ngôn ngữ thành chuỗi dễ đọc
    lang_details_str = ", ".join([
        f"{lang} ({round(bytes / 1024)}KB)" for lang, bytes in languages_detail.items()
    ]) if languages_detail else "Không có chi tiết ngôn ngữ."

    prompt = textwrap.dedent(f"""
    Bạn là một trợ lý AI chuyên nghiệp trong việc viết CV.
    Tôi sẽ cung cấp thông tin về một dự án GitHub và mục tiêu nghề nghiệp của tôi.
    Hãy tạo một đoạn mô tả ngắn gọn (tối đa 3-4 dòng) cho dự án này, phù hợp để đưa vào phần "Kinh nghiệm Dự án" trong CV.
    Đoạn mô tả nên:
    1.  Nêu bật các **công nghệ chính** được sử dụng (ngôn ngữ, frameworks, công cụ).
    2.  Mô tả **chức năng hoặc mục đích chính** của dự án.
    3.  Gợi ý về **thành tựu hoặc kết quả** nếu có thể suy luận (ví dụ: phát triển một API, xây dựng giao diện người dùng tương tác).
    4.  Ưu tiên các chi tiết liên quan đến **mục tiêu nghề nghiệp** của tôi.

    **Thông tin dự án:**
    - Tên: {repo_name}
    - Mô tả GitHub: {description}
    - Ngôn ngữ chính: {main_language}
    - Chi tiết ngôn ngữ: {lang_details_str}
    - URL: {html_url}

    **Mục tiêu nghề nghiệp của tôi:** {career_goal}

    Ví dụ:
    "Phát triển ứng dụng web sử dụng React.js và Node.js để quản lý kho hàng, bao gồm giao diện người dùng tương tác và API RESTful."
    """)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Lỗi khi tạo tóm tắt cho dự án '{repo_name}': {e}")
        return f"Dự án: {repo_name} - {description} (Công nghệ: {main_language})"

def generate_cv_content(github_data, career_goal, additional_info=None):
    """
    Phân tích toàn bộ dữ liệu GitHub và mục tiêu nghề nghiệp để tạo ra nội dung CV.
    """
    user_profile = github_data.get('user_profile', {})
    public_repos = github_data.get('public_repositories', [])

    cv_content = {
        "personal_info": {
            "name": user_profile.get('name', user_profile.get('login', 'Your Name')),
            "email": user_profile.get('email', 'your.email@example.com'),
            "phone": additional_info.get('phone', 'Your Phone Number') if additional_info else 'Your Phone Number',
            "linkedin": additional_info.get('linkedin', 'Your LinkedIn Profile') if additional_info else 'Your LinkedIn Profile',
            "github": user_profile.get('html_url', f"https://github.com/{user_profile.get('login', 'username')}")
        },
        "objective_summary": "",
        "skills": {
            "languages": [],
            "frameworks_tools": [],
            "databases": [],
            "concepts": []
        },
        "project_experience": [],
        "education": additional_info.get('education', []) if additional_info else [],
        "awards_certifications": additional_info.get('certifications', []) if additional_info else []
    }

    # 1. Tạo tóm tắt mục tiêu nghề nghiệp
    objective_prompt = textwrap.dedent(f"""
    Bạn là một chuyên gia viết CV. Hãy tạo một đoạn tóm tắt mục tiêu nghề nghiệp (Career Objective/Summary) ngắn gọn (2-3 dòng)
    dành cho một người có hồ sơ GitHub sau và mục tiêu nghề nghiệp: '{career_goal}'.
    Tập trung vào các kỹ năng lập trình chính và kinh nghiệm thực tế qua các dự án.

    **Thông tin chung về hồ sơ GitHub:**
    - Tên người dùng: {user_profile.get('login')}
    - Số repo công khai: {user_profile.get('public_repos')}
    - Các ngôn ngữ chính đã phát hiện (ví dụ từ bước trước): {', '.join(extract_skills_from_github_data(github_data)['languages'])}
    """)
    try:
        objective_response = model.generate_content(objective_prompt)
        cv_content['objective_summary'] = objective_response.text.strip()
    except Exception as e:
        print(f"Lỗi khi tạo tóm tắt mục tiêu: {e}")
        cv_content['objective_summary'] = f"Kỹ sư phần mềm có kinh nghiệm với các dự án GitHub, tìm kiếm cơ hội trong lĩnh vực {career_goal}."


    # 2. Trích xuất và phân loại kỹ năng chi tiết hơn bằng AI
    # Dùng Gemini để giúp phân loại tốt hơn
    all_raw_languages = set()
    for repo in public_repos:
        if isinstance(repo, dict):
            if repo.get('main_language'):
                all_raw_languages.add(repo['main_language'])
            for lang in repo.get('languages_detail', {}):
                all_raw_languages.add(lang)
    
    # Combine extracted skills from previous basic analysis with more granular data
    basic_extracted = extract_skills_from_github_data(github_data)
    all_skills_list = sorted(list(set(basic_extracted['languages'] + basic_extracted['frameworks_tools'] + basic_extracted['concepts'])))

    if all_skills_list:
        skill_categorization_prompt = textwrap.dedent(f"""
        Phân loại các kỹ năng sau vào các nhóm: 'languages', 'frameworks_tools', 'databases', 'concepts'.
        Chỉ trả về một đối tượng JSON với các khóa là tên nhóm và giá trị là mảng các kỹ năng.
        Không thêm bất kỳ văn bản nào khác ngoài JSON.

        Kỹ năng cần phân loại: {', '.join(all_skills_list)}
        """)
        try:
            skill_response = model.generate_content(skill_categorization_prompt)
            # LLM might return code block, try to parse JSON
            json_text = skill_response.text.strip().replace('```json', '').replace('```', '')
            categorized_skills = json.loads(json_text)
            cv_content['skills']['languages'] = sorted(list(set(categorized_skills.get('languages', []))))
            cv_content['skills']['frameworks_tools'] = sorted(list(set(categorized_skills.get('frameworks_tools', []))))
            cv_content['skills']['databases'] = sorted(list(set(categorized_skills.get('databases', []))))
            cv_content['skills']['concepts'] = sorted(list(set(categorized_skills.get('concepts', []))))
        except Exception as e:
            print(f"Lỗi khi phân loại kỹ năng bằng AI: {e}. Sử dụng kỹ năng cơ bản.")
            cv_content['skills']['languages'] = basic_extracted['languages']
            cv_content['skills']['frameworks_tools'] = basic_extracted['frameworks_tools']
            cv_content['skills']['concepts'] = basic_extracted['concepts']
            # Databases might be empty if not explicitly extracted
            cv_content['skills']['databases'] = []


    # 3. Tạo tóm tắt dự án
    for i, repo in enumerate(public_repos):
        if i >= 5: # Giới hạn số lượng dự án hiển thị trong CV để giữ cho CV ngắn gọn
            print("Đã giới hạn số lượng dự án hiển thị trong CV (tối đa 5).")
            break
        if isinstance(repo, dict) and not repo.get('fork', False): # Bỏ qua các repo fork
            project_summary = analyze_and_summarize_project(repo, career_goal)
            if project_summary:
                cv_content['project_experience'].append({
                    "name": repo.get('name', 'N/A'),
                    "url": repo.get('html_url', '#'),
                    "summary": project_summary
                })
    
    # 4. Đề xuất cải thiện (tùy chọn) - Có thể thêm vào một phần riêng trong CV hoặc là lời khuyên sau CV
    recommendation_prompt = textwrap.dedent(f"""
    Dựa trên các kỹ năng được trích xuất: {', '.join(all_skills_list)}
    và mục tiêu nghề nghiệp: '{career_goal}',
    hãy đưa ra 2-3 lời khuyên ngắn gọn về các kỹ năng hoặc dự án bạn nên tập trung để đạt được mục tiêu đó.
    """)
    try:
        recommendation_response = model.generate_content(recommendation_prompt)
        cv_content['recommendations_for_growth'] = recommendation_response.text.strip()
    except Exception as e:
        print(f"Lỗi khi tạo khuyến nghị: {e}")
        cv_content['recommendations_for_growth'] = "Tiếp tục học hỏi và xây dựng dự án để phát triển."


    return cv_content

if __name__ == "__main__":
    print("--- Bước 3: Phân tích Dữ liệu và Tạo Nội dung CV ---")
    github_username = input("Nhập lại tên người dùng GitHub đã dùng để tạo tệp dữ liệu (ví dụ: 050903): ")
    
    # Tải dữ liệu đã thu thập
    github_data = load_github_data(github_username)
    if not github_data:
        exit()

    # Hỏi mục tiêu nghề nghiệp
    career_goal_input = input("Mục tiêu nghề nghiệp của bạn là gì (ví dụ: 'Frontend Developer', 'Data Scientist', 'DevOps Engineer')? ")

    # Hỏi thêm thông tin cá nhân (tùy chọn)
    additional_info = {
        "phone": input("Số điện thoại của bạn (để trống nếu không muốn hiển thị): "),
        "linkedin": input("URL LinkedIn của bạn (để trống nếu không có): "),
        "education": [], # Có thể mở rộng để hỏi nhiều trường
        "certifications": [] # Có thể mở rộng để hỏi nhiều chứng chỉ
    }
    edu_input = input("Bạn có kinh nghiệm học vấn nào muốn thêm không? (ví dụ: 'Cử nhân Khoa học Máy tính - Đại học ABC, 2020') - Nhấn Enter để bỏ qua: ")
    if edu_input:
        additional_info['education'].append({"degree": edu_input, "details": ""})

    cert_input = input("Bạn có chứng chỉ nào muốn thêm không? (ví dụ: 'AWS Certified Developer Associate') - Nhấn Enter để bỏ qua: ")
    if cert_input:
        additional_info['certifications'].append({"name": cert_input, "details": ""})


    # Tạo nội dung CV
    cv_final_content = generate_cv_content(github_data, career_goal_input, additional_info)

    # Lưu nội dung CV vào file JSON
    output_cv_filename = f"{github_username}_cv_content.json"
    with open(output_cv_filename, 'w', encoding='utf-8') as f:
        json.dump(cv_final_content, f, ensure_ascii=False, indent=4)

    print(f"\nNội dung CV đã được tạo và lưu vào file: {output_cv_filename}")
    print("\n--- CV Đã Tạo (Định dạng JSON) ---")
    print(json.dumps(cv_final_content, ensure_ascii=False, indent=4))
    print("\nBạn có thể sử dụng file JSON này để tạo CV ở định dạng khác (ví dụ: PDF, Word) hoặc chỉnh sửa thủ công.")