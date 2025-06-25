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
    .stApp {
        background-color: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    .stExpander {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

class WebsiteGenerator:
    def __init__(self):
        # Mở rộng templates và color_map
        self.templates = {
            'cửa hàng': {'type': 'ecommerce', 'sections': ['header', 'hero', 'products', 'about', 'contact', 'footer'], 'primary_color': '#e91e63', 'secondary_color': '#ffffff'},
            'nhà hàng': {'type': 'restaurant', 'sections': ['header', 'hero', 'menu', 'about', 'gallery', 'contact', 'footer'], 'primary_color': '#ff5722', 'secondary_color': '#ffffff'},
            'công ty': {'type': 'corporate', 'sections': ['header', 'hero', 'services', 'about', 'team', 'contact', 'footer'], 'primary_color': '#2196f3', 'secondary_color': '#ffffff'},
            'cá nhân': {'type': 'portfolio', 'sections': ['header', 'hero', 'portfolio', 'skills', 'about', 'contact', 'footer'], 'primary_color': '#9c27b0', 'secondary_color': '#ffffff'},
            'blog': {'type': 'blog', 'sections': ['header', 'hero', 'posts', 'about', 'contact', 'footer'], 'primary_color': '#795548', 'secondary_color': '#ffffff'}
        }
        
        self.color_map = {
            'đỏ': '#e53e3e', 'xanh dương': '#3182ce', 'vàng': '#d69e2e',
            'hồng': '#ed64a6', 'tím': '#805ad5', 'cam': '#dd6b20',
            'xanh lá': '#38a169', 'xanh lục': '#38a169',
            'đen': '#1a202c', 'trắng': '#ffffff', 'xám': '#718096'
        }
    
    def analyze_input(self, user_input):
        lower_input = user_input.lower()
        
        site_name = "My Awesome Website"
        name_match = re.search(r'tên là\s*["\']?([^"\']+)["\']?', user_input, re.IGNORECASE)
        if name_match:
            site_name = name_match.group(1).strip()
        
        website_type = 'corporate'
        template_info = self.templates['công ty']
        for key, template in self.templates.items():
            if key in lower_input:
                website_type = template['type']
                template_info = template
                break
        
        primary_color = template_info['primary_color']
        for color_name, color_code in self.color_map.items():
            if color_name in lower_input:
                primary_color = color_code
                break
        
        features = {
            'has_products': any(word in lower_input for word in ['sản phẩm', 'cửa hàng', 'shop']),
            'has_menu': any(word in lower_input for word in ['thực đơn', 'menu', 'món ăn']),
            'has_services': any(word in lower_input for word in ['dịch vụ']),
            'has_portfolio': any(word in lower_input for word in ['portfolio', 'dự án']),
            'has_blog': any(word in lower_input for word in ['blog', 'bài viết', 'tin tức']),
            'has_gallery': any(word in lower_input for word in ['gallery', 'thư viện ảnh', 'hình ảnh']),
            'has_team': any(word in lower_input for word in ['đội ngũ', 'nhân viên', 'team']),
            'has_about': 'giới thiệu' in lower_input,
            'has_contact_form': 'liên hệ' in lower_input,
        }
        # Đảm bảo các trang cơ bản luôn có
        features['has_about'] = True
        features['has_contact_form'] = True
        
        description_match = re.search(r'mô tả\s*:\s*(.+)', user_input, re.IGNORECASE)
        description = description_match.group(1).strip() if description_match else f"Chào mừng đến với website {website_type} của chúng tôi."
        
        return {
            'site_name': site_name,
            'website_type': website_type,
            'primary_color': primary_color,
            'secondary_color': template_info['secondary_color'],
            'sections': template_info['sections'],
            'features': features,
            'description': description,
            'user_input': user_input
        }
    
    def generate_html(self, spec):
        return f"""<!DOCTYPE html>
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
        <nav class="navbar container">
            <a href="#" class="nav-brand">{spec['site_name']}</a>
            <ul class="nav-menu">
                <li><a href="#home">Trang chủ</a></li>
                {self._generate_nav_items(spec['features'])}
            </ul>
            <div class="hamburger"><i class="fas fa-bars"></i></div>
        </nav>
    </header>

    <main>
        <section id="home" class="hero" style="background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://via.placeholder.com/1920x1080/667eea/ffffff.png?text=Hero+Image');">
            <div class="hero-content">
                <h1 class="hero-title">{spec['site_name']}</h1>
                <p class="hero-description">{spec['description']}</p>
                <a href="#contact" class="btn btn-primary">Liên hệ ngay</a>
            </div>
        </section>

        {self._generate_content_sections(spec)}

    </main>

    <footer class="footer">
        <div class="container">
            <p>© {datetime.now().year} {spec['site_name']}. All Rights Reserved.</p>
            <div class="social-links">
                <a href="#"><i class="fab fa-facebook-f"></i></a>
                <a href="#"><i class="fab fa-twitter"></i></a>
                <a href="#"><i class="fab fa-instagram"></i></a>
            </div>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>"""

    def generate_css(self, spec):
        primary_color = spec['primary_color']
        return f""":root {{
    --primary-color: {primary_color};
    --secondary-color: #f4f4f4;
    --text-color: #333;
    --light-text-color: #fff;
    --header-height: 70px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: var(--text-color); }}
.container {{ max-width: 1100px; margin: auto; overflow: hidden; padding: 0 20px; }}
section {{ padding: 60px 0; }}
.section-title {{ text-align: center; font-size: 2.5rem; margin-bottom: 40px; color: var(--primary-color); position: relative; }}
.section-title::after {{ content: ''; display: block; width: 60px; height: 3px; background: var(--primary-color); margin: 8px auto 0; }}
.header {{ background: #fff; color: var(--text-color); position: fixed; width: 100%; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); height: var(--header-height); }}
.navbar {{ display: flex; justify-content: space-between; align-items: center; height: 100%; }}
.nav-brand {{ font-size: 1.5rem; font-weight: bold; color: var(--primary-color); text-decoration: none; }}
.nav-menu {{ display: flex; list-style: none; }}
.nav-menu li a {{ color: var(--text-color); padding: 1rem; text-decoration: none; transition: color 0.3s; }}
.nav-menu li a:hover {{ color: var(--primary-color); }}
.hero {{ height: 100vh; background-size: cover; background-position: center; display: flex; justify-content: center; align-items: center; text-align: center; color: var(--light-text-color); }}
.hero-content {{ max-width: 800px; }}
.hero-title {{ font-size: 4rem; margin-bottom: 20px; }}
.hero-description {{ font-size: 1.5rem; margin-bottom: 30px; }}
.btn {{ display: inline-block; padding: 12px 25px; border-radius: 5px; text-decoration: none; transition: background-color 0.3s; }}
.btn-primary {{ background: var(--primary-color); color: var(--light-text-color); }}
.btn-primary:hover {{ background: #e91e63dd; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
.card {{ background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center; }}
.card i {{ font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem; }}
.card h3 {{ margin-bottom: 1rem; }}
.contact-form {{ max-width: 700px; margin: auto; }}
.form-group {{ margin-bottom: 1.5rem; }}
.form-group input, .form-group textarea {{ width: 100%; padding: 12px; border-radius: 5px; border: 1px solid #ddd; }}
.footer {{ background: #333; color: #fff; text-align: center; padding: 2rem 0; }}
.social-links a {{ color: #fff; margin: 0 10px; font-size: 1.2rem; }}
.hamburger {{ display: none; cursor: pointer; font-size: 1.5rem; }}
@media (max-width: 768px) {{
    .hamburger {{ display: block; }}
    .nav-menu {{ display: none; position: absolute; top: var(--header-height); left: 0; background: #fff; width: 100%; flex-direction: column; text-align: center; }}
    .nav-menu.active {{ display: flex; }}
    .nav-menu li {{ width: 100%; }}
    .nav-menu li a {{ display: block; padding: 1rem; border-bottom: 1px solid #f4f4f4; }}
    .hero-title {{ font-size: 2.5rem; }}
    .hero-description {{ font-size: 1.2rem; }}
}}
"""

    def generate_js(self, spec):
        return """
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
            }
        });
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
"""

    # --- HÀM HELPER CHO CÁC SECTION ---
    def _generate_nav_items(self, features):
        nav_items = []
        if features.get('has_about'): nav_items.append('<li><a href="#about">Giới thiệu</a></li>')
        if features.get('has_products'): nav_items.append('<li><a href="#products">Sản phẩm</a></li>')
        if features.get('has_menu'): nav_items.append('<li><a href="#menu">Thực đơn</a></li>')
        if features.get('has_services'): nav_items.append('<li><a href="#services">Dịch vụ</a></li>')
        if features.get('has_portfolio'): nav_items.append('<li><a href="#portfolio">Dự án</a></li>')
        if features.get('has_blog'): nav_items.append('<li><a href="#blog">Blog</a></li>')
        if features.get('has_gallery'): nav_items.append('<li><a href="#gallery">Thư viện</a></li>')
        if features.get('has_team'): nav_items.append('<li><a href="#team">Đội ngũ</a></li>')
        if features.get('has_contact_form'): nav_items.append('<li><a href="#contact">Liên hệ</a></li>')
        return '\n'.join(nav_items)

    def _generate_content_sections(self, spec):
        sections = []
        features = spec['features']
        if features.get('has_about'): sections.append(self._generate_about_section())
        if features.get('has_products'): sections.append(self._generate_products_section())
        if features.get('has_menu'): sections.append(self._generate_menu_section())
        if features.get('has_services'): sections.append(self._generate_services_section())
        if features.get('has_portfolio'): sections.append(self._generate_portfolio_section())
        if features.get('has_blog'): sections.append(self._generate_blog_section())
        if features.get('has_gallery'): sections.append(self._generate_gallery_section())
        if features.get('has_team'): sections.append(self._generate_team_section())
        if features.get('has_contact_form'): sections.append(self._generate_contact_section())
        return '\n\n'.join(sections)

    def _generate_about_section(self):
        return """
        <section id="about" class="container">
            <h2 class="section-title">Về Chúng Tôi</h2>
            <p style="text-align: center; max-width: 800px; margin: auto;">Chúng tôi là một đội ngũ đam mê, tận tâm mang đến những sản phẩm và dịch vụ chất lượng nhất cho khách hàng. Với nhiều năm kinh nghiệm, chúng tôi tự hào về sự chuyên nghiệp và sự hài lòng của khách hàng.</p>
        </section>"""
    
    def _generate_products_section(self):
        return """
        <section id="products" style="background-color: #f9f9f9;">
            <div class="container">
                <h2 class="section-title">Sản phẩm nổi bật</h2>
                <div class="grid">
                    <div class="card">
                        <img src="https://via.placeholder.com/300x200/cccccc/333333?text=Sản+Phẩm+1" alt="Sản phẩm 1" style="width: 100%; border-radius: 5px; margin-bottom: 1rem;">
                        <h3>Sản phẩm 1</h3>
                        <p>Mô tả ngắn gọn về sản phẩm này.</p>
                        <p style="font-weight: bold; color: var(--primary-color); margin-top: 1rem;">$19.99</p>
                    </div>
                    <div class="card">
                        <img src="https://via.placeholder.com/300x200/cccccc/333333?text=Sản+Phẩm+2" alt="Sản phẩm 2" style="width: 100%; border-radius: 5px; margin-bottom: 1rem;">
                        <h3>Sản phẩm 2</h3>
                        <p>Mô tả ngắn gọn về sản phẩm này.</p>
                        <p style="font-weight: bold; color: var(--primary-color); margin-top: 1rem;">$29.99</p>
                    </div>
                    <div class="card">
                        <img src="https://via.placeholder.com/300x200/cccccc/333333?text=Sản+Phẩm+3" alt="Sản phẩm 3" style="width: 100%; border-radius: 5px; margin-bottom: 1rem;">
                        <h3>Sản phẩm 3</h3>
                        <p>Mô tả ngắn gọn về sản phẩm này.</p>
                        <p style="font-weight: bold; color: var(--primary-color); margin-top: 1rem;">$39.99</p>
                    </div>
                </div>
            </div>
        </section>"""
        
    def _generate_services_section(self):
        return """
        <section id="services" class="container">
            <h2 class="section-title">Dịch Vụ Của Chúng Tôi</h2>
            <div class="grid">
                <div class="card">
                    <i class="fas fa-cogs"></i>
                    <h3>Dịch vụ A</h3>
                    <p>Mô tả chi tiết về dịch vụ A, mang lại lợi ích gì cho khách hàng.</p>
                </div>
                <div class="card">
                    <i class="fas fa-chart-line"></i>
                    <h3>Dịch vụ B</h3>
                    <p>Mô tả chi tiết về dịch vụ B, mang lại lợi ích gì cho khách hàng.</p>
                </div>
                <div class="card">
                    <i class="fas fa-users"></i>
                    <h3>Dịch vụ C</h3>
                    <p>Mô tả chi tiết về dịch vụ C, mang lại lợi ích gì cho khách hàng.</p>
                </div>
            </div>
        </section>"""
        
    def _generate_portfolio_section(self):
        # Tương tự như products
        return self._generate_products_section().replace('products', 'portfolio').replace('Sản phẩm', 'Dự án').replace('$', '')
        
    def _generate_blog_section(self):
        return """
        <section id="blog" style="background-color: #f9f9f9;">
            <div class="container">
                <h2 class="section-title">Tin tức & Bài viết</h2>
                <div class="grid">
                    <div class="card">
                        <img src="https://via.placeholder.com/300x200/cccccc/333333?text=Bài+Viết+1" alt="Bài viết 1" style="width: 100%; border-radius: 5px; margin-bottom: 1rem;">
                        <h3>Tiêu đề bài viết 1</h3>
                        <p>Một đoạn trích ngắn từ bài viết này để thu hút người đọc...</p>
                        <a href="#" style="margin-top: 1rem; display: inline-block;">Đọc thêm</a>
                    </div>
                    <div class="card">
                         <img src="https://via.placeholder.com/300x200/cccccc/333333?text=Bài+Viết+2" alt="Bài viết 2" style="width: 100%; border-radius: 5px; margin-bottom: 1rem;">
                        <h3>Tiêu đề bài viết 2</h3>
                        <p>Một đoạn trích ngắn từ bài viết này để thu hút người đọc...</p>
                         <a href="#" style="margin-top: 1rem; display: inline-block;">Đọc thêm</a>
                    </div>
                    <div class="card">
                         <img src="https://via.placeholder.com/300x200/cccccc/333333?text=Bài+Viết+3" alt="Bài viết 3" style="width: 100%; border-radius: 5px; margin-bottom: 1rem;">
                        <h3>Tiêu đề bài viết 3</h3>
                        <p>Một đoạn trích ngắn từ bài viết này để thu hút người đọc...</p>
                         <a href="#" style="margin-top: 1rem; display: inline-block;">Đọc thêm</a>
                    </div>
                </div>
            </div>
        </section>"""
        
    def _generate_contact_section(self):
        return """
        <section id="contact" class="container">
            <h2 class="section-title">Liên Hệ</h2>
            <div class="contact-form">
                <form>
                    <div class="form-group">
                        <input type="text" name="name" placeholder="Tên của bạn" required>
                    </div>
                    <div class="form-group">
                        <input type="email" name="email" placeholder="Email của bạn" required>
                    </div>
                    <div class="form-group">
                        <textarea name="message" placeholder="Nội dung tin nhắn" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Gửi Tin Nhắn</button>
                </form>
            </div>
        </section>"""
        
    def _generate_menu_section(self):
        return self._generate_products_section().replace('products', 'menu').replace('Sản phẩm', 'Món ăn')

    def _generate_gallery_section(self):
        return self._generate_products_section().replace('products', 'gallery').replace('Sản phẩm', 'Hình ảnh').replace('$', '')
        
    def _generate_team_section(self):
        return """
        <section id="team" class="container">
            <h2 class="section-title">Đội Ngũ Của Chúng Tôi</h2>
            <div class="grid">
                <div class="card">
                    <img src="https://via.placeholder.com/150" alt="Thành viên 1" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
                    <h3>John Doe</h3>
                    <p>CEO & Founder</p>
                </div>
                <div class="card">
                    <img src="https://via.placeholder.com/150" alt="Thành viên 2" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
                    <h3>Jane Smith</h3>
                    <p>CTO</p>
                </div>
                <div class="card">
                    <img src="https://via.placeholder.com/150" alt="Thành viên 3" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
                    <h3>Peter Jones</h3>
                    <p>Lead Designer</p>
                </div>
            </div>
        </section>"""


# --- GIAO DIỆN STREAMLIT ---

st.markdown('<p class="main-header">Project Genesis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Nền tảng Tự động "Văn bản thành Website" - Prototype</p>', unsafe_allow_html=True)

# Ví dụ mẫu
default_prompt = "Tạo một trang web cho cửa hàng bánh ngọt tên là 'Sweet Delights', màu chủ đạo là hồng. Trang web cần có phần giới thiệu, trưng bày các sản phẩm bánh, và một form liên hệ. Mô tả: chuyên các loại bánh thủ công cho mọi dịp."

user_prompt = st.text_area("Nhập mô tả về trang web bạn muốn tạo:", value=default_prompt, height=150)

if st.button("Tạo Website 🚀"):
    if not user_prompt:
        st.warning("Vui lòng nhập mô tả cho trang web của bạn.")
    else:
        generator = WebsiteGenerator()
        
        with st.spinner("Phân tích yêu cầu của bạn..."):
            time.sleep(1)
            spec = generator.analyze_input(user_prompt)
        
        st.info("✅ **Phân tích hoàn tất!** Đang tiến hành tạo mã nguồn...")
        
        with st.spinner("Đang tạo mã HTML, CSS, và JavaScript..."):
            time.sleep(2)
            html_code = generator.generate_html(spec)
            css_code = generator.generate_css(spec)
            js_code = generator.generate_js(spec)
            
            # Tạo file zip trong bộ nhớ
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr("index.html", html_code)
                zip_file.writestr("styles.css", css_code)
                zip_file.writestr("script.js", js_code)
        
        st.success("🎉 **Tuyệt vời! Website của bạn đã được tạo thành công!**")
        
        # Hiển thị và tải xuống
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Xem trước và Tải về")
            st.markdown("Bạn có thể xem mã nguồn bên dưới hoặc tải toàn bộ website dưới dạng file ZIP.")
        with col2:
            st.download_button(
                label="📥 Tải Website (.zip)",
                data=zip_buffer.getvalue(),
                file_name=f"{spec['site_name'].lower().replace(' ', '_')}_website.zip",
                mime="application/zip",
            )
        
        st.subheader("Mã nguồn đã tạo")
        with st.expander("📄 HTML (index.html)"):
            st.code(html_code, language="html")
        
        with st.expander("🎨 CSS (styles.css)"):
            st.code(css_code, language="css")
        
        with st.expander("⚙️ JavaScript (script.js)"):
            st.code(js_code, language="javascript")

st.sidebar.title("Về Project Genesis")
st.sidebar.info(
    "Đây là một ứng dụng prototype dựa trên bản thiết kế kiến trúc 'Project Genesis'. "
    "Nó mô phỏng quá trình chuyển đổi văn bản mô tả thành một trang web tĩnh hoàn chỉnh. "
    "Trong phiên bản này, logic phân tích và tạo mã được thực hiện bằng các quy tắc lập trình thay vì các mô hình AI phức tạp."
)
st.sidebar.markdown("---")
st.sidebar.header("Kiến trúc mô phỏng")
st.sidebar.markdown("""
- **Bước 1: Phân tích Yêu cầu:** Dùng Regex để trích xuất thực thể.
- **Bước 2: Tạo Thông số:** Tạo một dictionary Python làm 'thông số kỹ thuật'.
- **Bước 3: Tạo mã Nguồn:** Dùng template strings (f-strings) để tạo HTML/CSS/JS.
- **Bước 4: Đóng gói:** Nén các file đã tạo thành một file ZIP để tải về.
""")