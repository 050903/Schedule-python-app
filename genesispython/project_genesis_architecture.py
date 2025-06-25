# project_genesis_architecture.py

import json

class ProjectGenesisSimulator:
    """
    Một chương trình Python mô phỏng quy trình làm việc của nền tảng "Project Genesis".
    Chương trình này minh họa luồng dữ liệu và chuyển đổi giữa các bước
    "Văn bản thành Website" mà không cần gọi các API AI thực tế hoặc triển khai.
    """

    def __init__(self):
        # Lưu trữ kết quả của các bước trong quy trình
        self.analysis_result = None
        self.specification_json = None
        self.generated_code = None

    def analyze_requirements(self, user_prompt: str) -> dict:
        """
        Bước 1: Mô phỏng phân tích yêu cầu và làm rõ.
        Trong thực tế, một LLM sẽ phân tích lời nhắc và có thể hỏi thêm câu hỏi.
        Ở đây, chúng ta sẽ trích xuất các thực thể đơn giản.
        """
        print(f"\n--- Bước 1: Phân tích Yêu cầu và Làm rõ ---")
        print(f"Lời nhắc của người dùng: '{user_prompt}'")

        # Logic phân tích yêu cầu đơn giản (mô phỏng NLP)
        identified_entities = {
            "website_name": "Sweet Delights" if "Sweet Delights" in user_prompt else "My Website",
            "pages": [],
            "color_scheme": [],
            "features": []
        }

        if "homepage" in user_prompt:
            identified_entities["pages"].append("homepage")
        if "product page" in user_prompt:
            identified_entities["pages"].append("product page")
        if "contact page" in user_prompt:
            identified_entities["pages"].append("contact page")
        if "pink" in user_prompt:
            identified_entities["color_scheme"].append("pink")
        if "white" in user_prompt:
            identified_entities["color_scheme"].append("white")
        if "hero section" in user_prompt:
            identified_entities["features"].append("hero section")
        if "contact form" in user_prompt:
            identified_entities["features"].append("contact form")
        if "map" in user_prompt:
            identified_entities["features"].append("map")

        print(f"Đã xác định các thực thể: {identified_entities}")
        # Giả định đã làm rõ và hoàn thiện thông tin
        self.analysis_result = identified_entities
        return identified_entities

    def generate_detailed_specification(self, requirements: dict) -> dict:
        """
        Bước 2: Mô phỏng tạo thông số kỹ thuật chi tiết ở định dạng JSON.
        Trong thực tế, một LLM sẽ chuyển đổi các yêu cầu thành JSON phức tạp hơn.
        Ở đây, chúng ta xây dựng một JSON đơn giản dựa trên các yêu cầu.
        """
        print(f"\n--- Bước 2: Tạo Thông số kỹ thuật Chi tiết ---")
        print(f"Yêu cầu đầu vào: {requirements}")

        website_name = requirements.get("website_name", "My Default Website")
        primary_color = "#FFC0CB" if "pink" in requirements.get("color_scheme", []) else "#3B82F6" # Default blue
        secondary_color = "#FFFFFF" if "white" in requirements.get("color_scheme", []) else "#F9FAFB" # Default light gray

        pages_spec = []
        if "homepage" in requirements["pages"]:
            homepage_components = [
                {"type": "Header", "props": {"logoText": website_name, "navigation": []}},
                {"type": "HeroSection", "props": {"title": "Chào mừng!", "subtitle": "Trang web của bạn đã sẵn sàng."}}
            ]
            if "hero section" in requirements["features"]:
                homepage_components[1]["props"]["title"] = f"Thỏa Sức Với {website_name}"
                homepage_components[1]["props"]["subtitle"] = "Những Sản Phẩm Tuyệt Hảo"
                homepage_components[1]["props"]["ctaButton"] = {"text": "Khám phá ngay", "link": "/products"}
            pages_spec.append({
                "pageName": "Trang chủ",
                "slug": "/",
                "components": homepage_components
            })

        if "product page" in requirements["pages"]:
            pages_spec.append({
                "pageName": "Trang sản phẩm",
                "slug": "/products",
                "components": [
                    {"type": "Header", "props": {"logoText": website_name, "navigation": []}},
                    {"type": "ProductGrid", "props": {"title": "Sản phẩm của chúng tôi", "products": [{"name": "Sản phẩm 1", "price": "$10"}]}}
                ]
            })

        if "contact page" in requirements["pages"]:
            contact_components = [
                {"type": "Header", "props": {"logoText": website_name, "navigation": []}},
                {"type": "ContactForm", "props": {"title": "Liên hệ với chúng tôi", "fields": ["name", "email", "message"]}}
            ]
            if "map" in requirements["features"]:
                contact_components.append({"type": "MapSection", "props": {"address": "Địa chỉ của bạn"}})

            pages_spec.append({
                "pageName": "Trang liên hệ",
                "slug": "/contact",
                "components": contact_components
            })

        # Giả định footer luôn có
        for page in pages_spec:
            page["components"].append({"type": "Footer", "props": {"copyright": f"© 2025 {website_name}"}})

        detailed_spec = {
            "websiteName": website_name,
            "theme": {
                "primaryColor": primary_color,
                "secondaryColor": secondary_color,
                "fontFamily": "Inter, sans-serif"
            },
            "pages": pages_spec
        }

        print("Thông số kỹ thuật JSON đã tạo:")
        print(json.dumps(detailed_spec, indent=2, ensure_ascii=False))
        self.specification_json = detailed_spec
        return detailed_spec

    def generate_code(self, specification: dict) -> dict:
        """
        Bước 3: Mô phỏng tạo mã nguồn (HTML, CSS với Tailwind, React/Next.js).
        Trong thực tế, các module AI sẽ tạo ra mã đầy đủ và phức tạp.
        Ở đây, chúng ta tạo ra các đoạn mã ví dụ đơn giản.
        """
        print(f"\n--- Bước 3: Tạo mã Nguồn ---")
        print(f"Đang tạo mã dựa trên thông số kỹ thuật...")

        generated_files = {}
        website_name = specification["websiteName"]
        primary_color = specification["theme"]["primaryColor"]
        secondary_color = specification["theme"]["secondaryColor"]
        font_family = specification["theme"]["fontFamily"]

        # Giả định một cấu trúc Next.js đơn giản
        generated_files["README.md"] = f"# {website_name} - Được tạo bởi Project Genesis\n\nĐây là trang web của bạn được tạo tự động bởi Project Genesis."
        generated_files["package.json"] = """{
  "name": "my-nextjs-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-dom": "18.x"
  },
  "devDependencies": {
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0"
  }
}"""
        generated_files["tailwind.config.js"] = f"""/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  content: [
    "./pages/**/*.{{js,ts,jsx,tsx,mdx}}",
    "./components/**/*.{{js,ts,jsx,tsx,mdx}}",
    "./app/**/*.{{js,ts,jsx,tsx,mdx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: '{primary_color}',
        secondary: '{secondary_color}',
      }},
      fontFamily: {{
        sans: ['{font_family}', 'sans-serif'],
      }},
    }},
  }},
  plugins: [],
}};"""
        generated_files["globals.css"] = """@tailwind base;
@tailwind components;
@tailwind utilities;"""

        for page in specification["pages"]:
            page_name = page["pageName"].replace(" ", "_").lower()
            slug = page["slug"]
            components_jsx = []

            for component in page["components"]:
                comp_type = component["type"]
                props = component["props"]

                if comp_type == "Header":
                    nav_items = "".join([
                        f'<li key="{nav["label"]}"><a href="{nav["link"]}" class="block mt-4 lg:inline-block lg:mt-0 text-white hover:text-gray-200 mr-4 rounded-md p-2 transition duration-300 ease-in-out hover:bg-opacity-80">{nav["label"]}</a></li>'
                        for nav in props.get("navigation", [])
                    ])
                    components_jsx.append(f"""
<header class="bg-primary shadow-md p-4 rounded-b-lg">
  <nav class="container mx-auto flex items-center justify-between flex-wrap">
    <div class="flex items-center flex-shrink-0 text-white mr-6">
      <span class="font-semibold text-xl tracking-tight rounded-md p-1">{props["logoText"]}</span>
    </div>
    <div class="block lg:hidden">
      <button class="flex items-center px-3 py-2 border rounded text-white border-white hover:text-white hover:border-white">
        <svg class="fill-current h-3 w-3" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><title>Menu</title><path d="M0 3h20v2H0V3zm0 6h20v2H0V9zm0 6h20v2H0v15z"/></svg>
      </button>
    </div>
    <div class="w-full block flex-grow lg:flex lg:items-center lg:w-auto">
      <div class="text-sm lg:flex-grow">
        {nav_items}
      </div>
    </div>
  </nav>
</header>
""")
                elif comp_type == "HeroSection":
                    cta_button = ""
                    if props.get("ctaButton"):
                        cta_button = f'<a href="{props["ctaButton"]["link"]}" class="mt-8 inline-block bg-white text-primary font-bold py-3 px-8 rounded-full shadow-lg hover:bg-gray-100 transition duration-300 ease-in-out transform hover:scale-105">{props["ctaButton"]["text"]}</a>'
                    components_jsx.append(f"""
<section class="relative bg-primary text-white text-center py-20 px-4 rounded-lg shadow-xl m-4">
  <div class="absolute inset-0 bg-cover bg-center rounded-lg opacity-30" style="background-image: url('https://placehold.co/1200x600/{primary_color.replace('#', '')}/{secondary_color.replace('#', '')}?text=Banner%20Image');"></div>
  <div class="relative z-10">
    <h1 class="text-5xl font-bold mb-4 rounded-md p-2">{props["title"]}</h1>
    <p class="text-xl mb-8 rounded-md p-2">{props["subtitle"]}</p>
    {cta_button}
  </div>
</section>
""")
                elif comp_type == "AboutUsSection":
                    components_jsx.append(f"""
<section class="py-16 px-4 bg-secondary text-gray-800 rounded-lg shadow-md m-4">
  <div class="container mx-auto text-center">
    <h2 class="text-4xl font-bold mb-8 text-primary rounded-md p-2">{props["title"]}</h2>
    <div class="flex flex-col md:flex-row items-center justify-center gap-8">
      <div class="md:w-1/2">
        <img src="https://placehold.co/600x400/CCCCCC/333333?text=About%20Us%20Image" alt="About Us" class="w-full h-auto rounded-lg shadow-lg"/>
      </div>
      <div class="md:w-1/2 text-left">
        <p class="text-lg leading-relaxed rounded-md p-2">{props["description"]}</p>
      </div>
    </div>
  </div>
</section>
""")
                elif comp_type == "FeaturedProductsSection":
                    product_cards = "".join([
                        f"""
          <div class="bg-white rounded-lg shadow-md overflow-hidden transform transition-transform duration-300 hover:scale-105">
            <img src="https://placehold.co/400x300/E5E7EB/1F2937?text={product['name'].replace(' ', '%20')}" alt="{product['name']}" class="w-full h-48 object-cover"/>
            <div class="p-4">
              <h3 class="font-bold text-xl mb-2 text-primary">{product['name']}</h3>
              <p class="text-gray-700 text-base">{product['price']}</p>
            </div>
          </div>
                        """ for product in props.get("products", [])
                    ])
                    components_jsx.append(f"""
<section class="py-16 px-4 bg-white text-gray-800 rounded-lg shadow-md m-4">
  <div class="container mx-auto text-center">
    <h2 class="text-4xl font-bold mb-10 text-primary rounded-md p-2">{props["title"]}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {product_cards}
    </div>
  </div>
</section>
""")
                elif comp_type == "ProductGrid":
                    product_items = "".join([
                        f"""
          <div class="bg-white rounded-lg shadow-md overflow-hidden transform transition-transform duration-300 hover:scale-105">
            <img src="https://placehold.co/400x300/E5E7EB/1F2937?text={product['name'].replace(' ', '%20')}" alt="{product['name']}" class="w-full h-48 object-cover"/>
            <div class="p-4">
              <h3 class="font-bold text-xl mb-2 text-primary">{product['name']}</h3>
              <p class="text-gray-700 text-sm mb-4">{product.get('description', 'Mô tả sản phẩm.')}</p>
              <p class="text-gray-900 font-bold text-lg">{product['price']}</p>
            </div>
          </div>
                        """ for product in props.get("products", [])
                    ])
                    components_jsx.append(f"""
<section class="py-16 px-4 bg-white text-gray-800 rounded-lg shadow-md m-4">
  <div class="container mx-auto text-center">
    <h2 class="text-4xl font-bold mb-10 text-primary rounded-md p-2">{props["title"]}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {product_items}
    </div>
  </div>
</section>
""")
                elif comp_type == "ContactForm":
                    form_fields = "".join([
                        f"""
          <div class="mb-4">
            <label for="{field}" class="block text-gray-700 text-sm font-bold mb-2 capitalize">{field}:</label>
            <input type="{'email' if field == 'email' else 'text'}" id="{field}" name="{field}" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline-blue focus:border-blue-300 rounded-md" required>
          </div>
                        """ if field != "message" else f"""
          <div class="mb-4">
            <label for="{field}" class="block text-gray-700 text-sm font-bold mb-2 capitalize">{field}:</label>
            <textarea id="{field}" name="{field}" rows="5" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline-blue focus:border-blue-300 rounded-md" required></textarea>
          </div>
                        """ for field in props.get("fields", [])
                    ])
                    components_jsx.append(f"""
<section class="py-16 px-4 bg-secondary text-gray-800 rounded-lg shadow-md m-4">
  <div class="container mx-auto text-center max-w-md">
    <h2 class="text-4xl font-bold mb-8 text-primary rounded-md p-2">{props["title"]}</h2>
    <form class="bg-white shadow-md rounded-lg px-8 pt-6 pb-8 mb-4">
      {form_fields}
      <div class="flex items-center justify-between">
        <button type="submit" class="bg-primary hover:bg-opacity-80 text-white font-bold py-2 px-4 rounded-full focus:outline-none focus:shadow-outline transition duration-300 ease-in-out rounded-md">
          {props.get("submitButtonText", "Gửi")}
        </button>
      </div>
    </form>
  </div>
</section>

                elif comp_type == "MapSection":
                    components_jsx.append(f"""""")
<section class="py-16 px-4 bg-white text-gray-800 rounded-lg shadow-md m-4">
  <div class="container mx-auto text-center">
    <h2 class="text-4xl font-bold mb-8 text-primary rounded-md p-2">Vị trí của chúng tôi</h2>
    <p class="mb-4 text-lg">{props["address"]}</p>
    <div class="h-96 w-full bg-gray-200 rounded-lg overflow-hidden shadow-lg">
      {/* Placeholder for an embedded map, in a real app this would be Google Maps/OpenStreetMap embed */}
      <iframe
        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3153.2503932029766!2d{props.get('longitude', '0')}!3d{props.get('latitude', '0')}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMTPCsDA0JzI1LjAiTiAxMTHCsDI0JzAzLjEiRQ!5e0!3m2!1sen!2sus!4v1678912345678!5m2!1sen!2sus"
        width="100%"
        height="100%"
        style="border:0;"
        allowfullscreen=""
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"
        class="rounded-lg"
      ></iframe>
    </div>
  </div>
</section>
""")
                elif comp_type == "Footer":
                    social_links = "".join([
                        f'<a href="{link["url"]}" class="text-white hover:text-gray-200 mx-2 transition duration-300 ease-in-out rounded-md p-2">{link["platform"].capitalize()}</a>'
                        for link in props.get("socialLinks", [])
                    ])
                    components_jsx.append(f"""
<footer class="bg-primary text-white py-6 px-4 text-center rounded-t-lg shadow-md m-4">
  <div class="container mx-auto">
    <p class="mb-2 rounded-md p-2">{props["copyright"]}</p>
    <div>
      {social_links}
    </div>
  </div>
</footer>
""")

            # Tạo tệp trang Next.js
            page_content = f"""
import Head from 'next/head';

export default function {page_name.replace('_', '').capitalize()}Page() {{
  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <Head>
        <title>{page['pageName']} - {website_name}</title>
        <meta name="description" content="Trang {page['pageName']} của {website_name}" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="flex flex-col items-center justify-center py-2">
        {chr(10).join(components_jsx)}
      </main>
    </div>
  );
}}
"""
            generated_files[f"pages/{slug.replace('/', '') if slug != '/' else 'index'}.js"] = page_content

        print("Mã nguồn đã được tạo (xem chi tiết trong đối tượng `generated_code`).")
        self.generated_code = generated_files
        return generated_files

    def package_and_deploy(self, generated_code_files: dict):
        """
        Bước 4: Mô phỏng đóng gói và đề xuất triển khai.
        Trong thực tế, điều này sẽ liên quan đến các lệnh build và gọi API triển khai.
        """
        print(f"\n--- Bước 4: Đóng gói và Triển khai ---")
        print("Mô phỏng quá trình đóng gói và chuẩn bị triển khai...")

        # In ra các tệp được tạo để cho thấy những gì sẽ được đóng gói
        print("\nCác tệp đã được tạo (sẽ được đóng gói):")
        for filename in generated_code_files.keys():
            print(f"- {filename}")

        print("\nĐề xuất các tùy chọn triển khai:")
        print("- Vercel: Lý tưởng cho các ứng dụng Next.js, tích hợp Git dễ dàng.")
        print("- AWS Amplify: Giải pháp CI/CD và hosting toàn diện trên AWS.")
        print("- Các nền tảng đám mây khác (Netlify, Render, v.v.)")
        print("\nQuá trình đóng gói và triển khai thực tế sẽ được tự động hóa bằng các công cụ CI/CD.")


if __name__ == "__main__":
    # Mô phỏng đầu vào của người dùng
    user_website_description = "Tạo một trang web cửa hàng bánh ngọt có tên 'Sweet Delights', với trang chủ, trang sản phẩm và trang liên hệ. Sơ đồ màu chính nên là hồng và trắng. Trang chủ cần một phần hero với hình ảnh biểu ngữ, phần 'Về chúng tôi' và phần 'Sản phẩm nổi bật'. Trang sản phẩm nên hiển thị bánh với hình ảnh, mô tả và giá cả. Trang liên hệ nên có một biểu mẫu liên hệ và một bản đồ."

    # Khởi tạo trình mô phỏng Project Genesis
    simulator = ProjectGenesisSimulator()

    # Thực thi quy trình làm việc từng bước
    requirements = simulator.analyze_requirements(user_website_description)
    specification = simulator.generate_detailed_specification(requirements)
    code_files = simulator.generate_code(specification)
    simulator.package_and_deploy(code_files)

    print("\n\n--- Mô phỏng Project Genesis đã hoàn tất ---")
    print("Bạn có thể xem các bước và kết quả mô phỏng ở trên.")

