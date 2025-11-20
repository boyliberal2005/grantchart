import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Biểu đồ Timeline", layout="wide")
st.title("📊 Biểu đồ Timeline (Chữ nằm trên Bar)")

uploaded_file = st.file_uploader("Upload file Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # --- 1. XỬ LÝ FILE (Giữ nguyên logic làm sạch dữ liệu) ---
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        header_row_index = -1
        for i, row in df_raw.iterrows():
            row_values = row.astype(str).str.lower().tolist()
            if 'task' in row_values and 'start' in row_values:
                header_row_index = i
                break
        
        if header_row_index == -1:
            st.error("Không tìm thấy cột Task/Start.")
        else:
            if uploaded_file.name.endswith('.csv'):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, header=header_row_index)
            else:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file, header=header_row_index)

            df.columns = df.columns.str.strip()
            df = df.dropna(subset=['Task', 'Start', 'End'])
            df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
            df['End'] = pd.to_datetime(df['End'], errors='coerce')
            df = df[df['Start'].dt.year > 1900]
            df = df[df['End'].dt.year > 1900]

            # Tạo nhãn hiển thị
            if 'WBS' in df.columns:
                 df['Task_Label'] = df['WBS'].astype(str) + ". " + df['Task']
            else:
                 df['Task_Label'] = df['Task']

            # Đảo ngược để task đầu tiên lên trên cùng
            df = df.iloc[::-1].reset_index(drop=True)
            
            # --- 2. VẼ BIỂU ĐỒ THEO YÊU CẦU MỚI ---
            # Dùng Graph Objects để tùy biến vị trí chữ tốt hơn
            fig = go.Figure()

            # Màu sắc mặc định
            colors = px.colors.qualitative.Plotly

            # Duyệt qua từng dòng để vẽ Bar và Chữ
            for i, row in df.iterrows():
                # Chọn màu (dựa theo Lead hoặc màu ngẫu nhiên)
                color_idx = i % len(colors)
                bar_color = colors[color_idx]

                # 1. Vẽ Thanh Bar (Nằm dưới)
                fig.add_trace(go.Bar(
                    x=[(row['End'] - row['Start']).days], # Độ dài
                    y=[i], # Vị trí dòng
                    base=[row['Start']], # Điểm bắt đầu
                    orientation='h', # Nằm ngang
                    marker_color=bar_color,
                    name=row['Task_Label'],
                    hovertemplate=f"<b>{row['Task_Label']}</b><br>Bắt đầu: {row['Start'].date()}<br>Kết thúc: {row['End'].date()}<extra></extra>",
                    showlegend=False,
                    height=0.4 # Độ dày của thanh bar (nhỏ lại để nhường chỗ cho chữ)
                ))

                # 2. Vẽ Tên Task (Nằm trên Bar)
                # Ta dùng Scatter dạng text đặt ngay phía trên thanh Bar
                fig.add_trace(go.Scatter(
                    x=[row['Start']], # Chữ bắt đầu ngay đầu thanh Bar
                    y=[i + 0.35], # Đẩy chữ lên trên thanh bar một chút (offset trục Y)
                    text=[f"<b>{row['Task_Label']}</b>"], # Nội dung chữ (in đậm)
                    mode="text",
                    textposition="middle right", # Căn lề
                    textfont=dict(size=13, color="black"),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # --- 3. TINH CHỈNH GIAO DIỆN ---
            fig.update_layout(
                height=60 * len(df) + 100, # Tự động chỉnh chiều cao tổng thể
                xaxis=dict(
                    side='top', # Ngày tháng nằm trên cùng
                    tickformat="%d-%m",
                    gridcolor='lightgrey',
                    title=""
                ),
                yaxis=dict(
                    showticklabels=False, # Ẩn nhãn trục Y bên trái đi (vì đã đưa chữ vào trong rồi)
                    showgrid=False,
                    range=[-1, len(df)] # Căn chỉnh khoảng cách trục Y
                ),
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=100, b=20), # Căn lề
                bargap=0.5 # Khoảng cách giữa các dòng task rộng ra để chứa chữ
            )
            
            # Thêm các đường kẻ ngang mờ để phân cách các dòng task
            for i in range(len(df)):
                fig.add_shape(type="line",
                    x0=df['Start'].min(), y0=i - 0.5, x1=df['End'].max(), y1=i - 0.5,
                    line=dict(color="lightgrey", width=1, dash="dot"),
                    layer="below"
                )

            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Xem dữ liệu chi tiết"):
                st.dataframe(df.iloc[::-1]) # Show bảng theo thứ tự xuôi

    except Exception as e:
        st.error(f"Lỗi: {e}")
