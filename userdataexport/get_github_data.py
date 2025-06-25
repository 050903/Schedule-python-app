import requests
import json
import os
from utils import extract_skills_from_github_data

def get_github_data_enhanced(username, access_token=None):
    """
    Truy xuất thông tin hồ sơ và các kho lưu trữ công khai từ GitHub API,
    bao gồm chi tiết ngôn ngữ của từng kho lưu trữ.
    """
    base_url = "https://api.github.com"
    user_url = f"{base_url}/users/{username}"
    repos_url = f"{base_url}/users/{username}/repos"

    headers = {}
    if access_token:
        headers['Authorization'] = f'token {access_token}'

    all_data = {}
    
    print(f"Đang truy xuất thông tin hồ sơ của {username}...")
    try:
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        all_data['user_profile'] = user_data
        print("Truy xuất thông tin hồ sơ thành công.")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy xuất thông tin hồ sơ: {e}")
        all_data['user_profile'] = {"error": str(e)}

    print(f"Đang truy xuất các kho lưu trữ của {username} và chi tiết ngôn ngữ...")
    repos_list = []
    page = 1
    while True:
        try:
            paged_repos_url = f"{repos_url}?per_page=100&page={page}"
            repos_response = requests.get(paged_repos_url, headers=headers)
            repos_response.raise_for_status()
            current_repos = repos_response.json()
            
            if not current_repos:
                break # No more repositories

            for repo in current_repos:
                repo_name = repo['name']
                repo_details = {
                    'name': repo_name,
                    'html_url': repo['html_url'],
                    'description': repo['description'], # description can be None
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'fork': repo['fork'],
                    'stargazers_count': repo['stargazers_count'],
                    'forks_count': repo['forks_count'],
                    'main_language': repo['language'], # Primary language from repo list
                    'languages_detail': {} # To be populated
                }
                
                # Fetch detailed language stats for each repo
                languages_url = repo['languages_url']
                try:
                    languages_response = requests.get(languages_url, headers=headers)
                    languages_response.raise_for_status()
                    repo_details['languages_detail'] = languages_response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Cảnh báo: Không thể truy xuất chi tiết ngôn ngữ cho {repo_name}: {e}")
                    repo_details['languages_detail'] = {"error": str(e)}
                
                repos_list.append(repo_details)
            
            page += 1
            # Implement a small delay to avoid hitting rate limits too quickly
            # This is more critical for larger accounts or without a token
            # import time
            # time.sleep(0.1) 

        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi truy xuất kho lưu trữ (trang {page}): {e}")
            repos_list = {"error": str(e)}
            break
        except Exception as e:
            print(f"Lỗi không xác định khi truy xuất kho lưu trữ (trang {page}): {e}")
            repos_list = {"error": str(e)}
            break

    all_data['public_repositories'] = repos_list
    print(f"Truy xuất {len(repos_list)} kho lưu trữ thành công.")

    return all_data


if __name__ == "__main__":
    print("--- Bước 1: Thu thập Dữ liệu GitHub Nâng cao ---")
    github_username = input("Vui lòng nhập tên người dùng GitHub của bạn (ví dụ: octocat): ")
    
    github_access_token = input("Nhập GitHub Personal Access Token (để trống nếu không có/không muốn dùng): ")
    
    data = get_github_data_enhanced(github_username, github_access_token if github_access_token else None)

    output_filename = f"{github_username}_github_data_enhanced.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\nThông tin đã được lưu vào file: {output_filename}")
    print(f"Bạn có thể mở file '{output_filename}' để xem dữ liệu JSON.")

    print("\n--- Bước 2: Trích xuất Kỹ năng sơ bộ từ Dữ liệu đã thu thập ---")
    extracted_skills = extract_skills_from_github_data(data)
    
    print("\nCác Kỹ năng cơ bản được trích xuất:")
    print(f"Ngôn ngữ: {', '.join(extracted_skills['languages']) if extracted_skills['languages'] else 'Không có'}")
    print(f"Frameworks/Công cụ: {', '.join(extracted_skills['frameworks_tools']) if extracted_skills['frameworks_tools'] else 'Không có'}")
    print(f"Khái niệm/Lĩnh vực: {', '.join(extracted_skills['concepts']) if extracted_skills['concepts'] else 'Không có'}")