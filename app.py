import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Biểu đồ Gantt Chuẩn", layout="wide")
st.title("📊 Biểu đồ Gantt (Giữ nguyên thứ tự Excel)")

uploaded_file = st.file_uploader("Upload file Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # --- 1. XỬ LÝ FILE (Giống bước trước nhưng kỹ hơn về header) ---
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        # Tìm dòng header
        header_row_index = -1
        for i, row in df_raw.iterrows():
            row_values = row.astype(str).str.lower().tolist()
            if 'task' in row_values and 'start' in row_values:
                header_row_index = i
                break
        
        if header_row_index == -1:
            st.error("Không tìm thấy cột Task/Start. Vui lòng kiểm tra file.")
        else:
            # Đọc lại file với header chuẩn
            if uploaded_file.name.endswith('.csv'):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, header=header_row_index)
            else:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, header=header_row_index)

            # Chuẩn hóa tên cột
            df.columns = df.columns.str.strip()
            df = df.dropna(subset=['Task', 'Start', 'End'])

            # Convert ngày tháng
            df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
            df['End'] = pd.to_datetime(df['End'], errors='coerce')
            
            # Lọc lỗi ngày tháng (năm 1899...)
            df = df[df['Start'].dt.year > 1900]
            df = df[df['End'].dt.year > 1900]

            # Tạo cột nhãn (WBS + Task)
            if 'WBS' in df.columns:
                 df['Task_Label'] = df['WBS'].astype(str) + ". " + df['Task']
            else:
                 df['Task_Label'] = df['Task']

            # --- 2. QUAN TRỌNG: GIỮ THỨ TỰ VÀ TẠO "SONG SONG" ---
            
            # Đảo ngược thứ tự DataFrame để khi vẽ lên biểu đồ
            # Task đầu tiên trong Excel sẽ nằm trên cùng (trục Y của biểu đồ vẽ từ dưới lên)
            df = df.iloc[::-1] 

            # Tính toán độ dài công việc (để hiển thị text bên cạnh nếu cần)
            df['Duration'] = (df['End'] - df['Start']).dt.days

            # --- 3. VẼ BIỂU ĐỒ ---
            fig = px.timeline(
                df, 
                x_start="Start", 
                x_end="End", 
                y="Task_Label",
                color="Lead" if "Lead" in df.columns else None,
                text="Duration", # Hiển thị số ngày trên thanh bar luôn cho dễ nhìn
                hover_data=["Start", "End"],
                height=40 * len(df) + 100 # Tự động chỉnh chiều cao biểu đồ theo số lượng task
            )

            fig.update_traces(
                texttemplate='%{text} ngày', # Hiển thị chữ "X ngày" trên thanh
                textposition='inside' # Chữ nằm trong thanh bar
            )

            # Tinh chỉnh Layout cho giống Excel
            fig.update_layout(
                title_text='Tiến độ dự án',
                xaxis_title='Thời gian',
                yaxis_title=None, # Ẩn tiêu đề trục Y cho đỡ rối
                bargap=0.3, # Khoảng cách giữa các thanh
                yaxis=dict(
                    type='category', # Bắt buộc hiển thị tất cả tên Task
                    automargin=True,
                    tickfont=dict(size=13) # Cỡ chữ tên Task
                ),
                xaxis=dict(
                    side='top', # Đưa ngày tháng lên trên cùng (giống Excel/MS Project)
                    tickformat="%d-%m",
                    gridcolor='lightgrey', # Kẻ lưới dọc
                    dtick="M1" # Hiển thị grid theo từng tháng (hoặc để auto)
                ),
                plot_bgcolor='white' # Nền trắng cho sạch
            )
            
            # Thêm đường kẻ ngang mờ để dóng hàng (giống dòng kẻ trong Excel)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Xem dữ liệu bảng"):
                # Hiển thị bảng gốc nhưng đảo lại cho đúng chiều mắt đọc
                st.dataframe(df.iloc[::-1])

    except Exception as e:
        st.error(f"Lỗi: {e}")
