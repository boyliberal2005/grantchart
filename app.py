import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Cấu hình trang rộng để hiển thị biểu đồ đẹp hơn
st.set_page_config(page_title="Timeline Project", layout="wide")
st.title("📊 Biểu đồ Tiến độ (Style: Chữ trên - Bar dưới)")

# CSS để ẩn bớt padding thừa của Streamlit
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
</style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload file Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # --- 1. XỬ LÝ FILE THÔNG MINH ---
        # Logic: Tìm dòng chứa chữ "Task" và "Start" để làm header
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        header_row = -1
        for i, row in df_raw.iterrows():
            row_str = row.astype(str).str.lower().tolist()
            if 'task' in row_str and 'start' in row_str:
                header_row = i
                break
        
        if header_row == -1:
            st.error("Không tìm thấy dòng tiêu đề (Task, Start). Hãy kiểm tra file.")
        else:
            # Đọc lại dữ liệu từ dòng header tìm được
            if uploaded_file.name.endswith('.csv'):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, header=header_row)
            else:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, header=header_row)

            # Chuẩn hóa tên cột
            df.columns = df.columns.str.strip()
            
            # Lọc bỏ dòng trống quan trọng
            df = df.dropna(subset=['Task', 'Start', 'End'])

            # Convert ngày tháng
            df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
            df['End'] = pd.to_datetime(df['End'], errors='coerce')
            
            # Loại bỏ dữ liệu lỗi (năm 1899, 1900...)
            df = df[df['Start'].dt.year > 1900]
            df = df[df['End'].dt.year > 1900]

            # Tạo nhãn Task (WBS + Tên)
            if 'WBS' in df.columns:
                 df['Task_Label'] = df['WBS'].astype(str) + ". " + df['Task']
            else:
                 df['Task_Label'] = df['Task']

            # Đảo ngược dataframe để Task 1 nằm trên cùng khi vẽ
            df = df.iloc[::-1].reset_index(drop=True)

            # --- 2. VẼ BIỂU ĐỒ (CUSTOM LAYOUT) ---
            fig = go.Figure()

            # Tạo bảng màu
            colors = px.colors.qualitative.Set2  # Dùng bảng màu Set2 cho dịu mắt
            
            # Duyệt qua từng task để vẽ
            for i, row in df.iterrows():
                # Xác định màu (nếu có cột Lead thì theo Lead, không thì random)
                color = colors[i % len(colors)]
                
                duration = (row['End'] - row['Start']).days
                if duration <= 0: duration = 1 # Tối thiểu 1 ngày để hiển thị

                # 2.1. VẼ THANH BAR (NẰM DƯỚI)
                # Lưu ý: 'width' trong bar ngang chính là độ dày của thanh
                fig.add_trace(go.Bar(
                    y=[i],                  # Vị trí dòng thứ i
                    x=[duration],           # Chiều dài thanh
                    base=[row['Start']],    # Điểm bắt đầu
                    orientation='h',        # Nằm ngang
                    marker=dict(color=color, opacity=0.9),
                    name=row['Task_Label'],
                    width=0.3,              # ĐỘ DÀY THANH BAR (Mỏng lại để nhường chỗ cho chữ)
                    hoverinfo='text',
                    hovertext=f"<b>{row['Task_Label']}</b><br>Start: {row['Start'].strftime('%d/%m/%Y')}<br>End: {row['End'].strftime('%d/%m/%Y')}"
                ))

                # 2.2. VẼ TÊN TASK (NẰM TRÊN BAR)
                # Dùng Scatter Text để đặt chữ chính xác lên trên thanh bar
                fig.add_trace(go.Scatter(
                    x=[row['Start']],       # Chữ bắt đầu tại ngày Start
                    y=[i + 0.3],            # Đẩy chữ lên trên thanh bar (Offset trục Y)
                    text=[f"<b>{row['Task_Label']}</b>"], # In đậm tên Task
                    mode='text',
                    textposition='middle right', # Căn lề: Chữ chạy sang phải từ điểm Start
                    textfont=dict(size=14, color='#333333'), # Font chữ to, rõ
                    hoverinfo='skip'        # Không hiện popup khi rê chuột vào chữ
                ))

            # --- 3. TINH CHỈNH GIAO DIỆN (CHO GIỐNG HÌNH MẪU) ---
            fig.update_layout(
                height=60 * len(df) + 100, # Tự động chỉnh chiều cao: 60px mỗi dòng
                xaxis=dict(
                    side='top',            # Đưa ngày tháng lên trên đầu
                    tickformat="%d-%m",    # Định dạng ngày/tháng
                    gridcolor='#eeeeee',   # Màu lưới dọc nhạt
                    tickfont=dict(size=12, color='grey'),
                    zeroline=False
                ),
                yaxis=dict(
                    showticklabels=False,  # Tắt nhãn trục Y bên trái (vì tên task đã ở trên bar rồi)
                    showgrid=False,        # Tắt lưới ngang mặc định
                    range=[-0.5, len(df)], # Căn lề trên dưới
                    zeroline=False
                ),
                showlegend=False,          # Tắt chú giải
                plot_bgcolor='white',      # Nền trắng sạch
                margin=dict(l=10, r=10, t=80, b=10), # Căn lề sát biên
                hovermode="closest"
            )

            # Kẻ đường phân cách giữa các Task (Nét đứt mờ)
            # Giúp người xem phân biệt rõ từng cụm "Chữ + Bar"
            for i in range(len(df)):
                fig.add_shape(type="line",
                    x0=df['Start'].min(), 
                    y0=i - 0.5, 
                    x1=df['End'].max(), 
                    y1=i - 0.5,
                    line=dict(color="#e0e0e0", width=1, dash="dot"),
                    layer="below"
                )

            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)

            # Hiển thị bảng dữ liệu thô (đã sắp xếp lại đúng chiều đọc)
            with st.expander("Xem dữ liệu chi tiết"):
                st.dataframe(df.iloc[::-1])

    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")
        st.write("Vui lòng kiểm tra file Excel có đúng định dạng cột Task, Start, End chưa.")
