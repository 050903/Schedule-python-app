import streamlit as st
import re
import json
import os
import zipfile
from io import BytesIO
import time
from datetime import datetime

# Cấu hình trang
st.set_page_config(
    page_title="Project Genesis - Text to Website",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .code-preview {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

class WebsiteGenerator:
    def __init__(self):
        self.templates = { # Giữ nguyên template để làm fallback hoặc base
            'cửa hàng': {
                'type': 'ecommerce',
                'sections': ['header', 'hero', 'products', 'about', 'contact', 'footer'],
                'primary_color': '#e91e63',
                'secondary_color': '#ffffff'
            },
            'nhà hàng': {
                'type': 'restaurant', 
                'sections': ['header', 'hero', 'menu', 'about', 'contact', 'footer'],
                'primary_color': '#ff5722',
                'secondary_color': '#ffffff'
            },
            'công ty': {
                'type': 'corporate',
                'sections': ['header', 'hero', 'services', 'about', 'team', 'contact', 'footer'],
                'primary_color': '#2196f3',
                'secondary_color': '#ffffff'
            },
            'cá nhân': {
                'type': 'portfolio',
                'sections': ['header', 'hero', 'portfolio', 'skills', 'contact', 'footer'],
                'primary_color': '#9c27b0',
                'secondary_color': '#ffffff'
            },
            'blog': {
                'type': 'blog',
                'sections': ['header', 'hero', 'posts', 'about', 'contact', 'footer'],
                'primary_color': '#795548',
                'secondary_color': '#ffffff'
            }
        }
        
        self.color_map = {
            'đỏ': '#e53e3e', 'xanh': '#3182ce', 'vàng': '#d69e2e',
            'hồng': '#ed64a6', 'tím': '#805ad5', 'cam': '#dd6b20',
            'xanh lá': '#38a169', 'xanh lục': '#38a169',
            'đen': '#1a202c', 'trắng': '#ffffff', 'xám': '#718096'
        }

        # Định nghĩa các component có thể nhận diện và các từ khóa liên quan
        # Trong tương lai, đây sẽ là một thư viện Component Blueprints đồ sộ
        self.component_keywords = {
            'products': ['sản phẩm', 'cửa hàng', 'shop', 'bán'],
            'menu': ['thực đơn', 'món ăn', 'menu', 'đồ ăn'],
            'services': ['dịch vụ', 'phục vụ', 'service'],
            'portfolio': ['portfolio', 'dự án', 'work', 'tác phẩm'],
            'blog': ['blog', 'bài viết', 'tin tức', 'news'],
            'gallery': ['gallery', 'hình ảnh', 'ảnh', 'thư viện'],
            'team': ['đội ngũ', 'team', 'thành viên'],
            'testimonials': ['ý kiến khách hàng', 'testimonials', 'phản hồi'],
            'faq': ['hỏi đáp', 'faq', 'câu hỏi thường gặp'],
            'pricing': ['giá', 'bảng giá', 'pricing']
        }

        # Các component mặc định cho hầu hết các trang web
        self.default_components = ['header', 'hero', 'about', 'contact', 'footer']
    
    def analyze_input(self, user_input):
        """Phân tích đầu vào của người dùng và trích xuất thông tin, xây dựng cấu trúc component."""
        lower_input = user_input.lower()
        
        # 1. Trích xuất tên website
        site_name = "My Website"
        name_patterns = [
            r'tên[\s]*(?:là|:)?[\s]*[\'"]?([^\'".,\n]+)[\'"]?',
            r'gọi là[\s]*[\'"]?([^\'".,\n]+)[\'"]?',
            r'có tên[\s]*[\'"]?([^\'".,\n]+)[\'"]?'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                site_name = match.group(1).strip()
                break
        
        # 2. Xác định loại website (dùng để gợi ý các section ban đầu)
        website_type = 'corporate' # Mặc định
        template_info = self.templates['công ty'] # Mặc định
        
        for key, template in self.templates.items():
            if key in lower_input:
                website_type = template['type']
                template_info = template
                break
        
        # 3. Trích xuất màu sắc
        primary_color = template_info['primary_color'] # Lấy từ template ban đầu
        for color_name, color_code in self.color_map.items():
            if color_name in lower_input:
                primary_color = color_code
                break
        
        # 4. Trích xuất mô tả chung
        description = f"Website {website_type} chuyên nghiệp với thiết kế hiện đại."
        desc_patterns = [
            r'mô tả[\s]*:?[\s]*([^\n]+)',
            r'giới thiệu[\s]*:?[\s]*([^\n]+)',
            r'về[\s]+website[\s]*(?:là|:)?[\s]*([^\n]+)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                break

        # 5. Phân tích và xây dựng danh sách components
        # Đây là phần cải tiến chính: cố gắng nhận diện các component cụ thể
        
        # Bắt đầu với các component mặc định
        detected_components = set(self.default_components) 
        
        # Thêm các component dựa trên từ khóa trong input
        for component_name, keywords in self.component_keywords.items():
            for keyword in keywords:
                if keyword in lower_input:
                    detected_components.add(component_name)
                    break
        
        # Sắp xếp các component theo một thứ tự hợp lý (tùy chỉnh)
        # Đây là một heuristics đơn giản, trong tương lai có thể dùng LLM để sắp xếp
        ordered_components = []
        for comp in ['header', 'hero']: # Luôn ở đầu
            if comp in detected_components:
                ordered_components.append(comp)
                detected_components.remove(comp)
        
        # Thêm các component "nội dung" phổ biến
        content_order = ['products', 'menu', 'services', 'portfolio', 'blog', 'gallery', 'testimonials', 'team', 'faq', 'pricing']
        for comp in content_order:
            if comp in detected_components:
                ordered_components.append(comp)
                detected_components.remove(comp)
        
        # Các component còn lại (ví dụ: about, contact, footer)
        for comp in ['about', 'contact', 'footer']: # Luôn ở cuối hoặc gần cuối
            if comp in detected_components:
                ordered_components.append(comp)
                detected_components.remove(comp)
        
        # Cuối cùng, thêm bất kỳ component nào còn sót lại (nếu có)
        ordered_components.extend(list(detected_components))

        # Đặc tả chi tiết hơn cho từng component (cho phép tùy chỉnh sâu hơn)
        # Trong tương lai, đây sẽ là kết quả của việc gọi LLM với JSON Schema
        component_specs = []
        for comp_type in ordered_components:
            if comp_type == 'header':
                component_specs.append({"type": "header", "props": {"siteName": site_name}})
            elif comp_type == 'hero':
                 # Cố gắng trích xuất headline và tagline từ mô tả nếu có
                hero_headline_match = re.search(r'(?:tiêu đề chính|headline)[\s]*(?:là|:)?[\s]*["\']?([^"\']+)["\']?', user_input, re.IGNORECASE)
                hero_headline = hero_headline_match.group(1).strip() if hero_headline_match else f"Chào mừng đến với {site_name}"

                hero_tagline_match = re.search(r'(?:mô tả hero|tagline)[\s]*(?:là|:)?[\s]*["\']?([^"\']+)["\']?', user_input, re.IGNORECASE)
                hero_tagline = hero_tagline_match.group(1).strip() if hero_tagline_match else description

                component_specs.append({"type": "hero", "props": {"headline": hero_headline, "tagline": hero_tagline}})
            elif comp_type == 'about':
                # Cố gắng trích xuất nội dung about từ mô tả nếu có
                about_content_match = re.search(r'(?:về chúng tôi|about)[\s]*(?:nội dung|:)?[\s]*([^\n]+)', user_input, re.IGNORECASE)
                about_content = about_content_match.group(1).strip() if about_content_match else "Chúng tôi là một đội ngũ đam mê tạo ra các giải pháp web tuyệt vời."
                component_specs.append({"type": "about", "props": {"title": "Về chúng tôi", "content": about_content}})
            elif comp_type == 'products':
                component_specs.append({"type": "products", "props": {"title": "Sản phẩm của chúng tôi", "items": [{"name": "Sản phẩm A", "desc": "Mô tả A", "image": "https://via.placeholder.com/300x200?text=SP+A"}, {"name": "Sản phẩm B", "desc": "Mô tả B", "image": "https://via.placeholder.com/300x200?text=SP+B"}]}})
            elif comp_type == 'menu':
                component_specs.append({"type": "menu", "props": {"title": "Thực đơn của chúng tôi", "items": [{"name": "Món X", "desc": "Mô tả X", "image": "https://via.placeholder.com/300x200?text=Món+X"}, {"name": "Món Y", "desc": "Mô tả Y", "image": "https://via.placeholder.com/300x200?text=Món+Y"}]}})
            elif comp_type == 'services':
                component_specs.append({"type": "services", "props": {"title": "Dịch vụ của chúng tôi", "items": [{"name": "Dịch vụ 1", "desc": "Mô tả DV1"}, {"name": "Dịch vụ 2", "desc": "Mô tả DV2"}]}})
            elif comp_type == 'portfolio':
                component_specs.append({"type": "portfolio", "props": {"title": "Dự án nổi bật", "items": [{"name": "Dự án 1", "desc": "Mô tả DA1", "image": "https://via.placeholder.com/400x250?text=DA1"}, {"name": "Dự án 2", "desc": "Mô tả DA2", "image": "https://via.placeholder.com/400x250?text=DA2"}]}})
            elif comp_type == 'blog':
                component_specs.append({"type": "blog", "props": {"title": "Bài viết mới nhất", "posts": [{"title": "Bài blog 1", "desc": "Tóm tắt B1", "image": "https://via.placeholder.com/400x250?text=Blog+1"}, {"title": "Bài blog 2", "desc": "Tóm tắt B2", "image": "https://via.placeholder.com/400x250?text=Blog+2"}]}})
            elif comp_type == 'gallery':
                component_specs.append({"type": "gallery", "props": {"title": "Thư viện ảnh", "images": ["https://via.placeholder.com/400x300?text=Img+1", "https://via.placeholder.com/400x300?text=Img+2"]}})
            elif comp_type == 'team':
                component_specs.append({"type": "team", "props": {"title": "Đội ngũ của chúng tôi", "members": [{"name": "Thành viên 1", "role": "CEO", "image": "https://via.placeholder.com/150x150?text=TV1"}, {"name": "Thành viên 2", "role": "CTO", "image": "https://via.placeholder.com/150x150?text=TV2"}]}})
            elif comp_type == 'testimonials':
                component_specs.append({"type": "testimonials", "props": {"title": "Khách hàng nói gì về chúng tôi", "quotes": [{"text": "Dịch vụ tuyệt vời!", "author": "Khách hàng A"}, {"text": "Website rất chuyên nghiệp!", "author": "Khách hàng B"}]}})
            elif comp_type == 'faq':
                component_specs.append({"type": "faq", "props": {"title": "Câu hỏi thường gặp", "items": [{"question": "Câu hỏi 1?", "answer": "Trả lời 1."}, {"question": "Câu hỏi 2?", "answer": "Trả lời 2."}]}})
            elif comp_type == 'pricing':
                component_specs.append({"type": "pricing", "props": {"title": "Bảng giá dịch vụ", "plans": [{"name": "Cơ bản", "price": "100$", "features": ["Tính năng 1", "Tính năng 2"]}, {"name": "Nâng cao", "price": "200$", "features": ["Tính năng 1", "Tính năng 2", "Tính năng 3"]}]}})
            elif comp_type == 'contact':
                # Kiểm tra lại tính năng contact form có được yêu cầu không
                has_contact_form = 'liên hệ' in lower_input or 'contact form' in lower_input or 'biểu mẫu liên hệ' in lower_input
                component_specs.append({"type": "contact", "props": {"has_form": has_contact_form}})
            elif comp_type == 'footer':
                component_specs.append({"type": "footer", "props": {"siteName": site_name}})
        
        # Đây là cấu trúc output mới
        return {
            'site_name': site_name,
            'website_type': website_type, # Giữ lại để tham khảo hoặc gợi ý ban đầu
            'primary_color': primary_color,
            'secondary_color': template_info['secondary_color'], # Lấy từ template ban đầu
            'description': description, # Mô tả chung
            'pages': [ # Hiện tại chỉ có một trang chính, nhưng có thể mở rộng
                {
                    'name': 'Trang chủ',
                    'path': '/',
                    'components': component_specs
                }
            ],
            'user_input': user_input
        }
    
    def generate_html(self, spec):
        """Tạo mã HTML từ thông số kỹ thuật (spec) mới."""
        # Hiện tại, chỉ lấy components của trang đầu tiên
        main_page_components = spec['pages'][0]['components'] if spec['pages'] else []

        # Các item navigation sẽ được tạo từ các components có id
        nav_items_html = ""
        for comp in main_page_components:
            if comp['type'] in self.component_keywords.keys() or comp['type'] in ['about', 'contact']: # Các section có thể nav tới
                nav_label = self._get_nav_label(comp['type'])
                if nav_label:
                    nav_items_html += f"                <li><a href=\"#{comp['type']}\">{nav_label}</a></li>\n"

        html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec['site_name']}</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <header class="header">
        <nav class="navbar">
            <div class="nav-brand">
                <h1>{spec['site_name']}</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="#home">Trang chủ</a></li>
{nav_items_html.strip()}
            </ul>
            <div class="hamburger">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </nav>
    </header>

    {self._render_component(spec['primary_color'], {'type': 'hero', 'props': next((comp['props'] for comp in main_page_components if comp['type'] == 'hero'), {})})}

    {self._generate_content_sections_from_spec(spec)}

    <script src="script.js"></script>
</body>
</html>"""
        return html_template
    
    def generate_css(self, spec):
        """Tạo mã CSS từ thông số kỹ thuật"""
        # Đảm bảo primary_color được đưa vào CSS một cách chính xác
        css_template = f"""/* Reset và Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

:root {{
    --primary-color: {spec['primary_color']};
    --secondary-color: {spec['secondary_color']};
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    overflow-x: hidden;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header Styles */
.header {{
    background: var(--primary-color);
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
    transition: all 0.3s ease;
    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}}

.navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}}

.nav-brand h1 {{
    color: white;
    font-size: 1.8rem;
    font-weight: bold;
}}

.nav-menu {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-menu a {{
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
}}

.nav-menu a:hover {{
    color: #f0f0f0;
}}

.nav-menu a::after {{
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 0;
    height: 2px;
    background: white;
    transition: width 0.3s ease;
}}

.nav-menu a:hover::after {{
    width: 100%;
}}

/* Hero Section */
.hero {{
    background: linear-gradient(135deg, var(--primary-color)22, var(--primary-color)44);
    min-height: 100vh;
    display: flex;
    align-items: center;
    position: relative;
    overflow: hidden;
}}

.hero-content {{
    max-width: 600px;
    z-index: 2;
    padding: 2rem;
}}

.hero-title {{
    font-size: 3.5rem;
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 1rem;
    line-height: 1.2;
}}

.hero-description {{
    font-size: 1.3rem;
    color: #666;
    margin-bottom: 2rem;
    line-height: 1.6;
}}

.hero-buttons {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}}

.btn {{
    display: inline-block;
    padding: 12px 30px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    cursor: pointer;
    border: none;
}}

.btn-primary {{
    background: var(--primary-color);
    color: white;
}}

.btn-primary:hover {{
    background: var(--primary-color)dd;
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}}

.btn-secondary {{
    background: transparent;
    color: var(--primary-color);
    border: 2px solid var(--primary-color);
}}

.btn-secondary:hover {{
    background: var(--primary-color);
    color: white;
}}

/* Floating Animation */
.floating-shapes {{
    position: absolute;
    top: 0;
    right: 0;
    width: 50%;
    height: 100%;
    z-index: 1;
}}

.shape {{
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    animation: float 6s ease-in-out infinite;
}}

.shape-1 {{
    width: 200px;
    height: 200px;
    background: var(--primary-color);
    top: 20%;
    right: 20%;
    animation-delay: 0s;
}}

.shape-2 {{
    width: 150px;
    height: 150px;
    background: var(--primary-color);
    top: 60%;
    right: 40%;
    animation-delay: 2s;
}}

.shape-3 {{
    width: 100px;
    height: 100px;
    background: var(--primary-color);
    top: 40%;
    right: 10%;
    animation-delay: 4s;
}}

@keyframes float {{
    0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-20px) rotate(180deg); }}
}}

