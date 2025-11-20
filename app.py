import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Kế hoạch tổng quan", layout="wide")

# CSS styling
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(90deg, #1e5a9e 0%, #2b7dd4 100%);
        color: white;
        padding: 25px;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
        border-radius: 0px;
    }
    .stApp {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Kế hoạch tổng quan</div>', unsafe_allow_html=True)

# Upload file
uploaded_file = st.file_uploader("📁 Upload file Excel chứa dữ liệu dự án", type=['xlsx'])

if uploaded_file:
    # Đọc dữ liệu Excel
    df = pd.read_excel(uploaded_file, header=None)
    
    # Tìm dòng header
    header_row = None
    for i in range(len(df)):
        if df.iloc[i, 0] == 'WBS':
            header_row = i
            break
    
    if header_row is not None:
        # Đọc dữ liệu với header
        df_data = pd.read_excel(uploaded_file, header=header_row)
        df_data.columns = ['WBS', 'Task', 'Lead', 'Start', 'End', 'Cal_Days', 'Percent_Done', 'Work_Days', 'Days_Done']
        
        # Xử lý dữ liệu
        df_data['Start'] = pd.to_datetime(df_data['Start'], errors='coerce')
        df_data['End'] = pd.to_datetime(df_data['End'], errors='coerce')
        df_data = df_data.dropna(subset=['Start', 'End'])
        
        # Phân loại tasks theo category
        def classify_task(task_name, wbs, lead):
            task_lower = str(task_name).lower()
            lead_lower = str(lead).lower()
            wbs_str = str(wbs)
            
            # Phân loại dựa vào nội dung
            if any(keyword in task_lower for keyword in ['sap', 'erp', 'steercom']):
                return 'SAP'
            elif any(keyword in task_lower for keyword in ['qr code', 'sales portal', 'travel', 'expense']):
                return 'NonSAP'
            elif any(keyword in task_lower for keyword in ['ux', 'ui', 'design', 'khảo sát', 'giới thiệu']):
                return 'CM'
            elif any(keyword in task_lower for keyword in ['ifrs', 'accounting', 'dln', 'số dư', 'bctc']):
                return 'IFRS & Accounting Data Review'
            else:
                # Phân loại theo WBS
                main_wbs = wbs_str.split('.')[0] if '.' in wbs_str else wbs_str
                if main_wbs in ['1']:
                    return 'CM'
                elif main_wbs in ['2']:
                    return 'IFRS & Accounting Data Review'
                elif main_wbs in ['3', '4']:
                    return 'SAP'
                else:
                    return 'NonSAP'
        
        df_data['Category'] = df_data.apply(
            lambda row: classify_task(row['Task'], row['WBS'], row['Lead']), 
            axis=1
        )
        
        # Định nghĩa các phases theo mẫu
        min_date = df_data['Start'].min()
        max_date = df_data['End'].max()
        
        # Tạo các tháng cho timeline
        start_month = min_date.replace(day=1)
        end_month = max_date.replace(day=1)
        timeline_months = pd.date_range(start=start_month, end=end_month, freq='MS')
        
        # Định nghĩa phases với màu sắc y hệt mẫu
        phases = [
            {'name': 'Vision', 'color': '#B8D8F0', 'text_color': '#1e5a9e'},
            {'name': 'Validate', 'color': '#4FA3D1', 'text_color': 'white'},
            {'name': 'Construct', 'color': '#7B3F9B', 'text_color': 'white'},
            {'name': 'Deploy', 'color': '#5B1F70', 'text_color': 'white'},
            {'name': 'Evolve', 'color': '#FF9933', 'text_color': 'white'}
        ]
        
        # Tính thời gian cho từng phase (chia đều)
        total_duration = (max_date - min_date).days
        phase_duration = total_duration / len(phases)
        
        for i, phase in enumerate(phases):
            phase['start'] = min_date + timedelta(days=i * phase_duration)
            phase['end'] = min_date + timedelta(days=(i + 1) * phase_duration)
        
        # Màu sắc cho categories
        category_colors = {
            'SAP': '#1e5a9e',
            'NonSAP': '#8B4513', 
            'CM': '#2ca02c',
            'IFRS & Accounting Data Review': '#17becf'
        }
        
        # Tạo figure với Plotly
        fig = go.Figure()
        
        # Chiều cao và khoảng cách
        row_height = 1
        y_offset = 0
        category_y_positions = {}
        
        # Vẽ từng category
        for category in ['SAP', 'NonSAP', 'CM', 'IFRS & Accounting Data Review']:
            category_tasks = df_data[df_data['Category'] == category].copy()
            category_tasks = category_tasks.sort_values('Start')
            
            if len(category_tasks) == 0:
                continue
            
            category_y_positions[category] = y_offset
            
            for idx, row in category_tasks.iterrows():
                duration = (row['End'] - row['Start']).days
                
                # Vẽ task bar
                fig.add_trace(go.Scatter(
                    x=[row['Start'], row['End'], row['End'], row['Start'], row['Start']],
                    y=[y_offset - 0.3, y_offset - 0.3, y_offset + 0.3, y_offset + 0.3, y_offset - 0.3],
                    fill='toself',
                    fillcolor=category_colors[category],
                    line=dict(color=category_colors[category], width=1),
                    mode='lines',
                    hovertemplate=(
                        f"<b>{row['Task']}</b><br>"
                        f"Start: {row['Start'].strftime('%Y-%m-%d')}<br>"
                        f"End: {row['End'].strftime('%Y-%m-%d')}<br>"
                        f"Duration: {duration} days<br>"
                        f"Category: {category}<br>"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                    name=row['Task']
                ))
                
                # Vẽ markers ở đầu và cuối
                fig.add_trace(go.Scatter(
                    x=[row['Start'], row['End']],
                    y=[y_offset, y_offset],
                    mode='markers',
                    marker=dict(
                        color=category_colors[category],
                        size=10,
                        symbol='circle',
                        line=dict(color='white', width=2)
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                y_offset += row_height
        
        max_y = y_offset
        
        # Vẽ phase backgrounds
        phase_y_top = max_y + 3
        phase_y_bottom = -2
        
        for phase in phases:
            fig.add_shape(
                type="rect",
                x0=phase['start'],
                x1=phase['end'],
                y0=phase_y_bottom,
                y1=phase_y_top,
                fillcolor=phase['color'],
                opacity=0.15,
                layer="below",
                line_width=0,
            )
        
        # Vẽ phase labels và arrows
        phase_label_y = max_y + 1.5
        arrow_y = max_y + 2.5
        
        for i, phase in enumerate(phases):
            phase_mid = phase['start'] + (phase['end'] - phase['start']) / 2
            
            # Phase arrow
            fig.add_shape(
                type="path",
                path=f"M {phase['start'].timestamp() * 1000} {arrow_y} L {phase['end'].timestamp() * 1000} {arrow_y} L {(phase['end'] + timedelta(days=2)).timestamp() * 1000} {arrow_y} L {(phase['end'] + timedelta(days=5)).timestamp() * 1000} {arrow_y + 0.15} L {(phase['end'] + timedelta(days=2)).timestamp() * 1000} {arrow_y} L {phase['end'].timestamp() * 1000} {arrow_y}",
                fillcolor=phase['color'],
                line=dict(color=phase['color'], width=2),
                layer="above"
            )
            
            # Phase label
            fig.add_annotation(
                x=phase_mid,
                y=phase_label_y,
                text=f"<b>{phase['name']}</b>",
                showarrow=False,
                font=dict(size=14, color=phase['text_color']),
                bgcolor=phase['color'],
                borderpad=8,
                bordercolor='white',
                borderwidth=1
            )
        
        # Vẽ timeline months (T4, T5, T6...)
        month_y = max_y + 3.5
        year_labels = {}
        
        for month_date in timeline_months:
            month_mid = month_date + timedelta(days=15)
            month_label = f"T{month_date.month}"
            year = month_date.year
            
            fig.add_annotation(
                x=month_mid,
                y=month_y,
                text=month_label,
                showarrow=False,
                font=dict(size=12, color='#1e5a9e'),
                bgcolor='#E8F4F8',
                borderpad=6
            )
            
            # Thu thập năm để hiển thị
            if year not in year_labels:
                year_labels[year] = []
            year_labels[year].append(month_date)
        
        # Vẽ year labels
        year_y = max_y + 4.5
        for year, months in year_labels.items():
            year_start = months[0]
            year_end = months[-1] + timedelta(days=30)
            year_mid = year_start + (year_end - year_start) / 2
            
            fig.add_annotation(
                x=year_mid,
                y=year_y,
                text=f"<b>{year}</b>",
                showarrow=False,
                font=dict(size=16, color='#1e5a9e'),
            )
            
            # Draw year bracket
            fig.add_shape(
                type="line",
                x0=year_start, x1=year_end,
                y0=year_y - 0.3, y1=year_y - 0.3,
                line=dict(color='#1e5a9e', width=2)
            )
        
        # Thêm legend cho categories ở dưới
        legend_y_start = -1.5
        legend_x_start = min_date
        legend_spacing = (max_date - min_date).days / 4
        
        for i, (category, color) in enumerate(category_colors.items()):
            legend_x = legend_x_start + timedelta(days=i * legend_spacing)
            
            # Draw colored box
            fig.add_shape(
                type="rect",
                x0=legend_x,
                x1=legend_x + timedelta(days=10),
                y0=legend_y_start - 0.2,
                y1=legend_y_start + 0.2,
                fillcolor=color,
                line=dict(color=color, width=1)
            )
            
            # Add label
            fig.add_annotation(
                x=legend_x + timedelta(days=20),
                y=legend_y_start,
                text=category,
                showarrow=False,
                font=dict(size=11),
                xanchor='left'
            )
        
        # Thêm milestone "Go-live" nếu có
        go_live_date = df_data['End'].max()
        fig.add_shape(
            type="path",
            path=f"M {go_live_date.timestamp() * 1000} {-0.5} L {(go_live_date - timedelta(days=15)).timestamp() * 1000} {-1.5} L {(go_live_date + timedelta(days=15)).timestamp() * 1000} {-1.5} Z",
            fillcolor='#c41e1e',
            line=dict(color='#c41e1e', width=2),
            layer="above"
        )
        
        fig.add_annotation(
            x=go_live_date,
            y=-1,
            text="<b>Go-live</b>",
            showarrow=False,
            font=dict(size=12, color='white'),
            bgcolor='#c41e1e',
            borderpad=5
        )
        
        # Layout
        fig.update_layout(
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#e0e0e0',
                showline=True,
                linewidth=2,
                linecolor='#1e5a9e',
                range=[min_date - timedelta(days=15), max_date + timedelta(days=15)],
                showticklabels=False
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                range=[legend_y_start - 1, year_y + 1],
                zeroline=False
            ),
            height=900,
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest',
            showlegend=False,
            margin=dict(l=50, r=50, t=20, b=80)
        )
        
        # Hiển thị biểu đồ
        st.plotly_chart(fig, use_container_width=True)
        
        # Thêm nút download
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            # Convert figure to image
            img_bytes = fig.to_image(format="png", width=1920, height=1080, scale=2)
            st.download_button(
                label="📥 Download biểu đồ (PNG)",
                data=img_bytes,
                file_name="ke_hoach_tong_quan.png",
                mime="image/png",
                use_container_width=True
            )
        
        # Hiển thị thống kê
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tổng số Tasks", len(df_data))
        with col2:
            st.metric("Thời gian dự án", f"{(max_date - min_date).days} ngày")
        with col3:
            st.metric("Ngày bắt đầu", min_date.strftime('%d/%m/%Y'))
        with col4:
            st.metric("Ngày kết thúc", max_date.strftime('%d/%m/%Y'))
        
        # Hiển thị bảng dữ liệu
        st.markdown("---")
        st.subheader("📊 Chi tiết dữ liệu Tasks")
        
        display_df = df_data[['WBS', 'Task', 'Lead', 'Start', 'End', 'Category', 'Work_Days']].copy()
        display_df['Start'] = display_df['Start'].dt.strftime('%Y-%m-%d')
        display_df['End'] = display_df['End'].dt.strftime('%Y-%m-%d')
        display_df = display_df.rename(columns={
            'WBS': 'Mã',
            'Task': 'Công việc',
            'Lead': 'Phụ trách',
            'Start': 'Ngày bắt đầu',
            'End': 'Ngày kết thúc',
            'Category': 'Phân loại',
            'Work_Days': 'Số ngày làm việc'
        })
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
else:
    st.info("📁 Vui lòng upload file Excel để tạo biểu đồ Kế hoạch tổng quan")
    
    # Hướng dẫn
    with st.expander("📖 Hướng dẫn sử dụng"):
        st.markdown("""
        ### Cách sử dụng:
        1. Upload file Excel chứa dữ liệu dự án
        2. File Excel cần có các cột sau:
           - **WBS**: Mã công việc (1, 1.1, 2, 2.1, ...)
           - **Task**: Tên công việc
           - **Lead**: Người phụ trách
           - **Start**: Ngày bắt đầu
           - **End**: Ngày kết thúc
           - **Cal Days**: Số ngày lịch
           - **%Done**: Phần trăm hoàn thành
           - **Work Days**: Số ngày làm việc
           - **Days Done**: Số ngày đã hoàn thành
        
        3. Ứng dụng sẽ tự động:
           - Phân loại các tasks theo category (SAP, NonSAP, CM, IFRS & Accounting Data Review)
           - Tạo timeline với các giai đoạn: Vision, Validate, Construct, Deploy, Evolve
           - Hiển thị biểu đồ Gantt với màu sắc và layout chuyên nghiệp
           - Tạo milestone "Go-live"
        
        4. Sau khi tạo xong, bạn có thể:
           - Xem biểu đồ tương tác (hover để xem chi tiết)
           - Download biểu đồ dưới dạng PNG
           - Xem bảng dữ liệu chi tiết
        """)
    
    # Sample data
    with st.expander("📝 Xem dữ liệu mẫu"):
        sample_data = {
            'WBS': ['1', '1.1', '1.2', '2', '2.1'],
            'Task': [
                'Giai đoạn hợp đồng',
                'Thống nhất hợp đồng', 
                'Thống nhất timeline triển khai',
                'Khảo sát, xây dựng tài liệu giải pháp hệ thống',
                'Kick-off'
            ],
            'Lead': ['Geso & khách hàng', '', 'Geso & khách hàng', 'Geso & khách hàng', 'Geso'],
            'Start': ['2025-11-18', '2025-11-18', '2025-11-18', '2025-11-18', ''],
            'End': ['2025-11-24', '2025-11-24', '2025-11-19', '2025-12-31', ''],
            'Cal Days': [7, 7, 2, 44, 1],
            '%Done': [0, 0, 0, 0, 0],
            'Work Days': [7, 5, 2, 37, 1],
            'Days Done': [0, 0, 0, 0, 0]
        }
        st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
