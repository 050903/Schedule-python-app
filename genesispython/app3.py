#<-- DÁN TOÀN BỘ MÃ NGUỒN VÀO ĐÂY -->
import streamlit as st
import google.generativeai as genai
import os
from io import BytesIO
import zipfile
import re

# --- Cấu hình trang Streamlit ---
st.set_page_config(
    page_title="Project Genesis - AI Web Builder",
    page_icon="🔮",
    layout="wide"
)

# --- CSS tùy chỉnh cho giao diện đẹp hơn ---
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
    .stButton>button {
        background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(65, 132, 234, 0.75);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(65, 132, 234, 0.95);
    }
    .stCodeBlock {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- Hàm chức năng ---

def get_api_key():
    """Lấy API key từ sidebar hoặc st.secrets."""
    try:
        return st.secrets["google_api_key"]
    except (FileNotFoundError, KeyError):
        return st.sidebar.text_input("Nhập Google API Key của bạn:", type="password", help="Lấy API key tại Google AI Studio.")

def parse_ai_response(response_text):
    """
    Phân tích phản hồi từ AI để trích xuất các khối mã HTML, CSS, và JS.
    """
    try:
        html = re.search(r"```html(.*?)```", response_text, re.DOTALL).group(1).strip()
        css = re.search(r"```css(.*?)```", response_text, re.DOTALL).group(1).strip()
        js_match = re.search(r"```javascript(.*?)```", response_text, re.DOTALL)
        js = js_match.group(1).strip() if js_match else "" # JS có thể không có
        return html, css, js
    except AttributeError:
        st.error("AI đã không trả về phản hồi theo đúng định dạng mong muốn. Vui lòng thử lại với một yêu cầu khác.")
        return None, None, None

# --- Giao diện người dùng ---

st.markdown('<h1 class="main-header">Project Genesis 🔮</h1>', unsafe_allow_html=True)
st.subheader("Trợ lý AI giúp bạn xây dựng website từ ý tưởng", anchor=False)

st.sidebar.title("Cấu hình")
st.sidebar.markdown("Để ứng dụng hoạt động, bạn cần cung cấp API key của Google Gemini.")
api_key = get_api_key()

if not api_key:
    st.warning("Vui lòng nhập Google API Key của bạn vào thanh bên trái để bắt đầu.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Lỗi khi khởi tạo mô hình AI. Vui lòng kiểm tra lại API key. Lỗi: {e}")
    st.stop()

prompt = st.text_area(
    "Hãy mô tả chi tiết website bạn muốn tạo:",
    height=150,
    placeholder="Ví dụ: Tạo một trang portfolio cho nhiếp ảnh gia tên 'John Doe'. Trang cần có màu tối (dark mode), một hero section với ảnh nền, một gallery ảnh dạng lưới và form liên hệ đơn giản."
)

if st.button("Xây dựng Website ngay!"):
    if not prompt:
        st.warning("Vui lòng nhập mô tả cho trang web.")
    else:
        with st.spinner("🔮 AI đang phác thảo ý tưởng và viết code... Quá trình này có thể mất một vài phút..."):
            try:
                full_prompt = f"""
                Bạn là một kỹ sư lập trình frontend chuyên nghiệp. Nhiệm vụ của bạn là tạo một trang web đơn trang hoàn chỉnh (HTML, CSS, JS) dựa trên yêu cầu sau: "{prompt}".

                HƯỚNG DẪN:
                1.  Viết mã HTML5 có cấu trúc ngữ nghĩa rõ ràng, liên kết đến `style.css` và `script.js`.
                2.  Viết mã CSS để tạo giao diện đẹp, hiện đại và đáp ứng (responsive).
                3.  Viết mã JavaScript thuần để thêm các chức năng tương tác cần thiết.
                4.  Sử dụng ảnh mẫu từ `https://via.placeholder.com/` nếu cần.

                ĐỊNH DẠNG ĐẦU RA (RẤT QUAN TRỌNG):
                Trả lời bằng 3 khối mã riêng biệt cho HTML, CSS, và JavaScript.

                ```html
                <!DOCTYPE html>
                ...
                </html>
                ```

                ```css
                /* CSS code here */
                ...
                ```

                ```javascript
                // JavaScript code here
                ...
                ```
                """

                response = model.generate_content(full_prompt)
                html_code, css_code, js_code = parse_ai_response(response.text)

                if html_code and css_code:
                    st.success("🎉 AI đã hoàn thành việc xây dựng website của bạn!")

                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        zip_file.writestr("index.html", html_code)
                        zip_file.writestr("style.css", css_code)
                        zip_file.writestr("script.js", js_code)
                    
                    zip_buffer.seek(0)

                    st.download_button(
                        label="📥 Tải xuống mã nguồn (.zip)",
                        data=zip_buffer,
                        file_name="ai_generated_website.zip",
                        mime="application/zip",
                    )
                    
                    st.subheader("Xem trước mã nguồn", anchor=False)
                    with st.expander("📄 HTML (index.html)"):
                        st.code(html_code, language='html')
                    with st.expander("🎨 CSS (style.css)"):
                        st.code(css_code, language='css')
                    with st.expander("⚙️ JavaScript (script.js)"):
                        st.code(js_code, language='javascript')

            except Exception as e:
                st.error(f"Đã có lỗi xảy ra trong quá trình giao tiếp với AI: {e}")