/* Sections */
section {{
    padding: 80px 0;
}}

.section-title {{
    text-align: center;
    font-size: 2.5rem;
    color: var(--primary-color);
    margin-bottom: 3rem;
    position: relative;
}}

.section-title::after {{
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: var(--primary-color);
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.card {{
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--primary-color);
}}

.card:hover {{
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}}

.card h3 {{
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-size: 1.3rem;
}}

.card p {{
    color: #666;
    line-height: 1.6;
}}

.card img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin-bottom: 1rem;
}}

/* Contact Section */
.contact {{
    background: #f8f9fa;
}}

.contact-content {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: start;
}}

.contact-info {{
    display: flex;
    flex-direction: column;
    gap: 2rem;
}}

.contact-item {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.contact-item i {{
    font-size: 1.5rem;
    color: var(--primary-color);
    min-width: 30px;
}}

.contact-form {{
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}

.form-group {{
    margin-bottom: 1.5rem;
}}

.form-group label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #333;
}}

.form-group input,
.form-group textarea {{
    width: 100%;
    padding: 12px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}}

.form-group input:focus,
.form-group textarea:focus {{
    outline: none;
    border-color: var(--primary-color);
}}

/* Footer */
.footer {{
    background: #333;
    color: white;
    padding: 3rem 0 1rem;
}}

