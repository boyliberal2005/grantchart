import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Cấu hình trang
st.set_page_config(page_title="Ứng dụng Tạo Biểu Đồ Gantt", layout="wide")

st.title("📊 Ứng dụng Tạo Biểu Đồ Gantt từ Excel")
st.markdown("Upload file dữ liệu dự án của bạn để tạo biểu đồ tự động.")

# 1. Upload File
uploaded_file = st.file_uploader("Chọn file Excel hoặc CSV của bạn", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 2. Xử lý dữ liệu
        # Dựa vào file mẫu, dữ liệu thật thường bắt đầu sau dòng tiêu đề chung.
        # Ta sẽ thử đọc và tìm dòng chứa chữ "WBS" hoặc "Task" để làm header.
        
        if uploaded_file.name.endswith('.csv'):
            # Đọc thử file csv để tìm header
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            # Đọc thử file excel
            df_raw = pd.read_excel(uploaded_file, header=None)

        # Tìm dòng chứa header thực sự (Dòng có chứa cột 'Task' hoặc 'Start')
        header_row_index = -1
        for i, row in df_raw.iterrows():
            row_values = row.astype(str).str.lower().tolist()
            if 'task' in row_values and 'start' in row_values:
                header_row_index = i
                break
        
        if header_row_index == -1:
            st.error("Không tìm thấy tiêu đề cột (Task, Start, End) trong file. Vui lòng kiểm tra lại định dạng.")
        else:
            # Đọc lại file với header đúng
            if uploaded_file.name.endswith('.csv'):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, header=header_row_index)
            else:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, header=header_row_index)

            # 3. Làm sạch dữ liệu
            # Chuyển đổi cột ngày tháng
            # Cần đảm bảo tên cột khớp với file của bạn (Start, End, Task, Lead, % Done)
            # Xử lý tên cột có thể bị khoảng trắng
            df.columns = df.columns.str.strip()
            
            # Lọc bỏ các dòng trống quan trọng
            df = df.dropna(subset=['Task', 'Start', 'End'])

            # Convert sang datetime
            df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
            df['End'] = pd.to_datetime(df['End'], errors='coerce')
            
            # Loại bỏ các dòng convert ngày lỗi (như dòng Kick-off 1899 trong file mẫu)
            df = df[df['Start'].dt.year > 1900]
            df = df[df['End'].dt.year > 1900]

            # Tạo cột nhãn hiển thị (kết hợp WBS và Tên Task)
            if 'WBS' in df.columns:
                 df['Task_Label'] = df['WBS'].astype(str) + " - " + df['Task']
            else:
                 df['Task_Label'] = df['Task']

            # Xử lý cột % Hoàn thành để tô màu (nếu cần)
            if '% Done' in df.columns:
                df['% Done'] = pd.to_numeric(df['% Done'], errors='coerce').fillna(0)

            # 4. Vẽ Biểu Đồ (Gantt Chart)
            st.subheader("Biểu đồ tiến độ dự án (Gantt Chart)")

            # Sắp xếp để Task đầu tiên nằm trên cùng
            df = df.sort_values(by='Start', ascending=False) 

            fig = px.timeline(
                df, 
                x_start="Start", 
                x_end="End", 
                y="Task_Label",
                color="Lead" if "Lead" in df.columns else None, # Tô màu theo người phụ trách
                hover_data=["Start", "End", "% Done"] if "% Done" in df.columns else ["Start", "End"],
                title="Tiến độ dự án",
                height=800 # Chiều cao biểu đồ
            )

            # Tinh chỉnh giao diện biểu đồ cho giống hình mẫu
            fig.update_yaxes(autorange="reversed") # Đảo ngược trục Y để task 1 lên đầu
            fig.update_layout(
                xaxis_title="Thời gian",
                yaxis_title="Hạng mục công việc",
                bargap=0.2,
                xaxis=dict(
                    tickformat="%d-%m-%Y",
                    gridcolor='lightgray'
                )
            )
            
            # Hiển thị thanh % hoàn thành (Mẹo nâng cao: vẽ thêm một lớp bar chart mờ nếu cần)
            # Ở đây dùng bản timeline chuẩn của Plotly cho rõ ràng.

            st.plotly_chart(fig, use_container_width=True)

            # 5. Hiển thị dữ liệu dạng bảng bên dưới
            with st.expander("Xem dữ liệu chi tiết"):
                st.dataframe(df)

    except Exception as e:
        st.error(f"Có lỗi xảy ra khi đọc file: {e}")
        st.info("Hãy đảm bảo file của bạn có cấu trúc giống file mẫu '1.xlsx' bạn đã cung cấp.")

else:
    st.info("Vui lòng upload file để bắt đầu.")
    
    # Hiển thị hướng dẫn định dạng
    st.markdown("""
    **Yêu cầu định dạng file Excel/CSV:**
    File cần có các cột tiêu đề (ở bất kỳ dòng nào):
    - `Task` (Tên công việc)
    - `Start` (Ngày bắt đầu - định dạng yyyy-mm-dd)
    - `End` (Ngày kết thúc)
    - `Lead` (Người phụ trách - Tùy chọn, dùng để tô màu)
    - `WBS` (Mã công việc - Tùy chọn)
    """)
