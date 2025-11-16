import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statistics import mode, multimode
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Kalkulator Statistika Lengkap",
    page_icon="📊",
    layout="wide"
)

# Custom CSS untuk memperindah tampilan
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .outlier-alert {
        background-color: #FFF3CD;
        border: 1px solid #FFEAA7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header aplikasi
st.markdown('<h1 class="main-header">📊 Kalkulator Statistika Lengkap</h1>', unsafe_allow_html=True)

# Fungsi untuk mendeteksi outlier menggunakan IQR method
def detect_outliers_iqr(data):
    if len(data) < 2:
        return []
    
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    return outliers, lower_bound, upper_bound, Q1, Q3

# Fungsi untuk membuat box plot
def create_box_plot(data, outliers):
    fig = go.Figure()
    
    # Box plot utama
    fig.add_trace(go.Box(
        y=data,
        name="Data",
        boxpoints='suspectedoutliers',  # Tampilkan titik yang diduga outlier
        marker=dict(color='rgb(8,81,156)'),
        line=dict(color='rgb(8,81,156)')
    ))
    
    fig.update_layout(
        title='Box Plot dengan Deteksi Outlier',
        yaxis_title='Nilai',
        showlegend=False,
        height=400
    )
    
    return fig

# Fungsi untuk membuat histogram
def create_histogram(data, outliers):
    fig = go.Figure()
    
    # Warna berbeda untuk outlier
    colors = ['#2E86AB' if x not in outliers else '#FF6B6B' for x in data]
    
    fig.add_trace(go.Histogram(
        x=data,
        marker_color=colors,
        opacity=0.7,
        name="Distribusi Data"
    ))
    
    fig.update_layout(
        title='Histogram dengan Highlight Outlier',
        xaxis_title='Nilai',
        yaxis_title='Frekuensi',
        showlegend=False,
        height=400
    )
    
    return fig

# Fungsi untuk membuat scatter plot
def create_scatter_plot(data, outliers):
    fig = go.Figure()
    
    for i, value in enumerate(data):
        if value in outliers:
            fig.add_trace(go.Scatter(
                x=[i],
                y=[value],
                mode='markers',
                marker=dict(color='red', size=10, symbol='x'),
                name='Outlier'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[i],
                y=[value],
                mode='markers',
                marker=dict(color='blue', size=8),
                name='Data Normal'
            ))
    
    fig.update_layout(
        title='Scatter Plot Data dengan Identifikasi Outlier',
        xaxis_title='Index Data',
        yaxis_title='Nilai',
        showlegend=True,
        height=400
    )
    
    return fig

# Input data
st.sidebar.header("Input Data")
input_method = st.sidebar.radio("Pilih metode input:", ("Manual", "Upload File CSV"))

data = []

if input_method == "Manual":
    input_text = st.sidebar.text_area(
        "Masukkan data numerik (pisahkan dengan koma):",
        placeholder="Contoh: 5, 7, 8, 9, 10, 10, 25, 30, 100"
    )
    if input_text:
        try:
            data = [float(x.strip()) for x in input_text.split(',')]
        except ValueError:
            st.error("Error: Pastikan semua data adalah angka yang valid!")
else:
    uploaded_file = st.sidebar.file_uploader("Upload file CSV", type=['csv'])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if df.empty:
                st.error("File CSV kosong!")
            else:
                # Pilih kolom numerik
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    selected_col = st.sidebar.selectbox("Pilih kolom data:", numeric_cols)
                    data = df[selected_col].dropna().tolist()
                else:
                    st.error("Tidak ada kolom numerik dalam file CSV!")
        except Exception as e:
            st.error(f"Error membaca file: {str(e)}")

# Main content
if data:
    # Deteksi outlier
    outliers, lower_bound, upper_bound, Q1, Q3 = detect_outliers_iqr(data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Preview Data")
        df_preview = pd.DataFrame(data, columns=['Data'])
        st.dataframe(df_preview, height=200)
    
    with col2:
        st.subheader("Statistik Dasar")
        st.metric("Jumlah Data", len(data))
        st.metric("Nilai Minimum", f"{min(data):.2f}")
        st.metric("Nilai Maksimum", f"{max(data):.2f}")
        st.metric("Range", f"{max(data) - min(data):.2f}")

    # Perhitungan statistika
    st.subheader("Hasil Perhitungan Statistika")
    
    try:
        # Mean
        mean_val = np.mean(data)
        
        # Median
        median_val = np.median(data)
        
        # Modus
        try:
            mode_vals = multimode(data)
            if len(mode_vals) == len(data):
                mode_result = "Tidak ada modus"
            else:
                mode_result = ", ".join(map(str, mode_vals))
        except:
            mode_result = "Error dalam menghitung modus"
        
        # Standar Deviasi
        std_val = np.std(data, ddof=1)  # Sample standard deviation
        
        # Variance
        variance_val = np.var(data, ddof=1)
        
        # Quartiles
        q1_val = np.percentile(data, 25)
        q3_val = np.percentile(data, 75)
        iqr_val = q3_val - q1_val
        
        # Tampilkan hasil
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="result-box">
                <h4>📈 Mean (Rata-rata)</h4>
                <h2>{mean_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h4>🔢 Modus</h4>
                <h2>{mode_result}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h4>📊 Variance</h4>
                <h2>{variance_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="result-box">
                <h4>🎯 Median (Nilai Tengah)</h4>
                <h2>{median_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h4>📏 Standar Deviasi</h4>
                <h2>{std_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h4>📐 IQR (Q3 - Q1)</h4>
                <h2>{iqr_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="result-box">
                <h4>⬇️ Quartile 1 (Q1)</h4>
                <h2>{q1_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h4>⬆️ Quartile 3 (Q3)</h4>
                <h2>{q3_val:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-box">
                <h4>🔍 Jumlah Outlier</h4>
                <h2>{len(outliers)}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error dalam perhitungan: {str(e)}")

    # Visualisasi Outlier
    st.subheader("🔍 Analisis dan Visualisasi Outlier")
    
    if outliers:
        st.markdown(f"""
        <div class="outlier-alert">
            <h4>⚠️ Outlier Terdeteksi!</h4>
            <p><strong>Jumlah outlier:</strong> {len(outliers)}</p>
            <p><strong>Nilai outlier:</strong> {', '.join([f'{x:.2f}' for x in outliers])}</p>
            <p><strong>Batas bawah:</strong> {lower_bound:.2f}</p>
            <p><strong>Batas atas:</strong> {upper_bound:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ Tidak ada outlier yang terdeteksi dalam data.")
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_box_plot(data, outliers), use_container_width=True)
        
        # Informasi tentang box plot
        with st.expander("ℹ️ Cara membaca Box Plot"):
            st.markdown("""
            - **Box**: Menunjukkan interquartile range (IQR) dari Q1 sampai Q3
            - **Garis di dalam box**: Median (nilai tengah)
            - **Whiskers**: Batas normal data (Q1 - 1.5×IQR sampai Q3 + 1.5×IQR)
            - **Titik di luar whiskers**: Outlier
            """)
    
    with col2:
        st.plotly_chart(create_histogram(data, outliers), use_container_width=True)
        
        # Informasi tentang histogram
        with st.expander("ℹ️ Cara membaca Histogram"):
            st.markdown("""
            - **Batang biru**: Data normal
            - **Batang merah**: Outlier
            - **Sumbu X**: Nilai data
            - **Sumbu Y**: Frekuensi kemunculan
            """)
    
    # Scatter plot
    st.plotly_chart(create_scatter_plot(data, outliers), use_container_width=True)
    
    # Data summary
    st.subheader("📋 Summary Data Lengkap")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Deskripsi Statistik:**")
        desc_stats = {
            'Metric': ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max', 'IQR'],
            'Value': [
                len(data),
                f"{mean_val:.2f}",
                f"{std_val:.2f}",
                f"{min(data):.2f}",
                f"{q1_val:.2f}",
                f"{median_val:.2f}",
                f"{q3_val:.2f}",
                f"{max(data):.2f}",
                f"{iqr_val:.2f}"
            ]
        }
        st.table(pd.DataFrame(desc_stats))
    
    with col2:
        st.write("**Informasi Outlier:**")
        outlier_info = {
            'Metric': ['Total Outlier', 'Lower Bound', 'Upper Bound', 'Outlier Percentage'],
            'Value': [
                len(outliers),
                f"{lower_bound:.2f}",
                f"{upper_bound:.2f}",
                f"{(len(outliers)/len(data))*100:.1f}%"
            ]
        }
        st.table(pd.DataFrame(outlier_info))
        
        if outliers:
            st.write("**Daftar Outlier:**")
            outlier_df = pd.DataFrame(outliers, columns=['Nilai Outlier'])
            st.dataframe(outlier_df, height=150)

else:
    st.info("👈 Silakan masukkan data atau upload file CSV di sidebar untuk memulai analisis.")
    
    # Contoh data
    with st.expander("💡 Contoh format data yang bisa digunakan"):
        st.code("""
        # Contoh data normal
        15, 18, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50
        
        # Contoh data dengan outlier
        15, 18, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 120, 150
        """)

# Footer
st.markdown("---")
st.markdown(
    "**Kalkulator Statistika Lengkap** | Dibuat Oleh Kelompok 2 Statistika Terapan (Tio Dwi Akbar, Ilham Adji Sudharyo, Wahyudi, Arief Dhiemas Suryanto) | "
    "Pascasarjana Ilmu Komputer"
)