.footer-content {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}}

.footer-section h3,
.footer-section h4 {{
    margin-bottom: 1rem;
    color: var(--primary-color);
}}

.footer-section ul {{
    list-style: none;
}}

.footer-section ul li {{
    margin-bottom: 0.5rem;
}}

.footer-section ul li a {{
    color: #ccc;
    text-decoration: none;
    transition: color 0.3s ease;
}}

.footer-section ul li a:hover {{
    color: white;
}}

.social-links {{
    display: flex;
    gap: 1rem;
}}

.social-links a {{
    display: inline-block;
    width: 40px;
    height: 40px;
    background: var(--primary-color);
    color: white;
    text-align: center;
    line-height: 40px;
    border-radius: 50%;
    transition: transform 0.3s ease;
}}

.social-links a:hover {{
    transform: translateY(-2px);
}}

.footer-bottom {{
    text-align: center;
    padding-top: 2rem;
    border-top: 1px solid #555;
    color: #ccc;
}}

/* Responsive Design */
.hamburger {{
    display: none;
    flex-direction: column;
    cursor: pointer;
}}

.hamburger span {{
    width: 25px;
    height: 3px;
    background: white;
    margin: 3px 0;
    transition: 0.3s;
}}

@media (max-width: 768px) {{
    .hamburger {{
        display: flex;
    }}
    
    .nav-menu {{
        position: fixed;
        left: -100%;
        top: 70px;
        flex-direction: column;
        background-color: var(--primary-color);
        width: 100%;
        text-align: center;
        transition: 0.3s;
        padding: 2rem 0;
    }}
    
    .nav-menu.active {{
        left: 0;
    }}
    
    .hero-title {{
        font-size: 2.5rem;
    }}
    
    .hero-buttons {{
        justify-content: center;
    }}
    
    .contact-content {{
        grid-template-columns: 1fr;
    }}
    
    .grid {{
        grid-template-columns: 1fr;
    }}
}}

