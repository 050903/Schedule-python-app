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
        self.templates = {
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
    
    def analyze_input(self, user_input):
        """Phân tích đầu vào của người dùng và trích xuất thông tin"""
        lower_input = user_input.lower()
        
        # Trích xuất tên website
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
        
        # Xác định loại website
        website_type = 'corporate'
        template_info = self.templates['công ty']
        
        for key, template in self.templates.items():
            if key in lower_input:
                website_type = template['type']
                template_info = template
                break
        
        # Trích xuất màu sắc
        primary_color = template_info['primary_color']
        for color_name, color_code in self.color_map.items():
            if color_name in lower_input:
                primary_color = color_code
                break
        
        # Phân tích tính năng
        features = {
            'has_products': any(word in lower_input for word in ['sản phẩm', 'bán', 'mua', 'shop']),
            'has_menu': any(word in lower_input for word in ['thực đơn', 'món ăn', 'menu', 'đồ ăn']),
            'has_services': any(word in lower_input for word in ['dịch vụ', 'phục vụ', 'service']),
            'has_portfolio': any(word in lower_input for word in ['portfolio', 'dự án', 'work', 'tác phẩm']),
            'has_blog': any(word in lower_input for word in ['blog', 'bài viết', 'tin tức', 'news']),
            'has_gallery': any(word in lower_input for word in ['gallery', 'hình ảnh', 'ảnh']),
            'has_contact_form': 'liên hệ' in lower_input or 'contact' in lower_input,
        }
        
        # Trích xuất mô tả
        description = f"Website {website_type} chuyên nghiệp với thiết kế hiện đại"
        desc_patterns = [
            r'mô tả[\s]*:?[\s]*([^\n]+)',
            r'giới thiệu[\s]*:?[\s]*([^\n]+)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                break
        
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
        """Tạo mã HTML từ thông số kỹ thuật"""
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
                {self._generate_nav_items(spec['features'])}
                <li><a href="#about">Giới thiệu</a></li>
                <li><a href="#contact">Liên hệ</a></li>
            </ul>
            <div class="hamburger">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </nav>
    </header>

    <section id="home" class="hero">
        <div class="hero-content">
            <h1 class="hero-title">Chào mừng đến với {spec['site_name']}</h1>
            <p class="hero-description">{spec['description']}</p>
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

    {self._generate_content_sections(spec)}

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
                {self._generate_contact_form() if spec['features']['has_contact_form'] else ''}
            </div>
        </div>
    </section>

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

    <script src="script.js"></script>
</body>
</html>"""
        return html_template
    
    def generate_css(self, spec):
        """Tạo mã CSS từ thông số kỹ thuật"""
        css_template = f"""/* Reset và Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
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
    background: {spec['primary_color']};
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
    background: linear-gradient(135deg, {spec['primary_color']}22, {spec['primary_color']}44);
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
    color: {spec['primary_color']};
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
    background: {spec['primary_color']};
    color: white;
}}

.btn-primary:hover {{
    background: {spec['primary_color']}dd;
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}}

.btn-secondary {{
    background: transparent;
    color: {spec['primary_color']};
    border: 2px solid {spec['primary_color']};
}}

.btn-secondary:hover {{
    background: {spec['primary_color']};
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
    background: {spec['primary_color']};
    top: 20%;
    right: 20%;
    animation-delay: 0s;
}}

.shape-2 {{
    width: 150px;
    height: 150px;
    background: {spec['primary_color']};
    top: 60%;
    right: 40%;
    animation-delay: 2s;
}}

.shape-3 {{
    width: 100px;
    height: 100px;
    background: {spec['primary_color']};
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
    color: {spec['primary_color']};
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
    background: {spec['primary_color']};
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
    background: {spec['primary_color']};
}}

.card:hover {{
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}}

.card h3 {{
    color: {spec['primary_color']};
    margin-bottom: 1rem;
    font-size: 1.3rem;
}}

.card p {{
    color: #666;
    line-height: 1.6;
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
    color: {spec['primary_color']};
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
    border-color: {spec['primary_color']};
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
    color: {spec['primary_color']};
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
    background: {spec['primary_color']};
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
        background-color: {spec['primary_color']};
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
        header.style.background = 'rgba(33, 150, 243, 0.95)';
        header.style.backdropFilter = 'blur(10px)';
    } else {
        // Fallback to the primary color from CSS or a default if not found
        // This assumes --primary-color is set in :root or body, which is not directly from spec in CSS,
        // so we'll make a slight adjustment to the JS to use the dynamic color.
        // For simplicity, we hardcode the common primary color for now,
        // but in a real app, this would be dynamically set.
        header.style.background = '""" + spec['primary_color'] + """'; 
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
document.querySelectorAll('.card, .contact-item, .hero-content').forEach(el => {
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
}
"""
        return js_template
    
    def _generate_nav_items(self, features):
        """Tạo các mục navigation dựa trên tính năng"""
        nav_items = []
        if features['has_products']:
            nav_items.append('<li><a href="#products">Sản phẩm</a></li>')
        if features['has_menu']:
            nav_items.append('<li><a href="#menu">Thực đơn</a></li>')
        if features['has_services']:
            nav_items.append('<li><a href="#services">Dịch vụ</a></li>')
        if features['has_portfolio']:
            nav_items.append('<li><a href="#portfolio">Portfolio</a></li>')
        if features['has_blog']:
            nav_items.append('<li><a href="#blog">Blog</a></li>')
        if features['has_gallery']:
            nav_items.append('<li><a href="#gallery">Thư viện</a></li>')
        
        return '\n                '.join(nav_items)
    
    def _generate_content_sections(self, spec):
        """Tạo các section nội dung dựa trên tính năng"""
        sections = []
        features = spec['features']
        
        if 'about' in spec['sections']:
            sections.append(f"""
    <section id="about" class="about">
        <div class="container">
            <h2 class="section-title">Về chúng tôi</h2>
            <div class="grid">
                <div class="card fade-in">
                    <h3>Sứ mệnh của chúng tôi</h3>
                    <p>Chúng tôi cam kết cung cấp các giải pháp website chất lượng cao, dễ sử dụng và hiệu quả, giúp doanh nghiệp và cá nhân phát triển trực tuyến.</p>
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
    </section>""")

        if features['has_products']:
            sections.append(f"""
    <section id="products" class="products">
        <div class="container">
            <h2 class="section-title">Sản phẩm của chúng tôi</h2>
            <div class="grid">
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/300x200?text=Sản+Phẩm+1" alt="Product 1">
                    <h3>Sản phẩm 1</h3>
                    <p>Mô tả ngắn gọn về sản phẩm 1. Đây là một sản phẩm tuyệt vời mà bạn sẽ yêu thích.</p>
                    <a href="#" class="btn btn-primary">Xem chi tiết</a>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/300x200?text=Sản+Phẩm+2" alt="Product 2">
                    <h3>Sản phẩm 2</h3>
                    <p>Mô tả ngắn gọn về sản phẩm 2. Sản phẩm này có nhiều tính năng độc đáo.</p>
                    <a href="#" class="btn btn-primary">Xem chi tiết</a>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/300x200?text=Sản+Phẩm+3" alt="Product 3">
                    <h3>Sản phẩm 3</h3>
                    <p>Mô tả ngắn gọn về sản phẩm 3. Đảm bảo chất lượng và giá cả phải chăng.</p>
                    <a href="#" class="btn btn-primary">Xem chi tiết</a>
                </div>
            </div>
        </div>
    </section>""")

        if features['has_menu']:
            sections.append(f"""
    <section id="menu" class="menu">
        <div class="container">
            <h2 class="section-title">Thực đơn của chúng tôi</h2>
            <div class="grid">
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/300x200?text=Món+Ăn+1" alt="Dish 1">
                    <h3>Món ăn 1</h3>
                    <p>Mô tả ngắn gọn về món ăn hấp dẫn này. Được chế biến từ nguyên liệu tươi ngon.</p>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/300x200?text=Món+Ăn+2" alt="Dish 2">
                    <h3>Món ăn 2</h3>
                    <p>Mô tả ngắn gọn về món ăn đặc biệt này. Hương vị khó quên.</p>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/300x200?text=Đồ+Uống+1" alt="Drink 1">
                    <h3>Đồ uống 1</h3>
                    <p>Thức uống giải khát, hoàn hảo cho mọi bữa ăn.</p>
                </div>
            </div>
        </div>
    </section>""")

        if features['has_services']:
            sections.append(f"""
    <section id="services" class="services">
        <div class="container">
            <h2 class="section-title">Dịch vụ của chúng tôi</h2>
            <div class="grid">
                <div class="card fade-in">
                    <i class="fas fa-desktop fa-3x"></i>
                    <h3>Thiết kế Web</h3>
                    <p>Chúng tôi cung cấp dịch vụ thiết kế web chuyên nghiệp, hiện đại và tối ưu cho mọi thiết bị.</p>
                </div>
                <div class="card fade-in">
                    <i class="fas fa-chart-line fa-3x"></i>
                    <h3>SEO & Marketing</h3>
                    <p>Giúp website của bạn đạt thứ hạng cao trên công cụ tìm kiếm và tiếp cận nhiều khách hàng hơn.</p>
                </div>
                <div class="card fade-in">
                    <i class="fas fa-headset fa-3x"></i>
                    <h3>Hỗ trợ 24/7</h3>
                    <p>Đội ngũ hỗ trợ của chúng tôi luôn sẵn sàng giải đáp mọi thắc mắc của bạn.</p>
                </div>
            </div>
        </div>
    </section>""")
        
        if features['has_portfolio']:
            sections.append(f"""
    <section id="portfolio" class="portfolio">
        <div class="container">
            <h2 class="section-title">Dự án nổi bật của chúng tôi</h2>
            <div class="grid">
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/400x250?text=Dự+án+1" alt="Project 1">
                    <h3>Dự án E-commerce</h3>
                    <p>Phát triển một nền tảng thương mại điện tử mạnh mẽ và dễ sử dụng.</p>
                    <a href="#" class="btn btn-secondary">Xem dự án</a>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/400x250?text=Dự+án+2" alt="Project 2">
                    <h3>Website Công ty</h3>
                    <p>Thiết kế lại website công ty với giao diện hiện đại và cải thiện trải nghiệm người dùng.</p>
                    <a href="#" class="btn btn-secondary">Xem dự án</a>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/400x250?text=Dự+án+3" alt="Project 3">
                    <h3>Ứng dụng Di động</h3>
                    <p>Phát triển ứng dụng di động cho cả iOS và Android, tích hợp nhiều tính năng.</p>
                    <a href="#" class="btn btn-secondary">Xem dự án</a>
                </div>
            </div>
        </div>
    </section>""")

        if features['has_blog']:
            sections.append(f"""
    <section id="blog" class="blog">
        <div class="container">
            <h2 class="section-title">Bài viết mới nhất</h2>
            <div class="grid">
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/400x250?text=Blog+Post+1" alt="Blog Post 1">
                    <h3>Xu hướng thiết kế web 2024</h3>
                    <p>Khám phá những xu hướng mới nhất định hình ngành thiết kế web năm nay.</p>
                    <a href="#" class="btn btn-secondary">Đọc thêm</a>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/400x250?text=Blog+Post+2" alt="Blog Post 2">
                    <h3>Tối ưu hóa SEO cho doanh nghiệp nhỏ</h3>
                    <p>Những mẹo và thủ thuật để cải thiện thứ hạng SEO cho website của bạn.</p>
                    <a href="#" class="btn btn-secondary">Đọc thêm</a>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/400x250?text=Blog+Post+3" alt="Blog Post 3">
                    <h3>Lợi ích của việc có một website chuyên nghiệp</h3>
                    <p>Tại sao một website chất lượng là điều cần thiết cho mọi doanh nghiệp.</p>
                    <a href="#" class="btn btn-secondary">Đọc thêm</a>
                </div>
            </div>
        </div>
    </section>""")
        
        if features['has_gallery']:
            sections.append(f"""
    <section id="gallery" class="gallery">
        <div class="container">
            <h2 class="section-title">Thư viện ảnh của chúng tôi</h2>
            <div class="grid">
                <div class="gallery-item card fade-in">
                    <img src="https://via.placeholder.com/400x300?text=Hình+ảnh+1" alt="Gallery Image 1">
                </div>
                <div class="gallery-item card fade-in">
                    <img src="https://via.placeholder.com/400x300?text=Hình+ảnh+2" alt="Gallery Image 2">
                </div>
                <div class="gallery-item card fade-in">
                    <img src="https://via.placeholder.com/400x300?text=Hình+ảnh+3" alt="Gallery Image 3">
                </div>
                <div class="gallery-item card fade-in">
                    <img src="https://via.placeholder.com/400x300?text=Hình+ảnh+4" alt="Gallery Image 4">
                </div>
            </div>
        </div>
    </section>""")

        # Add a generic team section if specified in sections, but not as a main feature
        if 'team' in spec['sections'] and not any(f for f in features.values()): # Only if no specific feature leads to content and team is requested
             sections.append(f"""
    <section id="team" class="team">
        <div class="container">
            <h2 class="section-title">Đội ngũ của chúng tôi</h2>
            <div class="grid">
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/150x150?text=Thành+viên+1" alt="Team Member 1" style="border-radius: 50%; margin-bottom: 1rem;">
                    <h3>Nguyễn Văn A</h3>
                    <p>CEO & Sáng lập</p>
                    <p>Với nhiều năm kinh nghiệm trong ngành, anh A dẫn dắt đội ngũ với tầm nhìn đột phá.</p>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/150x150?text=Thành+viên+2" alt="Team Member 2" style="border-radius: 50%; margin-bottom: 1rem;">
                    <h3>Trần Thị B</h3>
                    <p>Trưởng phòng Kỹ thuật</p>
                    <p>Chị B là bộ não phía sau các giải pháp công nghệ tiên tiến của chúng tôi.</p>
                </div>
                <div class="card fade-in">
                    <img src="https://via.placeholder.com/150x150?text=Thành+viên+3" alt="Team Member 3" style="border-radius: 50%; margin-bottom: 1rem;">
                    <h3>Lê Văn C</h3>
                    <p>Trưởng phòng Marketing</p>
                    <p>Anh C mang đến những chiến lược tiếp thị sáng tạo, giúp chúng tôi kết nối với khách hàng.</p>
                </div>
            </div>
        </div>
    </section>""")


        return '\n'.join(sections)
    
    def _generate_contact_form(self):
        """Tạo mã HTML cho form liên hệ"""
        return """
                <div class="contact-form fade-in">
                    <h3 style="color: #2196f3; margin-bottom: 1.5rem;">Gửi tin nhắn cho chúng tôi</h3>
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
    "Ví dụ: 'Tôi muốn một trang web cửa hàng bánh ngọt có tên \"Sweet Delights\" với màu sắc chủ đạo là hồng. Trang web cần có các trang sản phẩm, giới thiệu và liên hệ.'",
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

        st.subheader("2. Xem lại thông số kỹ thuật Website:")
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
            # zip_file.writestr("images/placeholder_cake_banner.jpg", requests.get("https://via.placeholder.com/1200x400?text=Banner").content)

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