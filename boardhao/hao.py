# Import các thư viện cần thiết
import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# --- DỮ LIỆU ---
# Dữ liệu được lấy trực tiếp từ "Bảng Phân bổ Ngân sách Thời gian 24 giờ"
data = {
    'Loại Ngân sách': [
        'Ngủ', 'Ăn uống & Vệ sinh', '"Khoảng thở"', 
        'Học trên trường', 'Đi lại', 'Học Lập trình', 'Làm cho Công ty'
    ],
    'Nhóm Chính': [
        'Cố định', 'Cố định', 'Linh hoạt', 
        'Có chủ đích', 'Có chủ đích', 'Có chủ đích', 'Có chủ đích'
    ],
    'Thời gian (Giờ)': [8.0, 3.5, 2.5, 2.5, 1.0, 4.0, 2.5]
}
df = pd.DataFrame(data)

# Nhóm dữ liệu theo Nhóm Chính để vẽ biểu đồ tròn
df_grouped = df.groupby('Nhóm Chính')['Thời gian (Giờ)'].sum().reset_index()

# Dữ liệu mục tiêu và thực tế cho thanh tiến trình (ví dụ)
progress_data = {
    'Học Lập trình': {'target': 9, 'actual': 8, 'color': '#3b82f6'},
    'Làm cho Công ty': {'target': 5, 'actual': 5, 'color': '#22c55e'},
    'Học trên trường': {'target': 4, 'actual': 4, 'color': '#f97316'},
    'Đi lại': {'target': 2, 'actual': 2, 'color': '#64748b'}
}

# --- KHỞI TẠO ỨNG DỤNG WEB ---
# Sử dụng một theme bên ngoài để giao diện đẹp hơn
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

# --- TẠO CÁC BIỂU ĐỒ ---

# 1. Biểu đồ tròn (Donut Chart)
donut_chart = go.Figure(data=[go.Pie(
    labels=df_grouped['Nhóm Chính'],
    values=df_grouped['Thời gian (Giờ)'],
    hole=.5, # Đây là phần tạo ra "lỗ" ở giữa, biến biểu đồ tròn thành donut
    marker_colors=['#f97316', '#64748b', '#3b82f6'], # Màu cho Cố định, Linh hoạt, Có chủ đích
    textinfo='label+percent',
    insidetextorientation='radial',
    hoverinfo='label+value+percent',
    textfont_size=14
)])
donut_chart.update_layout(
    title_text='Phân bổ Ngân sách Thời gian 24 giờ',
    title_x=0.5,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    margin=dict(t=50, b=100, l=0, r=0) # Căn chỉnh lề
)


# --- ĐỊNH NGHĨA GIAO DIỆN (LAYOUT) CỦA TRANG WEB ---

def create_progress_bar(title, data):
    """Hàm trợ giúp để tạo một thanh tiến trình."""
    percentage = (data['actual'] / data['target']) * 100
    return html.Div([
        html.Div([
            html.P(f'💻 {title}', style={'fontWeight': 'bold', 'color': data['color']}),
            html.P(f"{data['actual']} / {data['target']} khối", style={'fontWeight': 'bold'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.Div([
            html.Div(style={
                'width': f'{percentage}%',
                'backgroundColor': data['color'],
                'height': '20px',
                'borderRadius': '10px'
            })
        ], style={
            'backgroundColor': '#e0e0e0',
            'borderRadius': '10px',
            'padding': '3px'
        })
    ], style={'marginBottom': '20px'})


app.layout = html.Div([
    # Tiêu đề chính của trang web
    html.H1(
        'Bảng điều khiển Hiệu suất Tương tác',
        style={'textAlign': 'center', 'color': '#333'}
    ),

    # Container chính
    html.Div([
        # Cột bên trái chứa biểu đồ tròn
        html.Div([
            dcc.Graph(
                id='donut-chart',
                figure=donut_chart
            )
        ], className='six columns'),

        # Cột bên phải chứa các thanh tiến trình
        html.Div([
            html.H4('Theo dõi Hiệu suất Tuần', style={'textAlign': 'center'}),
            create_progress_bar('Học Lập trình', progress_data['Học Lập trình']),
            create_progress_bar('Làm cho Công ty', progress_data['Làm cho Công ty']),
            create_progress_bar('Học trên trường', progress_data['Học trên trường']),
            create_progress_bar('Đi lại', progress_data['Đi lại']),
            
        ], className='six columns', style={'paddingTop': '50px'})

    ], className='row')

], style={'maxWidth': '1000px', 'margin': 'auto', 'padding': '20px'})


# --- CHẠY SERVER ---
if __name__ == '__main__':
    # Chạy ứng dụng web trên máy của bạn
    # Mở trình duyệt và truy cập http://127.0.0.1:8050/
    app.run(debug=True)
