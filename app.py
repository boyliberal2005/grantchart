import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Kế hoạch tổng quan", layout="wide")

# CSS styling - giống y hệt mẫu
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
    div[data-testid="stFileUploader"] {
        background-color: #2d3748;
        padding: 30px;
        border-radius: 8px;
        color: white;
    }
    div[data-testid="stFileUploader"] label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Kế hoạch tổng quan</div>', unsafe_allow_html=True)

# Upload file
uploaded_file = st.file_uploader("📁 Upload file Excel chứa dữ liệu dự án", type=['xlsx'])

if uploaded_file:
    try:
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
            
            # Phân loại tasks theo category - Y HỆT MẪU
            def classify_task(task_name, wbs, lead):
                task_lower = str(task_name).lower()
                wbs_str = str(wbs)
                
                # Dựa vào WBS chính để phân loại chính xác
                main_wbs = wbs_str.split('.')[0] if '.' in wbs_str or ',' in wbs_str else wbs_str
                
                # CM - màu xanh lá
                if any(keyword in task_lower for keyword in ['hợp đồng', 'khảo sát', 'ux', 'ui', 'design', 'giới thiệu', 'kick', 'timeline']):
                    return 'CM'
                
                # IFRS - màu cyan  
                elif any(keyword in task_lower for keyword in ['dln', 'số dư', 'chuẩn hóa', 'cung cấp dln', 'import']):
                    return 'IFRS & Accounting Data Review'
                
                # SAP - màu xanh dương
                elif any(keyword in task_lower for keyword in ['phát triển', 'lập trình', 'uat', 'đào tạo', 'pilot', 'vận hành']):
                    return 'SAP'
                
                # NonSAP - màu nâu
                elif any(keyword in task_lower for keyword in ['xây dựng dln', 'kiểm tra']):
                    return 'NonSAP'
                
                # Phân loại dự phòng theo WBS
                else:
                    if main_wbs in ['1', '2']:
                        return 'CM'
                    elif main_wbs in ['3']:
                        return 'SAP'
                    elif main_wbs in ['4']:
                        return 'NonSAP'
                    else:
                        return 'IFRS & Accounting Data Review'
            
            df_data['Category'] = df_data.apply(
                lambda row: classify_task(row['Task'], row['WBS'], row['Lead']), 
                axis=1
            )
            
            # Định nghĩa màu sắc Y HỆT MẪU
            category_colors = {
                'SAP': '#17becf',           # Cyan - giống mẫu
                'NonSAP': '#8B4513',        # Nâu - giống mẫu
                'CM': '#2ca02c',            # Xanh lá - giống mẫu
                'IFRS & Accounting Data Review': '#17becf'  # Cyan - giống mẫu
            }
            
            min_date = df_data['Start'].min()
            max_date = df_data['End'].max()
            
            # Tạo các tháng cho timeline
            start_month = min_date.replace(day=1)
            end_month = max_date.replace(day=1)
            timeline_months = pd.date_range(start=start_month, end=end_month, freq='MS')
            
            # Định nghĩa phases với màu sắc Y HỆT MẪU
            phases = [
                {'name': 'Vision', 'color': '#B8D8F0'},
                {'name': 'Validate', 'color': '#5DADE2'},
                {'name': 'Construct', 'color': '#8E44AD'},
                {'name': 'Deploy', 'color': '#6C3483'},
                {'name': 'Evolve', 'color': '#FF9933'}
            ]
            
            # Tính thời gian cho từng phase
            total_duration = (max_date - min_date).days
            phase_duration = total_duration / len(phases)
            
            for i, phase in enumerate(phases):
                phase['start'] = min_date + timedelta(days=i * phase_duration)
                phase['end'] = min_date + timedelta(days=(i + 1) * phase_duration)
            
            # Tạo figure
            fig = go.Figure()
            
            # Chiều cao và spacing
            row_height = 0.8
            y_offset = 0
            
            # Sắp xếp theo category và WBS
            category_order = ['CM', 'IFRS & Accounting Data Review', 'SAP', 'NonSAP']
            
            # Vẽ từng category
            for category in category_order:
                category_tasks = df_data[df_data['Category'] == category].copy()
                category_tasks = category_tasks.sort_values('Start')
                
                if len(category_tasks) == 0:
                    continue
                
                for idx, row in category_tasks.iterrows():
                    duration = (row['End'] - row['Start']).days
                    
                    # Vẽ task bar với rounded corners
                    fig.add_trace(go.Scatter(
                        x=[row['Start'], row['End']],
                        y=[y_offset, y_offset],
                        mode='lines',
                        line=dict(
                            color=category_colors[category],
                            width=20  # Dày hơn để giống mẫu
                        ),
                        hovertemplate=(
                            f"<b>{row['Task']}</b><br>"
                            f"Bắt đầu: {row['Start'].strftime('%d/%m/%Y')}<br>"
                            f"Kết thúc: {row['End'].strftime('%d/%m/%Y')}<br>"
                            f"Thời gian: {duration} ngày<br>"
                            f"Phân loại: {category}<br>"
                            "<extra></extra>"
                        ),
                        showlegend=False,
                        name=row['Task']
                    ))
                    
                    # Vẽ circles ở đầu và cuối - GIỐNG Y MẪU
                    fig.add_trace(go.Scatter(
                        x=[row['Start'], row['End']],
                        y=[y_offset, y_offset],
                        mode='markers',
                        marker=dict(
                            color=category_colors[category],
                            size=12,
                            symbol='circle',
                            line=dict(color='white', width=2)
                        ),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    y_offset += row_height
            
            max_y = y_offset
            
            # Vẽ phase backgrounds
            phase_y_top = max_y + 2
            phase_y_bottom = -1.5
            
            for phase in phases:
                fig.add_shape(
                    type="rect",
                    x0=phase['start'],
                    x1=phase['end'],
                    y0=phase_y_bottom,
                    y1=phase_y_top,
                    fillcolor=phase['color'],
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                )
            
            # Vẽ phase labels - Y HỆT MẪU
            phase_label_y = max_y + 0.8
            
            for phase in phases:
                phase_mid = phase['start'] + (phase['end'] - phase['start']) / 2
                
                fig.add_annotation(
                    x=phase_mid,
                    y=phase_label_y,
                    text=f"<b>{phase['name']}</b>",
                    showarrow=False,
                    font=dict(size=16, color='white'),
                    bgcolor=phase['color'],
                    borderpad=10,
                    bordercolor=phase['color'],
                    borderwidth=0
                )
            
            # Vẽ timeline months (T11, T12, T1, T2...) - Y HỆT MẪU
            month_y = max_y + 1.8
            year_y = max_y + 2.2
            
            # Vẽ các tháng
            year_2025_start = None
            year_2025_end = None
            year_2026_start = None
            year_2026_end = None
            
            for i, month_date in enumerate(timeline_months):
                month_mid = month_date + timedelta(days=15)
                month_label = f"T{month_date.month}"
                
                fig.add_annotation(
                    x=month_mid,
                    y=month_y,
                    text=month_label,
                    showarrow=False,
                    font=dict(size=13, color='#1e5a9e'),
                )
                
                # Lưu vị trí năm
                if month_date.year == 2025:
                    if year_2025_start is None:
                        year_2025_start = month_date
                    year_2025_end = month_date + timedelta(days=30)
                elif month_date.year == 2026:
                    if year_2026_start is None:
                        year_2026_start = month_date
                    year_2026_end = month_date + timedelta(days=30)
            
            # Vẽ năm 2025
            if year_2025_start and year_2025_end:
                year_2025_mid = year_2025_start + (year_2025_end - year_2025_start) / 2
                
                # Arrow line
                fig.add_shape(
                    type="line",
                    x0=year_2025_start, x1=year_2025_end,
                    y0=year_y, y1=year_y,
                    line=dict(color='#1e5a9e', width=3)
                )
                
                # Arrows
                fig.add_annotation(
                    x=year_2025_start,
                    y=year_y,
                    ax=-20, ay=0,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=4,
                    arrowsize=1.5,
                    arrowwidth=3,
                    arrowcolor='#1e5a9e'
                )
                
                fig.add_annotation(
                    x=year_2025_end,
                    y=year_y,
                    ax=20, ay=0,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=4,
                    arrowsize=1.5,
                    arrowwidth=3,
                    arrowcolor='#1e5a9e'
                )
                
                fig.add_annotation(
                    x=year_2025_mid,
                    y=year_y + 0.15,
                    text="<b>2025</b>",
                    showarrow=False,
                    font=dict(size=18, color='#1e5a9e'),
                )
            
            # Vẽ năm 2026
            if year_2026_start and year_2026_end:
                year_2026_mid = year_2026_start + (year_2026_end - year_2026_start) / 2
                
                fig.add_shape(
                    type="line",
                    x0=year_2026_start, x1=year_2026_end,
                    y0=year_y, y1=year_y,
                    line=dict(color='#1e5a9e', width=3)
                )
                
                fig.add_annotation(
                    x=year_2026_start,
                    y=year_y,
                    ax=-20, ay=0,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=4,
                    arrowsize=1.5,
                    arrowwidth=3,
                    arrowcolor='#1e5a9e'
                )
                
                fig.add_annotation(
                    x=year_2026_end,
                    y=year_y,
                    ax=20, ay=0,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    showarrow=True,
                    arrowhead=4,
                    arrowsize=1.5,
                    arrowwidth=3,
                    arrowcolor='#1e5a9e'
                )
                
                fig.add_annotation(
                    x=year_2026_mid,
                    y=year_y + 0.15,
                    text="<b>2026</b>",
                    showarrow=False,
                    font=dict(size=18, color='#1e5a9e'),
                )
            
            # Thêm legend ở dưới - Y HỆT MẪU
            legend_y = -0.8
            legend_items = [
                ('SAP', '#1e5a9e'),
                ('NonSAP', '#8B4513'),
                ('CM', '#2ca02c'),
                ('IFRS & Accounting Data Review', '#17becf')
            ]
            
            legend_spacing = (max_date - min_date).days / len(legend_items)
            
            for i, (name, color) in enumerate(legend_items):
                legend_x = min_date + timedelta(days=(i + 0.3) * legend_spacing)
                
                # Colored box
                fig.add_shape(
                    type="rect",
                    x0=legend_x,
                    x1=legend_x + timedelta(days=15),
                    y0=legend_y - 0.15,
                    y1=legend_y + 0.15,
                    fillcolor=color,
                    line=dict(color=color, width=1)
                )
                
                # Label
                fig.add_annotation(
                    x=legend_x + timedelta(days=25),
                    y=legend_y,
                    text=name,
                    showarrow=False,
                    font=dict(size=12, color='#333'),
                    xanchor='left'
                )
            
            # Milestone "Go-live" - Y HỆT MẪU
            go_live_date = df_data['End'].max()
            go_live_y = -0.3
            
            # Red triangle
            fig.add_shape(
                type="path",
                path=f"M {go_live_date.timestamp() * 1000} {go_live_y + 0.2} L {(go_live_date - timedelta(days=20)).timestamp() * 1000} {go_live_y - 0.3} L {(go_live_date + timedelta(days=20)).timestamp() * 1000} {go_live_y - 0.3} Z",
                fillcolor='#c41e1e',
                line=dict(color='#c41e1e', width=2),
                layer="above"
            )
            
            # Date label
            fig.add_annotation(
                x=go_live_date,
                y=go_live_y - 0.6,
                text=go_live_date.strftime('%d/%m/%Y'),
                showarrow=False,
                font=dict(size=11, color='white'),
                bgcolor='#c41e1e',
                borderpad=5
            )
            
            # Go-live label
            fig.add_annotation(
                x=go_live_date,
                y=go_live_y - 1.1,
                text="<b>Go-live</b>",
                showarrow=False,
                font=dict(size=14, color='#c41e1e'),
            )
            
            # Layout - Y HỆT MẪU
            fig.update_layout(
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e8e8e8',
                    showline=True,
                    linewidth=3,
                    linecolor='#1e5a9e',
                    range=[min_date - timedelta(days=20), max_date + timedelta(days=30)],
                    showticklabels=False
                ),
                yaxis=dict(
                    showticklabels=False,
                    showgrid=False,
                    range=[legend_y - 1.3, year_y + 0.5],
                    zeroline=False
                ),
                height=800,
                plot_bgcolor='white',
                paper_bgcolor='white',
                hovermode='closest',
                showlegend=False,
                margin=dict(l=30, r=30, t=20, b=80)
            )
            
            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
            
            # Hướng dẫn screenshot
            st.info("💡 **Tip**: Để lưu biểu đồ, bạn có thể chụp màn hình (screenshot) hoặc sử dụng nút camera 📷 trên góc trên bên phải của biểu đồ Plotly để download dưới dạng PNG")
            
            # Thống kê
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📋 Tổng Tasks", len(df_data))
            with col2:
                st.metric("⏱️ Thời gian dự án", f"{(max_date - min_date).days} ngày")
            with col3:
                st.metric("🚀 Ngày bắt đầu", min_date.strftime('%d/%m/%Y'))
            with col4:
                st.metric("🏁 Ngày kết thúc", max_date.strftime('%d/%m/%Y'))
            
            # Bảng dữ liệu
            with st.expander("📊 Xem chi tiết dữ liệu Tasks", expanded=False):
                display_df = df_data[['WBS', 'Task', 'Lead', 'Start', 'End', 'Category', 'Work_Days']].copy()
                display_df['Start'] = display_df['Start'].dt.strftime('%d/%m/%Y')
                display_df['End'] = display_df['End'].dt.strftime('%d/%m/%Y')
                display_df = display_df.rename(columns={
                    'WBS': 'Mã',
                    'Task': 'Công việc',
                    'Lead': 'Phụ trách',
                    'Start': 'Ngày bắt đầu',
                    'End': 'Ngày kết thúc',
                    'Category': 'Phân loại',
                    'Work_Days': 'Số ngày'
                })
                st.dataframe(display_df, use_container_width=True, height=400)
        
        else:
            st.error("❌ Không tìm thấy cột 'WBS' trong file Excel. Vui lòng kiểm tra lại file.")
            
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file: {str(e)}")
        st.info("Vui lòng đảm bảo file Excel có format đúng với cột WBS, Task, Lead, Start, End, ...")
        
else:
    st.info("📁 **Vui lòng upload file Excel để tạo biểu đồ Kế hoạch tổng quan**")
    
    # Hướng dẫn
    with st.expander("📖 **Hướng dẫn sử dụng**"):
        st.markdown("""
        ### ✅ Cách sử dụng:
        
        1. **Chuẩn bị file Excel** với các cột sau:
           - `WBS`: Mã công việc (1, 1.1, 2, 2.1, ...)
           - `Task`: Tên công việc
           - `Lead`: Người/đơn vị phụ trách
           - `Start`: Ngày bắt đầu (format: YYYY-MM-DD)
           - `End`: Ngày kết thúc (format: YYYY-MM-DD)
           - Các cột khác: Cal Days, %Done, Work Days, Days Done
        
        2. **Upload file** bằng cách click vào ô upload phía trên
        
        3. **Xem kết quả**:
           - Biểu đồ Gantt timeline với 5 giai đoạn: Vision, Validate, Construct, Deploy, Evolve
           - Tasks được tự động phân loại theo màu sắc
           - Có thể hover chuột để xem chi tiết từng task
        
        4. **Lưu biểu đồ**:
           - Click nút camera 📷 trên góc trên bên phải biểu đồ
           - Hoặc chụp màn hình (screenshot)
        
        ### 🎨 Màu sắc phân loại:
        
        - 🔵 **SAP**: Các tasks phát triển, lập trình, UAT, đào tạo, vận hành
        - 🟤 **NonSAP**: Xây dựng DLN, kiểm tra
        - 🟢 **CM**: Hợp đồng, khảo sát, UX/UI, thiết kế
        - 🔵 **IFRS & Accounting**: DLN, số dư, chuẩn hóa dữ liệu
        
        ### 📌 Lưu ý:
        
        - File Excel phải có dòng header chứa từ "WBS"
        - Ngày tháng phải có giá trị hợp lệ
        - Ứng dụng tự động phân loại tasks dựa vào từ khóa trong tên task
        """)