/* Animation Classes */
.fade-in {{
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.8s ease;
}}

.fade-in.active {{
    opacity: 1;
    transform: translateY(0);
}}

/* Scroll Animation */
@keyframes slideInUp {{
    from {{
        opacity: 0;
        transform: translateY(50px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.animate-on-scroll {{
    opacity: 0;
    animation: slideInUp 0.8s ease forwards;
}}"""
        return css_template
    
    def generate_js(self, spec):
        """Tạo mã JavaScript từ thông số kỹ thuật"""
        # Sử dụng biến CSS `--primary-color` để header background khớp với chủ đề
        js_template = """// Mobile Menu Toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(n => n.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
}));

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Header Background on Scroll
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        // Lấy màu chính từ biến CSS
        const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
        header.style.background = `rgba(${parseInt(primaryColor.slice(1,3), 16)}, ${parseInt(primaryColor.slice(3,5), 16)}, ${parseInt(primaryColor.slice(5,7), 16)}, 0.95)`;
        header.style.backdropFilter = 'blur(10px)';
    } else {
        const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
        header.style.background = primaryColor;
        header.style.backdropFilter = 'none';
    }
});


// Scroll Animation
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.card, .contact-item, .hero-content, .section-title').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
});

// Form Submission
const contactForm = document.querySelector('.contact-form form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        
        // Simple validation
        if (!data.name || !data.email || !data.message) {
            alert('Vui lòng điền đầy đủ thông tin!');
            return;
        }
        
        // Simulate form submission
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Đang gửi...';
        submitBtn.disabled = true;
        
        setTimeout(() => {
            alert('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể.');
            this.reset();
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 2000);
    });
}

