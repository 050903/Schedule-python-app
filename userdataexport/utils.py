def extract_skills_from_github_data(github_data):
    """
    Trích xuất các kỹ năng cơ bản từ dữ liệu GitHub đã truy xuất.
    """
    skills = {
        'languages': set(),
        'frameworks_tools': set(),
        'concepts': set()
    }

    public_repos = github_data.get('public_repositories', [])
    if isinstance(public_repos, dict) and "error" in public_repos:
        print("Không thể trích xuất kỹ năng do lỗi truy xuất kho lưu trữ.")
        return { 'languages': [], 'frameworks_tools': [], 'concepts': [] }

    for repo in public_repos:
        if isinstance(repo, dict):
            if repo.get('main_language'):
                skills['languages'].add(repo['main_language'])

            for lang in repo.get('languages_detail', {}):
                skills['languages'].add(lang)

            description = repo.get('description')
            if description is not None:
                description = description.lower()
                if 'react' in description: skills['frameworks_tools'].add('React.js')
                if 'node' in description or 'express' in description: skills['frameworks_tools'].add('Node.js / Express')
                if 'python' in description and ('django' in description or 'flask' in description): skills['frameworks_tools'].add('Python (Django/Flask)')
                if 'java' in description and 'spring' in description: skills['frameworks_tools'].add('Java (Spring Boot)')
                if 'docker' in description: skills['frameworks_tools'].add('Docker')
                if 'kubernetes' in description: skills['frameworks_tools'].add('Kubernetes')
                if 'api' in description: skills['concepts'].add('API Development')
                if 'database' in description or 'sql' in description or 'nosql' in description: skills['concepts'].add('Database Management (SQL/NoSQL)')
                if 'machine learning' in description or 'ml' in description: skills['concepts'].add('Machine Learning')
                if 'data science' in description: skills['concepts'].add('Data Science')
                if 'web' in description: skills['concepts'].add('Web Development')
                if 'mobile' in description: skills['concepts'].add('Mobile Development')

    skills['languages'] = sorted(list(skills['languages']))
    skills['frameworks_tools'] = sorted(list(skills['frameworks_tools']))
    skills['concepts'] = sorted(list(skills['concepts']))

    return skills