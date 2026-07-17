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
        res = requests.post("https://harissetiawan.onrender.com/catat", json={"teks": teks})
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
    res = requests.get("https://harissetiawan.onrender.com/riwayat")
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
            
            # 5. Tampilkan Daftar Transaksi & Tombol Hapus
            st.write("**Riwayat Transaksi Terakhir**")
            
            # Kita lakukan perulangan untuk setiap data dari database
            for item in data:
                # Membagi baris menjadi 2 kolom: Kiri (teks) lebih lebar, Kanan (tombol) lebih kecil
                col1, col2 = st.columns([4, 1])
                
                # Tampilkan detail nominal dan kategorinya
                # get() digunakan agar tidak error jika kebetulan ada data lama yang formatnya berbeda
                nominal = item.get('amount', 0)
                kategori = item.get('category', 'Lainnya')
                col1.write(f"Rp {nominal:,} - **{kategori}**") 
                
                # Buat tombol hapus yang dikaitkan dengan ID unik dari MongoDB
                if col2.button("Hapus", key=item['_id']):
                    # Kirim perintah DELETE ke backend Render Anda
                    url_delete = f"https://harissetiawan.onrender.com/delete/{item['_id']}"
                    res_delete = requests.delete(url_delete)
                    
                    if res_delete.status_code == 200:
                        st.success("Data berhasil dihapus!")
                        st.rerun() # Refresh halaman agar data langsung hilang dari layar
                    else:
                        st.error("Gagal menghapus data.")
            
        else:
            st.info("Belum ada data. Silakan catat pengeluaran pertama Anda!")