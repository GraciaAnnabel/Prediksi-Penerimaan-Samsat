import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Prediksi Samsat", layout="wide")

st.title("🚗 Prediksi Penerimaan Samsat Kantor Cabang Surabaya")

# Fungsi untuk membersihkan format rupiah
def bersihkan_rupiah(x):
    if isinstance(x, str):
        x = x.replace("Rp", "").replace(".", "").replace(",", "").strip()
    try:
        return float(x)
    except:
        return 0.0

# Upload file Excel
uploaded_file = st.file_uploader("Unggah file Excel (harus bernama 'SAMSAT.xlsx')", type=["xlsx"])

if uploaded_file is not None:
    if uploaded_file.name == "SAMSAT.xlsx":
        df = pd.read_excel(uploaded_file)
        st.success("✅ File berhasil diunggah dan dibaca.")
        st.dataframe(df)

        # Bersihkan kolom uang
        for kol in ['KD', 'SW', 'DENDA', 'TOTAL']:
            df[kol] = df[kol].apply(bersihkan_rupiah)

        # Sidebar - Pilih kantor
        st.sidebar.header("📌 Filter")
        kantor_list = df["Kantor"].unique()
        kantor_terpilih = st.sidebar.selectbox("Pilih Kantor", kantor_list)
        df_kantor = df[df["Kantor"] == kantor_terpilih].copy()

        st.subheader(f"📄 Tabel Prediksi: {kantor_terpilih}")
        st.dataframe(df_kantor[['Bulan', 'KD', 'SW', 'DENDA', 'TOTAL']])

        # Long format untuk visualisasi
        df_long = df_kantor.melt(id_vars='Bulan', value_vars=['KD', 'SW', 'DENDA', 'TOTAL'],
                                 var_name='Jenis', value_name='Nilai')

        # 1. Tren pendapatan per jenis (line chart)
        st.subheader("📈 Tren Pendapatan per Jenis pada Kantor Samsat")
        jenis_terpilih = st.selectbox("Pilih Jenis Pendapatan", ['KD', 'SW', 'DENDA', 'TOTAL'])
        df_jenis = df_kantor[['Bulan', jenis_terpilih]].copy()

        chart_jenis = alt.Chart(df_jenis).mark_line(point=True).encode(
            x='Bulan:N',
            y=alt.Y(f'{jenis_terpilih}:Q', title='Nilai (Rp)'),
            tooltip=['Bulan', jenis_terpilih]
        ).properties(width=800, height=400)
        st.altair_chart(chart_jenis, use_container_width=True)

        # 2. Perbandingan antar jenis pendapatan (bar chart)
        st.subheader("📊 Perbandingan Jenis Pendapatan pada Setiap Kantor Samsat")
        chart_bar = alt.Chart(df_long).mark_bar().encode(
            x='Bulan:N',
            y='Nilai:Q',
            color='Jenis:N',
            tooltip=['Bulan', 'Jenis', 'Nilai']
        ).properties(width=800, height=400)
        st.altair_chart(chart_bar, use_container_width=True)


        # 3. Ringkasan total seluruh kantor per bulan (area chart + tabel)
        st.subheader("🧮 Ringkasan Total Seluruh Kantor Samsat Setiap Bulan")
        df_summary = df.groupby("Bulan")[['KD', 'SW', 'DENDA', 'TOTAL']].sum().reset_index()
        for kol in ['KD', 'SW', 'DENDA', 'TOTAL']:
            df_summary[kol] = pd.to_numeric(df_summary[kol], errors='coerce')

        df_summary_long = df_summary.melt(id_vars='Bulan', value_vars=['KD', 'SW', 'DENDA', 'TOTAL'],
                                          var_name='Jenis', value_name='Nilai')

        area_chart = alt.Chart(df_summary_long).mark_area(opacity=0.5).encode(
            x='Bulan:N',
            y='Nilai:Q',
            color='Jenis:N'
        ).properties(width=800, height=400)
        st.altair_chart(area_chart, use_container_width=True)

        st.dataframe(
            df_summary.style.format({
                'KD': '{:,.0f}',
                'SW': '{:,.0f}',
                'DENDA': '{:,.0f}',
                'TOTAL': '{:,.0f}'
            })
        )

    else:
        st.error("❌ Nama file harus 'SAMSAT.xlsx'. Silakan unggah file dengan nama yang sesuai.")
else:
    st.info("📄 Silakan upload file Excel hasil prediksi.")
