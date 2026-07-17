import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Pencatat Keuangan AI", page_icon="💰")
st.title("💰 AI Pencatat Keuangan")

# Bagian Input
teks = st.text_input("Apa pengeluaranmu hari ini?", placeholder="Contoh: Beli kopi 20rb")

if st.button("Catat Pengeluaran"):
    if teks:
        # Kirim ke FastAPI kita
        res = requests.post("http://127.0.0.1:8000/catat", json={"teks": teks})
        if res.status_code == 200:
            st.success("Berhasil dicatat!")
        else:
            st.error("Gagal mencatat data.")
    else:
        st.warning("Silakan isi teks pengeluaran.")

# Bagian Tampilan Riwayat & Visualisasi
st.divider()
st.subheader("📊 Laporan Pengeluaran")

if st.button("Refresh Data"):
    res = requests.get("http://127.0.0.1:8000/riwayat")
    if res.status_code == 200:
        data = res.json()
        if data:
            # 1. Ubah data JSON menjadi DataFrame Pandas
            df = pd.DataFrame(data)
            
            # 2. Hitung Total Keseluruhan
            total_pengeluaran = df['amount'].sum()
            
            # Menampilkan angka total dengan kotak metrik yang rapi
            st.metric(label="Total Pengeluaran", value=f"Rp {total_pengeluaran:,}")
            
            # 3. Proses Data untuk Grafik (Group By Kategori)
            # Ini akan mengelompokkan kategori yang sama dan menjumlahkan nominalnya
            df_kategori = df.groupby("category")["amount"].sum().reset_index()
            
            # 4. Tampilkan Grafik Batang
            st.write("**Pengeluaran per Kategori**")
            st.bar_chart(data=df_kategori, x="category", y="amount", color="#ff4b4b")
            
            # 5. Tampilkan Tabel Detail
            st.write("**Riwayat Transaksi Terakhir**")
            st.dataframe(df) # st.dataframe lebih interaktif daripada st.table
            
        else:
            st.info("Belum ada data. Silakan catat pengeluaran pertama Anda!")