// Typing Effect for Hero Title
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';
    
    function typing() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(typing, speed);
        }
    }
    
    typing();
}

// Initialize typing effect when page loads
window.addEventListener('load', () => {
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const originalText = heroTitle.textContent;
        typeWriter(heroTitle, originalText, 80);
    }
});

// Parallax Effect for Hero Section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallax = document.querySelector('.hero');
    const speed = scrolled * 0.2; // Adjust speed as needed
    
    if (parallax) {
        parallax.style.transform = `translateY(${speed}px)`;
    }
});


// Add loading animation
document.addEventListener('DOMContentLoaded', function() {
    // Remove loading class if exists
    document.body.classList.remove('loading');
    
    // Add entrance animations
    setTimeout(() => {
        document.querySelectorAll('.fade-in').forEach((el, index) => {
            setTimeout(() => {
                el.classList.add('active');
            }, index * 100);
        });
    }, 300);
});

// Dynamic year in footer
const currentYear = new Date().getFullYear();
const yearElement = document.querySelector('.footer-bottom p');
if (yearElement) {
    yearElement.innerHTML = yearElement.innerHTML.replace('2024', currentYear);
}"""
        return js_template
    
    def _get_nav_label(self, component_type):
        """Helper để lấy nhãn điều hướng cho component type."""
        if component_type == 'products': return "Sản phẩm"
        if component_type == 'menu': return "Thực đơn"
        if component_type == 'services': return "Dịch vụ"
        if component_type == 'portfolio': return "Portfolio"
        if component_type == 'blog': return "Blog"
        if component_type == 'gallery': return "Thư viện"
        if component_type == 'team': return "Đội ngũ"
        if component_type == 'testimonials': return "Đánh giá"
        if component_type == 'faq': return "Hỏi đáp"
        if component_type == 'pricing': return "Bảng giá"
        if component_type == 'about': return "Giới thiệu"
        if component_type == 'contact': return "Liên hệ"
        return None

    def _render_component(self, primary_color, component_spec):
        """Render HTML cho một component cụ thể dựa trên spec."""
        comp_type = component_spec['type']
        props = component_spec['props']
        
        html = ""

        if comp_type == 'header':
            # Header được render riêng ở phần generate_html
            pass 
        elif comp_type == 'hero':
            html = f"""
    <section id="home" class="hero">
        <div class="hero-content">
            <h1 class="hero-title">{props.get('headline', 'Chào mừng!')}</h1>
            <p class="hero-description">{props.get('tagline', '')}</p>
            <div class="hero-buttons">
                <a href="#contact" class="btn btn-primary">Liên hệ ngay</a>
                <a href="#about" class="btn btn-secondary">Tìm hiểu thêm</a>
            </div>
        </div>
        <div class="hero-animation">
            <div class="floating-shapes">
                <div class="shape shape-1"></div>
                <div class="shape shape-2"></div>
                <div class="shape shape-3"></div>
            </div>
        </div>
    </section>
