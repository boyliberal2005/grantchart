import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Biểu đồ Timeline", layout="wide")
st.title("📊 Biểu đồ Timeline (Chữ nằm trên Bar)")

uploaded_file = st.file_uploader("Upload file Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # --- 1. XỬ LÝ FILE ---
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
            
            # Convert ngày tháng
            df['Start'] = pd.to_datetime(df['Start'], errors='coerce')
            df['End'] = pd.to_datetime(df['End'], errors='coerce')
            
            # Lọc lỗi ngày tháng
            df = df[df['Start'].dt.year > 1900]
            df = df[df['End'].dt.year > 1900]

            # Tạo nhãn hiển thị
            if 'WBS' in df.columns:
                 df['Task_Label'] = df['WBS'].astype(str) + ". " + df['Task']
            else:
                 df['Task_Label'] = df['Task']

            # Đảo ngược để task đầu tiên lên trên cùng
            df = df.iloc[::-1].reset_index(drop=True)
            
            # --- 2. VẼ BIỂU ĐỒ ---
            fig = go.Figure()
            colors = px.colors.qualitative.Plotly

            for i, row in df.iterrows():
                color_idx = i % len(colors)
                bar_color = colors[color_idx]
                
                # Tính độ dài (duration)
                duration = (row['End'] - row['Start']).days
                # Nếu duration = 0 (làm trong ngày) thì để tối thiểu là 1 ngày để hiện lên biểu đồ
                if duration == 0: duration = 1

                # 1. Vẽ Thanh Bar (Nằm dưới)
                fig.add_trace(go.Bar(
                    x=[duration], 
                    y=[i], 
                    base=[row['Start']], 
                    orientation='h', 
                    marker_color=bar_color,
                    name=row['Task_Label'],
                    hovertemplate=f"<b>{row['Task_Label']}</b><br>Start: {row['Start'].date()}<br>End: {row['End'].date()}<extra></extra>",
                    showlegend=False,
                    width=0.4 # ĐÃ SỬA: Dùng 'width' thay vì 'height' để chỉnh độ dày thanh bar
                ))

                # 2. Vẽ Tên Task (Nằm trên Bar)
                fig.add_trace(go.Scatter(
                    x=[row['Start']], 
                    y=[i + 0.35], # Đẩy chữ lên trên thanh bar
                    text=[f"<b>{row['Task_Label']}</b>"], 
                    mode="text",
                    textposition="middle right", 
                    textfont=dict(size=13, color="black"),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # --- 3. TINH CHỈNH GIAO DIỆN ---
            fig.update_layout(
                height=50 * len(df) + 150, # Chiều cao tự động
                xaxis=dict(
                    side='top', 
                    tickformat="%d-%m",
                    gridcolor='lightgrey',
                ),
                yaxis=dict(
                    showticklabels=False, # Ẩn trục Y bên trái
                    showgrid=False,
                    range=[-0.5, len(df)]
                ),
                plot_bgcolor='white',
                margin=dict(l=20, r=20, t=100, b=20),
                bargap=0.0 # Reset khoảng cách mặc định để kiểm soát thủ công tốt hơn
            )
            
            # Kẻ dòng phân cách mờ
            for i in range(len(df)):
                fig.add_shape(type="line",
                    x0=df['Start'].min(), y0=i - 0.5, x1=df['End'].max(), y1=i - 0.5,
                    line=dict(color="#eeeeee", width=1),
                    layer="below"
                )

            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Xem dữ liệu chi tiết"):
                st.dataframe(df.iloc[::-1])

    except Exception as e:
        st.error(f"Lỗi chi tiết: {e}")
