import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from bson.errors import InvalidId

# Load file .env
load_dotenv()

# Gunakan os.getenv untuk membaca data
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
MONGO_URL = os.getenv("MONGO_URL")

# ... sisa kode Anda tetap sama ...

# Global variable untuk database
db_client = None

# 2. Lifespan Events (Manajemen Koneksi Database)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_client
    # Dieksekusi saat server start: Buka koneksi
    db_client = AsyncIOMotorClient(MONGO_URL)
    print("Berhasil terhubung ke MongoDB!")
    yield
    # Dieksekusi saat server dimatikan: Tutup koneksi
    db_client.close()
    print("Koneksi MongoDB ditutup.")

# 3. Inisialisasi Aplikasi FastAPI
app = FastAPI(title="AI Pencatat Keuangan", lifespan=lifespan)

# 4. Definisi Struktur Data (Pydantic)
class InputTeks(BaseModel):
    teks: str

class OutputPengeluaran(BaseModel):
    amount: int
    category: str
    date: str
    merchant: str
    note: str

# Tambahkan endpoint GET untuk mengambil riwayat
@app.get("/riwayat", response_model=list[OutputPengeluaran])
async def ambil_riwayat():
    db = db_client["keuangan_pribadi"]
    koleksi = db["histori_pengeluaran"]
    
    # Ambil 20 data terakhir
    cursor = koleksi.find({}, {"_id": 0}).sort("_id", -1).limit(20)
    items = await cursor.to_list(length=20)
    return items

@app.delete("/delete/{item_id}")
async def delete_data(item_id: str):
    try:
        # Coba konversi ID yang dikirim ke format ObjectId MongoDB
        obj_id = ObjectId(item_id)
        print(f"Backend menerima perintah hapus untuk ID: {item_id}") 
        
        result = collection.delete_one({"_id": obj_id})
        
        if result.deleted_count == 1:
            return {"message": "Data berhasil dihapus"}
        else:
            return {"error": "Data tidak ditemukan"}
        # Lakukan penghapusan
        result = collection.delete_one({"_id": obj_id})
        
        if result.deleted_count == 1:
            return {"message": "Data berhasil dihapus"}
        else:
            return {"error": "Data tidak ditemukan"}
            
    except InvalidId:
        # Ini akan menangkap error jika format ID tidak valid (bukan crash lagi)
        return {"error": "Format ID tidak valid"}
    except Exception as e:
        # Ini akan menangkap error tak terduga lainnya
        return {"error": f"Terjadi kesalahan server: {str(e)}"}

# 5. Endpoint Utama
@app.post("/catat", response_model=OutputPengeluaran)
async def catat_pengeluaran(data: InputTeks):
    prompt = f"""
    Anda adalah asisten keuangan pintar. Ekstrak informasi dari teks berikut ke dalam format JSON.
    Format JSON yang WAJIB digunakan persis seperti ini:
    {{
        "amount": ,
        "category": "",
        "date": "",
        "merchant": "",
        "note": ""
    }}

    Teks pengguna: "{data.teks}"
    """

    try:
        # Panggil Groq AI
        response = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Anda adalah asisten yang hanya membalas dengan JSON yang valid."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        hasil_json = json.loads(response.choices[0].message.content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses AI: {str(e)}")

    try:
        # Simpan ke MongoDB
        db = db_client["keuangan_pribadi"]     # Nama Database
        koleksi = db["histori_pengeluaran"]    # Nama Collection (Tabel)

        # Kita copy dictionary-nya karena operasi insert_one akan menambahkan '_id' ke dalam objek
        data_simpan = hasil_json.copy()
        
        # Perintah async untuk menyimpan ke database
        await koleksi.insert_one(data_simpan)
        
        return hasil_json
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan ke database: {str(e)}")