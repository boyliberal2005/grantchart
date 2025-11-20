import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Kế hoạch tổng quan", layout="wide")

# CSS
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(90deg, #1e5a9e 0%, #2b7dd4 100%);
        color: white;
        padding: 25px;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Kế hoạch tổng quan</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Upload file Excel", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        
        header_row = None
        for i in range(len(df)):
            if df.iloc[i, 0] == 'WBS':
                header_row = i
                break
        
        if header_row:
            df_data = pd.read_excel(uploaded_file, header=header_row)
            df_data.columns = ['WBS', 'Task', 'Lead', 'Start', 'End', 'Cal_Days', 'Percent_Done', 'Work_Days', 'Days_Done']
            
            df_data['Start'] = pd.to_datetime(df_data['Start'], errors='coerce')
            df_data['End'] = pd.to_datetime(df_data['End'], errors='coerce')
            df_data = df_data.dropna(subset=['Start', 'End'])
            
            # Classify
            def classify_task(task):
                t = str(task).lower()
                if any(k in t for k in ['khảo sát', 'ux', 'ui', 'hợp đồng']):
                    return 'CM'
                elif any(k in t for k in ['dln', 'số dư', 'accounting']):
                    return 'IFRS & Accounting Data Review'
                elif any(k in t for k in ['phát triển', 'uat', 'đào tạo']):
                    return 'SAP'
                else:
                    return 'NonSAP'
            
            df_data['Category'] = df_data['Task'].apply(classify_task)
            
            colors = {
                'SAP': '#1e5a9e',
                'NonSAP': '#8B4513',
                'CM': '#2ca02c',
                'IFRS & Accounting Data Review': '#17becf'
            }
            
            min_date = df_data['Start'].min()
            max_date = df_data['End'].max()
            
            months = pd.date_range(start=min_date.replace(day=1), end=max_date.replace(day=1) + timedelta(days=32), freq='MS')
            
            phases = [
                {'name': 'Vision', 'color': '#B8D8F0'},
                {'name': 'Validate', 'color': '#5DADE2'},
                {'name': 'Construct', 'color': '#8E44AD'},
                {'name': 'Deploy', 'color': '#6C3483'},
                {'name': 'Evolve', 'color': '#FF9933'}
            ]
            
            duration = (max_date - min_date).days
            for i, p in enumerate(phases):
                p['start'] = min_date + timedelta(days=i * duration / len(phases))
                p['end'] = min_date + timedelta(days=(i + 1) * duration / len(phases))
            
            fig = go.Figure()
            
            # Tasks
            y = 0
            for cat in ['CM', 'IFRS & Accounting Data Review', 'SAP', 'NonSAP']:
                for _, row in df_data[df_data['Category'] == cat].sort_values('Start').iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['Start'], row['End']],
                        y=[y, y],
                        mode='lines',
                        line=dict(color=colors[cat], width=20),
                        hovertext=row['Task'],
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=[row['Start'], row['End']],
                        y=[y, y],
                        mode='markers',
                        marker=dict(color=colors[cat], size=12, line=dict(color='white', width=2)),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    y += 0.8
            
            max_y = y
            
            # Phase backgrounds
            for p in phases:
                fig.add_shape(type="rect", x0=p['start'], x1=p['end'], y0=-2, y1=max_y + 5,
                             fillcolor=p['color'], opacity=0.2, layer="below", line_width=0)
            
            # Phase chevrons
            py = max_y + 1
            for p in phases:
                w = (p['end'] - p['start']).days
                x0, x1, x2, x3, x4 = p['start'], p['start'] + timedelta(days=w*0.05), p['end'] - timedelta(days=w*0.05), p['end'], p['end'] + timedelta(days=w*0.05)
                fig.add_trace(go.Scatter(
                    x=[x0, x0, x1, x2, x3, x4, x3, x2, x1, x0],
                    y=[py-0.4, py+0.4, py+0.4, py+0.4, py+0.4, py, py-0.4, py-0.4, py-0.4, py-0.4],
                    fill='toself', fillcolor=p['color'], line=dict(color=p['color']),
                    showlegend=False, hoverinfo='skip'
                ))
                fig.add_annotation(x=p['start'] + (p['end'] - p['start'])/2, y=py,
                                 text=f"<b>{p['name']}</b>", showarrow=False,
                                 font=dict(size=14, color='white'))
            
            # Month chevrons
            my = max_y + 2
            for i in range(len(months)-1):
                m, nm = months[i], months[i+1]
                w = (nm - m).days
                x0, x1, x2, x3, x4 = m, m + timedelta(days=w*0.1), nm - timedelta(days=w*0.1), nm, nm + timedelta(days=w*0.1)
                col = '#2874A6' if i % 2 == 0 else '#3498DB'
                fig.add_trace(go.Scatter(
                    x=[x0, x0, x1, x2, x3, x4, x3, x2, x1, x0],
                    y=[my-0.3, my+0.3, my+0.3, my+0.3, my+0.3, my, my-0.3, my-0.3, my-0.3, my-0.3],
                    fill='toself', fillcolor=col, line=dict(color=col),
                    showlegend=False, hoverinfo='skip'
                ))
                fig.add_annotation(x=m + timedelta(days=15), y=my,
                                 text=f"<b>T{m.month}</b>", showarrow=False,
                                 font=dict(size=11, color='white'))
            
            # Years
            yy = max_y + 3
            years = {}
            for m in months:
                if m.year not in years:
                    years[m.year] = {'s': m, 'e': m}
                else:
                    years[m.year]['e'] = m + timedelta(days=30)
            
            for yr, d in years.items():
                mid = d['s'] + (d['e'] - d['s'])/2
                fig.add_shape(type="line", x0=d['s'], x1=d['e'], y0=yy, y1=yy,
                            line=dict(color='#1e5a9e', width=3))
                fig.add_annotation(x=d['s'], y=yy, ax=-30, showarrow=True,
                                 arrowhead=2, arrowwidth=3, arrowcolor='#1e5a9e')
                fig.add_annotation(x=d['e'], y=yy, ax=30, showarrow=True,
                                 arrowhead=2, arrowwidth=3, arrowcolor='#1e5a9e')
                fig.add_annotation(x=mid, y=yy, text=f"<b>{yr}</b>", showarrow=False,
                                 font=dict(size=18, color='#1e5a9e'))
            
            # Legend
            lx = min_date - timedelta(days=20)
            ly = max_y * 0.3
            for i, (n, c) in enumerate(colors.items()):
                y = ly - i*2
                fig.add_shape(type="line", x0=lx, x1=lx + timedelta(days=10), y0=y, y1=y,
                            line=dict(color=c, width=10))
                fig.add_annotation(x=lx, y=y-0.5, text=n, showarrow=False,
                                 font=dict(size=10), xanchor='left')
            
            # Go-live
            gx, gy = max_date, -0.5
            fig.add_trace(go.Scatter(
                x=[gx, gx-timedelta(days=20), gx+timedelta(days=20), gx],
                y=[gy, gy-0.8, gy-0.8, gy],
                fill='toself', fillcolor='#c41e1e', line=dict(color='#c41e1e'),
                showlegend=False, hoverinfo='skip'
            ))
            fig.add_annotation(x=gx, y=gy-0.5, text=gx.strftime('%d/%m/%Y'),
                             showarrow=False, font=dict(size=11, color='white'))
            fig.add_annotation(x=gx, y=gy-1.3, text="<b>Go-live</b>",
                             showarrow=False, font=dict(size=14, color='#c41e1e'))
            fig.add_shape(type="line", x0=gx, x1=gx, y0=gy, y1=max_y,
                        line=dict(color='#c41e1e', width=3, dash='dash'))
            
            fig.update_layout(
                xaxis=dict(showgrid=True, gridcolor='#e8e8e8', showline=True,
                          linewidth=3, linecolor='#1e5a9e',
                          range=[min_date-timedelta(days=40), max_date+timedelta(days=40)],
                          showticklabels=False),
                yaxis=dict(showticklabels=False, showgrid=False,
                          range=[gy-1.5, yy+0.5], zeroline=False),
                height=800, plot_bgcolor='white', hovermode='closest',
                showlegend=False, margin=dict(l=150, r=50, t=20, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 Click nút 📷 trên biểu đồ để download PNG")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📋 Tasks", len(df_data))
            col2.metric("⏱️ Thời gian", f"{(max_date-min_date).days} ngày")
            col3.metric("🚀 Bắt đầu", min_date.strftime('%d/%m/%Y'))
            col4.metric("🏁 Kết thúc", max_date.strftime('%d/%m/%Y'))
            
            with st.expander("📊 Chi tiết"):
                d = df_data[['WBS', 'Task', 'Start', 'End', 'Category']].copy()
                d['WBS'] = d['WBS'].astype(str)
                d['Start'] = d['Start'].dt.strftime('%d/%m/%Y')
                d['End'] = d['End'].dt.strftime('%d/%m/%Y')
                st.dataframe(d, height=400)
    
    except Exception as e:
        st.error(f"❌ Lỗi: {str(e)}")
else:
    st.info("📁 Upload file Excel để tạo biểu đồ")
