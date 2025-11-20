import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Biểu đồ Gantt Chuyên nghiệp", layout="wide")
st.title("📊 Tạo Biểu đồ Timeline (Tùy chỉnh cột)")

# --- CẤU HÌNH CSS ĐỂ GIAO DIỆN SÁT VỚI HÌNH MẪU ---
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    div[data-testid="stExpander"] details summary p {font-weight: bold; font-size: 1.1rem;}
</style>
""", unsafe_allow_html=True)

# 1. UPLOAD FILE
uploaded_file = st.file_uploader("Bước 1: Upload file Excel/CSV của bạn", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # --- 2. ĐỌC DỮ LIỆU THÔ ---
        # Đọc thử 10 dòng đầu tiên để tìm header
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file, header=None, nrows=15)
        else:
            df_preview = pd.read_excel(uploaded_file, header=None, nrows=15)

        st.info("👇 Hãy nhìn bảng dưới và chọn đúng dòng chứa tiêu đề cột (Task, Start, End)")
        
        # Cho người dùng chọn dòng Header
        header_row_idx = st.number_input(
            "Nhập số thứ tự dòng chứa tiêu đề (Header) trong bảng trên:", 
            min_value=0, 
            max_value=14, 
            value=0, 
            step=1,
            help="Nhìn vào bảng dữ liệu thô bên dưới, dòng nào chứa chữ Task, Start, End thì nhập số đó vào đây."
        )

        st.write("Dữ liệu thô (dòng 0 - 14):")
        st.dataframe(df_preview)

        # --- 3. ĐỌC LẠI FILE VỚI HEADER ĐÃ CHỌN ---
        if uploaded_file.name.endswith('.csv'):
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, header=header_row_idx)
        else:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file, header=header_row_idx)

        # --- 4. CHỌN CỘT DỮ LIỆU (QUAN TRỌNG ĐỂ KHÔNG BỊ LỖI TRỐNG) ---
        st.divider()
        st.subheader("Bước 2: Xác định cột dữ liệu")
        
        col1, col2, col3, col4 = st.columns(4)
        
        all_columns = df.columns.tolist()
        
        # Tự động gợi ý cột nếu tên giống
        default_task = next((x for x in all_columns if "task" in str(x).lower() or "việc" in str(x).lower()), all_columns[0])
        default_start = next((x for x in all_columns if "start" in str(x).lower() or "bắt đầu" in str(x).lower()), all_columns[1] if len(all_columns)>1 else all_columns[0])
        default_end = next((x for x in all_columns if "end" in str(x).lower() or "kết thúc" in str(x).lower() or "finish" in str(x).lower()), all_columns[2] if len(all_columns)>2 else all_columns[0])
        default_wbs = next((x for x in all_columns if "wbs" in str(x).lower()), "Không dùng")

        with col1:
            col_task = st.selectbox("Cột Tên công việc (Task):", all_columns, index=all_columns.index(default_task))
        with col2:
            col_start = st.selectbox("Cột Ngày bắt đầu:", all_columns, index=all_columns.index(default_start))
        with col3:
            col_end = st.selectbox("Cột Ngày kết thúc:", all_columns, index=all_columns.index(default_end))
        with col4:
            col_wbs = st.selectbox("Cột Mã WBS (Tùy chọn):", ["Không dùng"] + all_columns, index=0 if default_wbs == "Không dùng" else ["Không dùng"] + all_columns.index(default_wbs)+1)

        # --- 5. XỬ LÝ DỮ LIỆU ---
        # Đổi tên cột về chuẩn để xử lý
        df_chart = df.copy()
        df_chart = df_chart.rename(columns={col_task: 'Task', col_start: 'Start', col_end: 'End'})
        
        if col_wbs != "Không dùng":
            df_chart = df_chart.rename(columns={col_wbs: 'WBS'})

        # Convert ngày tháng
        df_chart['Start'] = pd.to_datetime(df_chart['Start'], errors='coerce')
        df_chart['End'] = pd.to_datetime(df_chart['End'], errors='coerce')
        
        # Lọc bỏ dòng không có ngày tháng
        df_clean = df_chart.dropna(subset=['Start', 'End'])
        
        # Lọc lỗi năm 1899
        df_clean = df_clean[df_clean['Start'].dt.year > 1900]
        df_clean = df_clean[df_clean['End'].dt.year > 1900]

        if df_clean.empty:
            st.error("⚠️ Không có dữ liệu hợp lệ sau khi lọc ngày tháng! Vui lòng kiểm tra lại cột Ngày bắt đầu/Kết thúc.")
        else:
            # Tạo nhãn hiển thị
            if 'WBS' in df_clean.columns:
                df_clean['Task_Label'] = df_clean['WBS'].astype(str) + ". " + df_clean['Task'].astype(str)
            else:
                df_clean['Task_Label'] = df_clean['Task'].astype(str)

            # Đảo ngược thứ tự để Task đầu tiên nằm trên cùng
            df_clean = df_clean.iloc[::-1].reset_index(drop=True)

            # --- 6. VẼ BIỂU ĐỒ (STYLE: CHỮ TRÊN - BAR DƯỚI) ---
            st.divider()
            st.subheader("Kết quả biểu đồ:")

            fig = go.Figure()
            
            # Bảng màu đẹp
            colors = px.colors.qualitative.Pastel  

            for i, row in df_clean.iterrows():
                color = colors[i % len(colors)]
                duration = (row['End'] - row['Start']).days
                if duration <= 0: duration = 1

                # 1. VẼ THANH BAR (Mỏng, nằm dưới)
                fig.add_trace(go.Bar(
                    y=[i],
                    x=[duration],
                    base=[row['Start']],
                    orientation='h',
                    marker=dict(color=color, opacity=1.0, line=dict(width=0)), # Màu đậm, không viền
                    width=0.25,  # ĐỘ DÀY THANH BAR (Rất mỏng để giống hình mẫu)
                    hoverinfo='text',
                    hovertext=f"<b>{row['Task_Label']}</b><br>{row['Start'].strftime('%d/%m')} - {row['End'].strftime('%d/%m')}",
                    showlegend=False
                ))

                # 2. VẼ CHỮ (Nằm hẳn lên trên thanh Bar)
                fig.add_trace(go.Scatter(
                    x=[row['Start']], 
                    y=[i + 0.3], # Đẩy chữ lên cao hơn thanh bar 0.3 đơn vị
                    text=[f"<b>{row['Task_Label']}</b>"],
                    mode='text',
                    textposition='middle right', # Canh lề trái (từ điểm start chạy sang phải)
                    textfont=dict(size=14, color='#2c3e50', family="Arial"), # Font đen đậm
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Cấu hình trục và khung
            fig.update_layout(
                height=60 * len(df_clean) + 100, # Chiều cao tự động
                xaxis=dict(
                    side='top', # Ngày tháng nằm trên cùng
                    tickformat="%d-%m",
                    gridcolor='#f0f0f0', # Lưới dọc rất mờ
                    tickfont=dict(size=12, color='grey'),
                    zeroline=False
                ),
                yaxis=dict(
                    showticklabels=False, # Ẩn trục trái
                    showgrid=False, 
                    range=[-0.5, len(df_clean)],
                    zeroline=False
                ),
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=80, b=20),
                bargap=0.0
            )

            # Kẻ dòng kẻ ngang mờ phân cách các task
            for i in range(len(df_clean)):
                fig.add_shape(type="line",
                    x0=df_clean['Start'].min(), y0=i - 0.4, 
                    x1=df_clean['End'].max(), y1=i - 0.4,
                    line=dict(color="#eeeeee", width=1),
                    layer="below"
                )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
        st.write("Hãy kiểm tra xem file Excel có chứa công thức bị lỗi (#REF, #NAME) không.")

else:
    st.info("Vui lòng upload file để bắt đầu.")