"""
        elif comp_type == 'about':
            html = f"""
    <section id="about" class="about">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Về chúng tôi')}</h2>
            <div class="grid">
                <div class="card fade-in">
                    <h3>Sứ mệnh của chúng tôi</h3>
                    <p>{props.get('content', 'Chúng tôi cam kết cung cấp các giải pháp web chất lượng cao, dễ sử dụng và hiệu quả, giúp doanh nghiệp và cá nhân phát triển trực tuyến.')}</p>
                </div>
                <div class="card fade-in">
                    <h3>Tầm nhìn</h3>
                    <p>Trở thành nền tảng hàng đầu trong việc chuyển đổi ý tưởng thành website một cách nhanh chóng và thông minh, loại bỏ rào cản kỹ thuật.</p>
                </div>
                <div class="card fade-in">
                    <h3>Giá trị cốt lõi</h3>
                    <p>Sáng tạo, Tận tâm, Hiệu quả, Hỗ trợ khách hàng vượt trội. Chúng tôi luôn lắng nghe và cải thiện để đáp ứng mọi nhu cầu.</p>
                </div>
            </div>
        </div>
    </section>
"""
        elif comp_type == 'products':
            items_html = ""
            for item in props.get('items', []):
                items_html += f"""
                <div class="card fade-in">
                    <img src="{item.get('image', 'https://via.placeholder.com/300x200?text=Sản+Phẩm')}" alt="{item.get('name', 'Sản phẩm')}">
                    <h3>{item.get('name', 'Sản phẩm')}</h3>
                    <p>{item.get('desc', 'Mô tả ngắn gọn về sản phẩm.')}</p>
                    <a href="#" class="btn btn-primary">Xem chi tiết</a>
                </div>
