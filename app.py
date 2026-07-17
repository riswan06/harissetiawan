import streamlit as st
import time
import requests
import pandas as pd

st.set_page_config(page_title="Pencatat Keuangan AI", page_icon="💰")
st.title("💰 AI Pencatat Keuangan")

# --- BAGIAN INPUT ---
teks = st.text_input("Apa pengeluaranmu hari ini?", placeholder="Contoh: Beli kopi 20rb")

if st.button("Catat Pengeluaran"):
    if teks:
        res = requests.post("https://harissetiawan.onrender.com/catat", json={"teks": teks})
        if res.status_code == 200:
            st.success("Berhasil dicatat!")
            time.sleep(1) # Beri waktu sebentar sebelum refresh
            st.rerun()
        else:
            st.error("Gagal mencatat data.")
    else:
        st.warning("Silakan isi teks pengeluaran.")

# --- BAGIAN TAMPILAN RIWAYAT ---
st.divider()
st.subheader("📊 Laporan Pengeluaran")

if st.button("Refresh Data"):
    st.rerun()

# Mengambil data dari server (berada di luar tombol agar otomatis tampil)
res = requests.get("https://harissetiawan.onrender.com/riwayat")

if res.status_code == 200:
    data = res.json()
    
    if data:
        # 1. Ubah data JSON menjadi DataFrame
        df = pd.DataFrame(data)
        
        # 2. Hitung Total Keseluruhan
        total_pengeluaran = df['amount'].sum()
        st.metric(label="Total Pengeluaran", value=f"Rp {total_pengeluaran:,}")
        
        # 3. Proses Grafik
        df_kategori = df.groupby("category")["amount"].sum().reset_index()
        st.write("**Pengeluaran per Kategori**")
        st.bar_chart(data=df_kategori, x="category", y="amount", color="#ff4b4b")
        
        # 4. Tampilkan Daftar Transaksi & Tombol Hapus
        st.write("**Riwayat Transaksi Terakhir**")
        
        for index, item in enumerate(data):
            col1, col2 = st.columns([4, 1])
            
            nominal = item.get('amount', 0)
            kategori = item.get('category', 'Lainnya')
            col1.write(f"Rp {nominal:,} - **{kategori}**") 
            
            item_id = item.get('_id') or item.get('id') or str(index)
            
            if col2.button("Hapus", key=str(item_id)):
                url_delete = f"https://harissetiawan.onrender.com/delete/{item_id}"
                res_delete = requests.delete(url_delete)
                
                if res_delete.status_code == 200:
                    st.success("Data berhasil dihapus!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Gagal menghapus. Kode: {res_delete.status_code}")
    else:
        st.info("Belum ada data. Silakan catat pengeluaran pertama Anda!")
else:
    st.error("Gagal mengambil data dari server.")