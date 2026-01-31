"""
Dashboard Interaktif: Analisis Desain Kemasan Corrugated Cardboard
Siap deploy ke Streamlit Cloud - WITH IMAGES

Author: [Nama Anda]
Version: 1.1
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="Dashboard Analisis Kemasan",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f4e79;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    .box-image {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.title("📦 Dashboard Analisis Desain Kemasan")
st.markdown("*Simulasi parameter kemasan corrugated cardboard menggunakan Formula McKee*")
st.markdown("---")

# ============================================
# SIDEBAR: INPUT PARAMETER
# ============================================
with st.sidebar:
    st.header("⚙️ Parameter Input")
    
    # Tipe Kemasan dengan Gambar
    st.subheader("📦 Tipe Kemasan")
    tipe_kemasan = st.selectbox(
        "Pilih Tipe Kemasan",
        options=[
            "1 - Box Arsip (Tutup & Handle)",
            "2 - Box Shipping (Handle Samping)",
            "3 - Box Storage (Tutup Atas)",
            "4 - Box Produk (Flip-Top)",
            "5 - Box Die-Cut (Flat/Pizza)",
            "6 - Box Standar (Tutup Terpisah)"
        ],
        index=5,
        help="Pilih tipe kemasan sesuai kebutuhan produk"
    )
    
    # Extract nomor tipe
    tipe_nomor = int(tipe_kemasan.split(" - ")[0])
    
    st.markdown("---")
    
    # Dimensi Kemasan
    st.subheader("📐 Dimensi Kemasan (mm)")
    col1, col2 = st.columns(2)
    with col1:
        panjang = st.number_input("Panjang (L)", min_value=50, max_value=1000, value=300, step=10)
        tinggi = st.number_input("Tinggi (H)", min_value=50, max_value=500, value=150, step=10)
    with col2:
        lebar = st.number_input("Lebar (W)", min_value=50, max_value=1000, value=200, step=10)
    
    st.markdown("---")
    
    # Material Properties
    st.subheader("🏭 Material Properties")
    jenis_flute = st.selectbox(
        "Jenis Flute",
        options=["A-Flute (4.8mm)", "B-Flute (3.0mm)", "C-Flute (4.0mm)", "E-Flute (1.5mm)", "BC-Flute (6.5mm)"],
        index=2,
        help="Pilih jenis flute sesuai spesifikasi material"
    )
    
    flute_thickness = {
        "A-Flute (4.8mm)": 4.8,
        "B-Flute (3.0mm)": 3.0,
        "C-Flute (4.0mm)": 4.0,
        "E-Flute (1.5mm)": 1.5,
        "BC-Flute (6.5mm)": 6.5
    }
    ketebalan = flute_thickness[jenis_flute]
    
    ect = st.slider(
        "Edge Crush Test - ECT (kN/m)", 
        min_value=3.0, max_value=15.0, value=7.0, step=0.5,
        help="Nilai ECT dari hasil pengujian material"
    )
    
    bct_target = st.number_input(
        "Target BCT (kg)", 
        min_value=50, max_value=1000, value=200, step=10,
        help="Target kekuatan tekan box yang diinginkan"
    )
    
    st.markdown("---")
    
    # Kondisi Distribusi
    st.subheader("🌡️ Kondisi Distribusi")
    kelembaban = st.slider(
        "Kelembaban Relatif (%)", 
        min_value=30, max_value=95, value=65,
        help="Kondisi kelembaban saat penyimpanan/distribusi"
    )
    
    durasi_simpan = st.slider(
        "Durasi Penyimpanan (hari)", 
        min_value=1, max_value=180, value=30,
        help="Estimasi lama penyimpanan produk"
    )
    
    st.markdown("---")
    st.caption("Dashboard by IPB University")

# ============================================
# KALKULASI
# ============================================

# Volume dan luas permukaan
volume_cm3 = (panjang * lebar * tinggi) / 1000
luas_permukaan = 2 * (panjang*lebar + lebar*tinggi + panjang*tinggi) / 100
perimeter = 2 * (panjang + lebar)

# Estimasi BCT menggunakan formula McKee
k_mckee = 5.87
bct_calculated = k_mckee * ect * np.sqrt(ketebalan * perimeter / 1000)

# Faktor koreksi kelembaban
humidity_factor = 1 - 0.01 * (kelembaban - 50) * 0.02
bct_adjusted = bct_calculated * humidity_factor

# Faktor koreksi durasi penyimpanan (creep factor)
if durasi_simpan <= 1:
    creep_factor = 0.85
elif durasi_simpan <= 30:
    creep_factor = 0.8 - 0.006 * durasi_simpan
else:
    creep_factor = 0.6

bct_final = bct_adjusted * creep_factor

# Safety factor
safety_factor = bct_final / bct_target if bct_target > 0 else 0

# Estimasi biaya material
area_material = luas_permukaan * 1.15
harga_per_cm2 = 0.05 + (ketebalan * 0.02)
biaya_material = area_material * harga_per_cm2

# ============================================
# MAIN CONTENT
# ============================================

# Top Section: Image and Metrics
col_img, col_metrics = st.columns([1, 2])

with col_img:
    st.subheader("🖼️ Tipe Kemasan")
    
    # Display image based on selection
    image_descriptions = {
        1: "Box Arsip dengan Tutup & Handle",
        2: "Box Shipping dengan Handle Samping", 
        3: "Box Storage dengan Tutup Atas",
        4: "Box Produk Flip-Top",
        5: "Box Die-Cut (Flat/Pizza Style)",
        6: "Box Standar dengan Tutup Terpisah"
    }
    
    try:
        st.image(f"images/{tipe_nomor}.png", caption=image_descriptions[tipe_nomor], use_container_width=True)
    except:
        st.info(f"📦 **{image_descriptions[tipe_nomor]}**\n\n*Upload gambar `{tipe_nomor}.png` ke folder `images/` di repository GitHub*")
    
    # Karakteristik tipe kemasan
    karakteristik = {
        1: "Cocok untuk dokumen, arsip, penyimpanan jangka panjang",
        2: "Cocok untuk pengiriman barang besar, moving box",
        3: "Cocok untuk penyimpanan barang rumah tangga",
        4: "Cocok untuk produk retail, kemasan consumer goods",
        5: "Cocok untuk makanan (pizza, pastry), barang flat",
        6: "Cocok untuk berbagai keperluan umum"
    }
    st.caption(karakteristik[tipe_nomor])

with col_metrics:
    st.subheader("📊 Hasil Analisis")
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric(
            label="📦 Volume Internal",
            value=f"{volume_cm3:,.0f} cm³"
        )
    
    with m2:
        delta_bct = bct_final - bct_target
        st.metric(
            label="💪 BCT Terhitung",
            value=f"{bct_final:.1f} kg",
            delta=f"{delta_bct:.1f} kg vs target"
        )
    
    with m3:
        if safety_factor >= 1.5:
            status = "✅ AMAN"
        elif safety_factor >= 1.0:
            status = "⚠️ MARGINAL"
        else:
            status = "❌ TIDAK AMAN"
        
        st.metric(
            label="🛡️ Safety Factor",
            value=f"{safety_factor:.2f}",
            delta=status
        )
    
    with m4:
        st.metric(
            label="💰 Estimasi Biaya",
            value=f"Rp {biaya_material:,.0f}"
        )
    
    # Status Box
    if safety_factor >= 1.5:
        st.success(f"✅ **DESAIN AMAN** - Safety Factor {safety_factor:.2f} melebihi batas minimum 1.5")
    elif safety_factor >= 1.0:
        st.warning(f"⚠️ **DESAIN MARGINAL** - Safety Factor {safety_factor:.2f} perlu ditingkatkan (target ≥ 1.5)")
    else:
        st.error(f"❌ **DESAIN TIDAK AMAN** - Safety Factor {safety_factor:.2f} di bawah batas minimum. Tingkatkan ECT atau gunakan flute lebih tebal!")

st.markdown("---")

# ============================================
# TABS VISUALISASI
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Analisis BCT", "📈 Sensitivitas Parameter", "📋 Data Summary", "ℹ️ Tentang"])

with tab1:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Breakdown BCT")
        
        bct_data = pd.DataFrame({
            'Tahap': ['BCT Teoritis', 'Setelah Koreksi RH', 'Setelah Koreksi Creep'],
            'Nilai': [bct_calculated, bct_adjusted, bct_final]
        })
        
        fig_bct = go.Figure()
        fig_bct.add_trace(go.Bar(
            x=bct_data['Tahap'],
            y=bct_data['Nilai'],
            marker_color=['#3498db', '#2ecc71', '#e74c3c'],
            text=[f"{v:.1f} kg" for v in bct_data['Nilai']],
            textposition='outside'
        ))
        fig_bct.add_hline(
            y=bct_target, 
            line_dash="dash", 
            line_color="orange",
            annotation_text=f"Target: {bct_target} kg",
            annotation_position="top right"
        )
        fig_bct.update_layout(
            title="Perbandingan BCT pada Berbagai Kondisi",
            yaxis_title="BCT (kg)",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_bct, use_container_width=True)
    
    with col_right:
        st.subheader("Faktor Koreksi")
        
        factor_data = pd.DataFrame({
            'Faktor': ['Humidity Factor', 'Creep Factor', 'Total Reduction'],
            'Nilai': [humidity_factor, creep_factor, humidity_factor * creep_factor]
        })
        
        fig_factor = px.bar(
            factor_data,
            x='Faktor',
            y='Nilai',
            color='Faktor',
            text=[f"{v:.2%}" for v in factor_data['Nilai']],
            color_discrete_sequence=['#3498db', '#9b59b6', '#e74c3c']
        )
        fig_factor.update_layout(
            title="Faktor Koreksi yang Diterapkan",
            yaxis_title="Faktor (rasio)",
            showlegend=False,
            height=400
        )
        fig_factor.update_traces(textposition='outside')
        st.plotly_chart(fig_factor, use_container_width=True)

with tab2:
    st.subheader("📈 Analisis Sensitivitas")
    
    col_sens1, col_sens2 = st.columns(2)
    
    with col_sens1:
        st.markdown("**Pengaruh ECT terhadap BCT**")
        
        ect_range = np.linspace(3, 15, 25)
        bct_values = []
        
        for e in ect_range:
            bct_calc = k_mckee * e * np.sqrt(ketebalan * perimeter / 1000)
            bct_adj = bct_calc * humidity_factor * creep_factor
            bct_values.append(bct_adj)
        
        sensitivity_df = pd.DataFrame({
            'ECT (kN/m)': ect_range,
            'BCT (kg)': bct_values
        })
        
        fig_sens = px.line(
            sensitivity_df,
            x='ECT (kN/m)',
            y='BCT (kg)',
            markers=True
        )
        fig_sens.add_hline(y=bct_target, line_dash="dash", line_color="red",
                          annotation_text=f"Target: {bct_target} kg")
        fig_sens.add_vline(x=ect, line_dash="dot", line_color="green",
                          annotation_text=f"Current: {ect} kN/m")
        fig_sens.update_layout(height=350)
        st.plotly_chart(fig_sens, use_container_width=True)
    
    with col_sens2:
        st.markdown("**Pengaruh Kelembaban terhadap BCT**")
        
        rh_range = np.linspace(30, 95, 20)
        bct_rh_values = []
        
        for rh in rh_range:
            hf = 1 - 0.01 * (rh - 50) * 0.02
            bct_rh = bct_calculated * hf * creep_factor
            bct_rh_values.append(bct_rh)
        
        rh_df = pd.DataFrame({
            'Kelembaban (%)': rh_range,
            'BCT (kg)': bct_rh_values
        })
        
        fig_rh = px.area(rh_df, x='Kelembaban (%)', y='BCT (kg)')
        fig_rh.add_hline(y=bct_target, line_dash="dash", line_color="red")
        fig_rh.add_vline(x=kelembaban, line_dash="dot", line_color="green",
                        annotation_text=f"Current: {kelembaban}%")
        fig_rh.update_layout(height=350)
        st.plotly_chart(fig_rh, use_container_width=True)
    
    # Heatmap
    st.markdown("**Heatmap: ECT vs Kelembaban → BCT**")
    
    ect_vals = np.linspace(4, 12, 9)
    rh_vals = np.linspace(40, 90, 6)
    
    heatmap_data = []
    for rh in rh_vals:
        row = []
        for e in ect_vals:
            hf = 1 - 0.01 * (rh - 50) * 0.02
            bct = k_mckee * e * np.sqrt(ketebalan * perimeter / 1000) * hf * creep_factor
            row.append(bct)
        heatmap_data.append(row)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=[f"{e:.0f}" for e in ect_vals],
        y=[f"{rh:.0f}%" for rh in rh_vals],
        colorscale='RdYlGn',
        text=[[f"{v:.0f}" for v in row] for row in heatmap_data],
        texttemplate="%{text}",
        colorbar_title="BCT (kg)"
    ))
    fig_heatmap.update_layout(
        title=f"BCT (kg) untuk berbagai kombinasi ECT dan RH (Flute: {jenis_flute})",
        xaxis_title="ECT (kN/m)",
        yaxis_title="Kelembaban Relatif",
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.subheader("📋 Ringkasan Data")
    
    col_input, col_output = st.columns(2)
    
    with col_input:
        st.markdown("**Parameter Input:**")
        input_data = pd.DataFrame({
            'Parameter': [
                'Tipe Kemasan', 'Panjang (L)', 'Lebar (W)', 'Tinggi (H)', 
                'Jenis Flute', 'Ketebalan Board', 'ECT',
                'Target BCT', 'Kelembaban', 'Durasi Simpan'
            ],
            'Nilai': [
                tipe_kemasan.split(" - ")[1],
                f"{panjang} mm", f"{lebar} mm", f"{tinggi} mm",
                jenis_flute, f"{ketebalan} mm", f"{ect} kN/m",
                f"{bct_target} kg", f"{kelembaban}%", f"{durasi_simpan} hari"
            ]
        })
        st.dataframe(input_data, hide_index=True, use_container_width=True)
    
    with col_output:
        st.markdown("**Hasil Perhitungan:**")
        output_data = pd.DataFrame({
            'Parameter': [
                'Volume Internal', 'Luas Permukaan', 'Perimeter',
                'BCT Teoritis', 'Humidity Factor', 'Creep Factor',
                'BCT Final', 'Safety Factor', 'Status', 'Estimasi Biaya'
            ],
            'Nilai': [
                f"{volume_cm3:,.1f} cm³",
                f"{luas_permukaan:,.1f} cm²",
                f"{perimeter} mm",
                f"{bct_calculated:.1f} kg",
                f"{humidity_factor:.3f}",
                f"{creep_factor:.3f}",
                f"{bct_final:.1f} kg",
                f"{safety_factor:.2f}",
                status,
                f"Rp {biaya_material:,.0f}"
            ]
        })
        st.dataframe(output_data, hide_index=True, use_container_width=True)
    
    # Export
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    export_df = pd.DataFrame({
        'Kategori': ['Input']*10 + ['Output']*10,
        'Parameter': input_data['Parameter'].tolist() + output_data['Parameter'].tolist(),
        'Nilai': input_data['Nilai'].tolist() + output_data['Nilai'].tolist()
    })
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name="hasil_analisis_kemasan.csv",
            mime="text/csv"
        )
    
    with col_dl2:
        json_data = {
            "input": {
                "tipe_kemasan": tipe_kemasan,
                "dimensi": {"panjang": panjang, "lebar": lebar, "tinggi": tinggi},
                "material": {"flute": jenis_flute, "ketebalan": ketebalan, "ect": ect},
                "kondisi": {"kelembaban": kelembaban, "durasi_simpan": durasi_simpan},
                "target_bct": bct_target
            },
            "output": {
                "volume_cm3": round(volume_cm3, 1),
                "bct_teoritis": round(bct_calculated, 1),
                "bct_final": round(bct_final, 1),
                "safety_factor": round(safety_factor, 2),
                "status": status,
                "estimasi_biaya": round(biaya_material, 0)
            }
        }
        import json
        st.download_button(
            label="📋 Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name="hasil_analisis_kemasan.json",
            mime="application/json"
        )

with tab4:
    st.subheader("ℹ️ Tentang Dashboard")
    
    st.markdown("""
    ### Formula yang Digunakan
    
    Dashboard ini menggunakan **Formula McKee (simplified)** untuk estimasi Box Compression Test (BCT):
    
    $$BCT = k \\times ECT \\times \\sqrt{h \\times Z}$$
    
    Dimana:
    - **k** = 5.87 (konstanta McKee)
    - **ECT** = Edge Crush Test (kN/m)
    - **h** = Ketebalan board (mm)
    - **Z** = Perimeter kemasan (mm)
    
    ### Faktor Koreksi
    
    1. **Humidity Factor**: Koreksi berdasarkan kelembaban relatif
       - RH < 50%: BCT meningkat
       - RH > 50%: BCT menurun
    
    2. **Creep Factor**: Koreksi berdasarkan durasi penyimpanan
       - 1 hari: 0.85
       - 30 hari: ~0.62
       - >30 hari: 0.60
    
    ### Safety Factor
    
    | Safety Factor | Status |
    |---------------|--------|
    | ≥ 1.5 | ✅ AMAN |
    | 1.0 - 1.5 | ⚠️ MARGINAL |
    | < 1.0 | ❌ TIDAK AMAN |
    
    ### Tipe Kemasan
    
    | No | Tipe | Karakteristik |
    |----|------|---------------|
    | 1 | Box Arsip | Tutup & handle, penyimpanan dokumen |
    | 2 | Box Shipping | Handle samping, pengiriman barang besar |
    | 3 | Box Storage | Tutup atas, penyimpanan rumah tangga |
    | 4 | Box Produk | Flip-top, kemasan retail |
    | 5 | Box Die-Cut | Flat/pizza, makanan & barang flat |
    | 6 | Box Standar | Tutup terpisah, keperluan umum |
    
    ### Catatan Penting
    
    ⚠️ Hasil estimasi bersifat **indikatif**. Untuk hasil akurat, disarankan:
    - Melakukan pengujian laboratorium (BCT test)
    - Menggunakan simulasi FEA (Finite Element Analysis)
    - Validasi dengan kondisi distribusi aktual
    
    ---
    
    **Referensi:**
    - McKee, R.C., Gander, J.W., & Wachuta, J.R. (1963). Compression strength formula for corrugated boxes.
    - TAPPI T 804 - Compression test of fiberboard shipping containers
    """)
    
    st.markdown("---")
    st.info("💡 Dashboard ini dikembangkan untuk keperluan edukasi dan penelitian.")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("📦 Dashboard Analisis Kemasan v1.1 | Dibuat dengan Streamlit | IPB University")