"""
            html = f"""
    <section id="products" class="products">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Sản phẩm của chúng tôi')}</h2>
            <div class="grid">
                {items_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'menu':
            items_html = ""
            for item in props.get('items', []):
                items_html += f"""
                <div class="card fade-in">
                    <img src="{item.get('image', 'https://via.placeholder.com/300x200?text=Món+Ăn')}" alt="{item.get('name', 'Món ăn')}">
                    <h3>{item.get('name', 'Món ăn')}</h3>
                    <p>{item.get('desc', 'Mô tả ngắn gọn về món ăn.')}</p>
                </div>
"""
            html = f"""
    <section id="menu" class="menu">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Thực đơn của chúng tôi')}</h2>
            <div class="grid">
                {items_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'services':
            items_html = ""
            for item in props.get('items', []):
                items_html += f"""
                <div class="card fade-in">
                    <i class="fas fa-desktop fa-3x"></i> <h3>{item.get('name', 'Dịch vụ')}</h3>
                    <p>{item.get('desc', 'Mô tả ngắn gọn về dịch vụ.')}</p>
                </div>
"""
            html = f"""
    <section id="services" class="services">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Dịch vụ của chúng tôi')}</h2>
            <div class="grid">
                {items_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'portfolio':
            items_html = ""
            for item in props.get('items', []):
                items_html += f"""
                <div class="card fade-in">
                    <img src="{item.get('image', 'https://via.placeholder.com/400x250?text=Dự+án')}" alt="{item.get('name', 'Dự án')}">
                    <h3>{item.get('name', 'Dự án')}</h3>
                    <p>{item.get('desc', 'Mô tả ngắn gọn về dự án.')}</p>
                    <a href="#" class="btn btn-secondary">Xem dự án</a>
                </div>
"""
            html = f"""
    <section id="portfolio" class="portfolio">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Dự án nổi bật của chúng tôi')}</h2>
            <div class="grid">
                {items_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'blog':
            posts_html = ""
            for post in props.get('posts', []):
                posts_html += f"""
                <div class="card fade-in">
                    <img src="{post.get('image', 'https://via.placeholder.com/400x250?text=Bài+viết')}" alt="{post.get('title', 'Bài viết')}">
                    <h3>{post.get('title', 'Tiêu đề bài viết')}</h3>
                    <p>{post.get('desc', 'Tóm tắt nội dung bài viết.')}</p>
                    <a href="#" class="btn btn-secondary">Đọc thêm</a>
                </div>
"""
            html = f"""
    <section id="blog" class="blog">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Bài viết mới nhất')}</h2>
            <div class="grid">
                {posts_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'gallery':
            images_html = ""
            for i, img_url in enumerate(props.get('images', [])):
                images_html += f"""
                <div class="gallery-item card fade-in">
                    <img src="{img_url}" alt="Gallery Image {i+1}">
                </div>
"""
            html = f"""
    <section id="gallery" class="gallery">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Thư viện ảnh của chúng tôi')}</h2>
            <div class="grid">
                {images_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'team':
            members_html = ""
            for member in props.get('members', []):
                members_html += f"""
                <div class="card fade-in">
                    <img src="{member.get('image', 'https://via.placeholder.com/150x150?text=Thành+viên')}" alt="{member.get('name', 'Thành viên')}" style="border-radius: 50%; margin-bottom: 1rem;">
                    <h3>{member.get('name', 'Tên Thành viên')}</h3>
                    <p>{member.get('role', 'Vai trò')}</p>
                    {f"<p>{member.get('bio', '')}</p>" if member.get('bio') else ""}
                </div>
"""
            html = f"""
    <section id="team" class="team">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Đội ngũ của chúng tôi')}</h2>
            <div class="grid">
                {members_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'testimonials':
            quotes_html = ""
            for quote in props.get('quotes', []):
                quotes_html += f"""
                <div class="card fade-in">
                    <p class="quote">"{quote.get('text', 'Ý kiến khách hàng.')}"</p>
                    <p class="author">- {quote.get('author', 'Khách hàng')}</p>
                </div>
"""
            html = f"""
    <section id="testimonials" class="testimonials">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Khách hàng nói gì về chúng tôi')}</h2>
            <div class="grid">
                {quotes_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'faq':
            items_html = ""
            for item in props.get('items', []):
                items_html += f"""
                <div class="card fade-in">
                    <h3>{item.get('question', 'Câu hỏi thường gặp?')}</h3>
                    <p>{item.get('answer', 'Đây là câu trả lời cho câu hỏi đó.')}</p>
                </div>
"""
            html = f"""
    <section id="faq" class="faq">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Câu hỏi thường gặp')}</h2>
            <div class="grid">
                {items_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'pricing':
            plans_html = ""
            for plan in props.get('plans', []):
                features_html = "".join([f"<li>{f}</li>" for f in plan.get('features', [])])
                plans_html += f"""
                <div class="card fade-in">
                    <h3>{plan.get('name', 'Gói')}</h3>
                    <p class="price">{plan.get('price', '$0')}</p>
                    <ul>{features_html}</ul>
                    <a href="#" class="btn btn-primary">Chọn gói</a>
                </div>
"""
            html = f"""
    <section id="pricing" class="pricing">
        <div class="container">
            <h2 class="section-title">{props.get('title', 'Bảng giá dịch vụ')}</h2>
            <div class="grid">
                {plans_html.strip()}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'contact':
            contact_form_html = self._generate_contact_form() if props.get('has_form', False) else ''
            html = f"""
    <section id="contact" class="contact">
        <div class="container">
            <h2 class="section-title">Liên hệ với chúng tôi</h2>
            <div class="contact-content">
                <div class="contact-info">
                    <div class="contact-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <div>
                            <h4>Địa chỉ</h4>
                            <p>123 Đường ABC, Quận 1, TP.HCM</p>
                        </div>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-phone"></i>
                        <div>
                            <h4>Điện thoại</h4>
                            <p>0123 456 789</p>
                        </div>
                    </div>
                    <div class="contact-item">
                        <i class="fas fa-envelope"></i>
                        <div>
                            <h4>Email</h4>
                            <p>info@{spec['site_name'].lower().replace(' ', '')}.com</p>
                        </div>
                    </div>
                </div>
                {contact_form_html}
            </div>
        </div>
    </section>
"""
        elif comp_type == 'footer':
            # Footer được render riêng ở cuối file html, không phải là section
            pass
        
        return html

    def _generate_content_sections_from_spec(self, spec):
        """Tạo các section nội dung từ spec.pages[0].components"""
        sections_html = []
        # Bỏ qua header, hero (đã render riêng) và footer (render cuối cùng)
        for component_spec in spec['pages'][0]['components']:
            if component_spec['type'] not in ['header', 'hero', 'footer']:
                sections_html.append(self._render_component(spec['primary_color'], component_spec))
        
        # Thêm footer cứng sau tất cả các section nội dung
        sections_html.append(f"""
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>{spec['site_name']}</h3>
                    <p>Cảm ơn bạn đã tin tưởng và sử dụng dịch vụ của chúng tôi.</p>
                </div>
                <div class="footer-section">
                    <h4>Liên kết nhanh</h4>
                    <ul>
                        <li><a href="#home">Trang chủ</a></li>
                        <li><a href="#about">Giới thiệu</a></li>
                        <li><a href="#contact">Liên hệ</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h4>Theo dõi chúng tôi</h4>
                    <div class="social-links">
                        <a href="#"><i class="fab fa-facebook"></i></a>
                        <a href="#"><i class="fab fa-instagram"></i></a>
                        <a href="#"><i class="fab fa-twitter"></i></a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 {spec['site_name']}. Tất cả quyền được bảo lưu.</p>
            </div>
        </div>
    </footer>
""")
        return '\n'.join(sections_html)
    
    def _generate_contact_form(self):
        """Tạo mã HTML cho form liên hệ"""
        return """
                <div class="contact-form fade-in">
                    <h3 style="color: var(--primary-color); margin-bottom: 1.5rem;">Gửi tin nhắn cho chúng tôi</h3>
                    <form>
                        <div class="form-group">
                            <label for="name">Tên của bạn</label>
                            <input type="text" id="name" name="name" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email của bạn</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="message">Tin nhắn của bạn</label>
                            <textarea id="message" name="message" rows="5" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width: 100%;">Gửi tin nhắn</button>
                    </form>
                </div>
        """

# --- Streamlit App ---
st.markdown("<h1 class='main-header'>🌐 Project Genesis - Text to Website</h1>", unsafe_allow_html=True)

st.write("""
Chào mừng bạn đến với **Project Genesis**! Nền tảng này giúp bạn tạo ra một website chuyên nghiệp chỉ từ mô tả văn bản. 
Hãy mô tả trang web bạn muốn, và AI của chúng tôi sẽ tạo ra mã nguồn HTML, CSS và JavaScript sẵn sàng để triển khai.
""")

st.markdown("---")

# Input người dùng
st.subheader("1. Mô tả trang web của bạn:")
user_input = st.text_area(
    "Ví dụ: 'Tôi muốn một trang web cửa hàng bánh ngọt có tên \"Sweet Delights\" với màu sắc chủ đạo là hồng. Trang web cần có các trang sản phẩm, giới thiệu và liên hệ. Thêm phần FAQ và một đoạn giới thiệu ngắn gọn về chúng tôi.'",
    height=150,
    placeholder="Nhập mô tả chi tiết về trang web của bạn ở đây..."
)

generator = WebsiteGenerator()

if st.button("Tạo Website"):
    if user_input:
        with st.spinner("Đang phân tích yêu cầu và tạo mã nguồn..."):
            time.sleep(2) # Simulate processing time
            spec = generator.analyze_input(user_input)
            
            html_code = generator.generate_html(spec)
            css_code = generator.generate_css(spec)
            js_code = generator.generate_js(spec)

        st.markdown("<div class='success-box'>🎉 Website của bạn đã được tạo thành công!</div>", unsafe_allow_html=True)

        st.subheader("2. Xem lại thông số kỹ thuật Website (Spec):")
        # Sử dụng st.json để hiển thị spec một cách đẹp mắt
        st.json(spec)

        st.subheader("3. Mã nguồn đã tạo:")

        # Hiển thị các tab cho HTML, CSS, JS
        tab1, tab2, tab3 = st.tabs(["HTML", "CSS", "JavaScript"])

        with tab1:
            st.code(html_code, language="html")
        with tab2:
            st.code(css_code, language="css")
        with tab3:
            st.code(js_code, language="javascript")

        st.subheader("4. Tải xuống Website của bạn:")
        st.write("Bạn có thể tải xuống toàn bộ mã nguồn website dưới dạng file ZIP.")

        # Tạo file ZIP trong bộ nhớ
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("index.html", html_code)
            zip_file.writestr("styles.css", css_code)
            zip_file.writestr("script.js", js_code)
            # Thêm placeholder images nếu cần thiết (tùy chọn)
            # Hiện tại chưa có cơ chế quản lý ảnh phức tạp, nên sẽ bỏ qua việc thêm ảnh vào ZIP

        zip_buffer.seek(0)
        st.download_button(
            label="Tải xuống Website (.zip)",
            data=zip_buffer,
            file_name=f"{spec['site_name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
        )

        st.markdown("---")
        st.info("""
        **Bước tiếp theo:** Sau khi tải xuống, bạn có thể giải nén file ZIP và mở `index.html` trong trình duyệt để xem website của mình.
        Để triển khai website lên internet, bạn có thể sử dụng các dịch vụ như Vercel, Netlify hoặc GitHub Pages.
        """)
    else:
        st.warning("Vui lòng nhập mô tả trang web của bạn để bắt đầu!")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #667eea;">
    <p>Được phát triển với niềm đam mê bởi Nhóm AI của bạn.</p>
</div>
""", unsafe_allow_html=True)
