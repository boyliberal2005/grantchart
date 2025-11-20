import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Project Timeline", layout="wide")
st.title("📊 Biểu đồ Tiến độ Dự án (Chuẩn Form)")

# CSS tuỳ chỉnh để biểu đồ full chiều rộng và đẹp hơn
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    .stAlert {padding: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_data(uploaded_file):
    # 1. Tìm dòng Header (Task, Start, End)
    # Đọc trước 20 dòng để quét
    if uploaded_file.name.endswith('.csv'):
        df_temp = pd.read_csv(uploaded_file, header=None, nrows=20)
    else:
        df_temp = pd.read_excel(uploaded_file, header=None, nrows=20)
    
    header_idx = -1
    for i, row in df_temp.iterrows():
        # Chuyển dòng thành chuỗi chữ thường để tìm từ khóa
        row_str = row.astype(str).str.lower().tolist()
        # Điều kiện: Dòng phải chứa 'task' và ('start' hoặc 'bắt đầu')
        if 'task' in row_str and ('start' in row_str or 'bắt đầu' in row_str):
            header_idx = i
            break
            
    if header_idx == -1:
        return None, "Không tìm thấy dòng tiêu đề (Task, Start). Vui lòng kiểm tra file."

    # 2. Đọc lại file từ dòng header tìm được
    if uploaded_file.name.endswith('.csv'):
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, header=header_idx)
    else:
        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, header=header_idx)
        
    # 3. Làm sạch cột
    df.columns = df.columns.str.strip() # Xóa khoảng trắng tên cột
    
    # Mapping tên cột (Đề phòng file đổi tên chút xíu)
    col_map = {c: c for c in df.columns}
    for c in df.columns:
        cl = c.lower()
        if 'task' in cl: col_map[c] = 'Task'
        elif 'start' in cl: col_map[c] = 'Start'
        elif 'end' in cl: col_map[c] = 'End'
        elif 'wbs' in cl: col_map[c] = 'WBS'
        elif 'lead' in cl: col_map[c] = 'Lead'
    
    df = df.rename(columns=col_map)
    
    # 4. Xử lý dữ liệu ngày tháng
    # Convert sang datetime
    df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
    df['End'] = pd.to_datetime(df['End'], errors='coerce')
    
    # QUAN TRỌNG: Loại bỏ dòng lỗi (Kick-off 1899, dòng trống)
    df = df.dropna(subset=['Task', 'Start', 'End'])
    df = df[df['Start'].dt.year > 1900]
    df = df[df['End'].dt.year > 1900]
    
    # 5. Tạo nhãn hiển thị (WBS + Task)
    if 'WBS' in df.columns:
        # Ép kiểu WBS về string và xử lý null
        df['WBS'] = df['WBS'].fillna('').astype(str)
        df['Task_Label'] = df.apply(lambda x: f"{x['WBS']} - {x['Task']}" if x['WBS'] != '' else x['Task'], axis=1)
    else:
        df['Task_Label'] = df['Task']
        
    # 6. Sắp xếp lại: Đảo ngược để khi vẽ dòng 1 Excel nằm trên cùng
    df = df.iloc[::-1].reset_index(drop=True)
    
    return df, None

# --- GIAO DIỆN CHÍNH ---
uploaded_file = st.file_uploader("Kéo thả file Excel/CSV vào đây", type=['xlsx', 'csv'])

if uploaded_file is not None:
    df, error = load_data(uploaded_file)
    
    if error:
        st.error(error)
    elif df.empty:
        st.warning("File không có dữ liệu ngày tháng hợp lệ (Sau năm 1900).")
    else:
        # --- VẼ BIỂU ĐỒ (VISUALIZATION) ---
        fig = go.Figure()
        
        # Bảng màu đẹp (Set3 hoặc Pastel)
        colors = px.colors.qualitative.Set2
        
        for i, row in df.iterrows():
            # Màu sắc: Nếu có cột Lead thì dùng Lead để hash màu, không thì xoay vòng
            color = colors[i % len(colors)]
            
            duration = (row['End'] - row['Start']).days
            if duration <= 0: duration = 1 # Tối thiểu 1 ngày

            # 1. VẼ THANH BAR (NẰM DƯỚI)
            fig.add_trace(go.Bar(
                y=[i],                  # Vị trí trục Y (0, 1, 2...)
                x=[duration],           # Chiều dài
                base=[row['Start']],    # Điểm bắt đầu
                orientation='h',        # Nằm ngang
                marker=dict(
                    color=color, 
                    opacity=0.85,
                    line=dict(width=0)  # Không viền cho phẳng
                ),
                name=row['Task_Label'],
                width=0.25,             # ĐỘ DÀY THANH BAR (Mỏng để đẹp)
                hoverinfo='text',
                hovertext=f"<b>{row['Task_Label']}</b><br>📅 {row['Start'].strftime('%d/%m')} - {row['End'].strftime('%d/%m')} ({duration} ngày)",
                showlegend=False
            ))

            # 2. VẼ CHỮ (NẰM TRÊN)
            fig.add_trace(go.Scatter(
                x=[row['Start']], 
                y=[i + 0.35],           # Đẩy chữ lên cao hơn thanh Bar (Offset Y)
                text=[f"<b>{row['Task_Label']}</b>"], # Chữ đậm
                mode='text',
                textposition='middle right', # Canh lề: Bắt đầu từ điểm Start chạy sang phải
                textfont=dict(size=13, color='#262730', family="Arial"), 
                showlegend=False,
                hoverinfo='skip'
            ))

        # --- CẤU HÌNH KHUNG NHÌN (LAYOUT) ---
        fig.update_layout(
            height=50 * len(df) + 120,  # Chiều cao tự động theo số lượng task
            xaxis=dict(
                side='top',             # Ngày tháng nằm trên cùng
                tickformat="%d-%m",     # Format ngày/tháng
                gridcolor='#F0F2F6',    # Lưới dọc rất mờ
                tickfont=dict(size=12, color='grey'),
                zeroline=False,
                title=""
            ),
            yaxis=dict(
                showticklabels=False,   # Ẩn trục Y bên trái
                showgrid=False,         # Tắt lưới ngang mặc định
                range=[-0.5, len(df)],  # Căn lề trên dưới
                zeroline=False
            ),
            plot_bgcolor='white',       # Nền trắng
            margin=dict(l=10, r=10, t=80, b=10), # Căn lề
            hovermode="closest"
        )

        # Kẻ đường phân cách ngang (Dòng kẻ mờ giữa các task)
        for i in range(len(df)):
            fig.add_shape(type="line",
                x0=df['Start'].min(), y0=i - 0.4, 
                x1=df['End'].max(), y1=i - 0.4,
                line=dict(color="#E6E9EF", width=1), # Màu xám nhạt
                layer="below"
            )

        st.plotly_chart(fig, use_container_width=True)

        # Hiển thị bảng dữ liệu bên dưới (đã lọc)
        with st.expander("🔍 Xem dữ liệu gốc (Đã xử lý)"):
            st.dataframe(df.iloc[::-1][['WBS', 'Task', 'Start', 'End', 'Lead']])
