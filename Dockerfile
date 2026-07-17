# 1. Gunakan sistem operasi Linux mini dengan Python
FROM python:3.12-slim

# 2. Buat folder bernama /app di dalam server
WORKDIR /app

# 3. Copy file requirements.txt dari laptop ke server
COPY requirements.txt .

# 4. Install semua library yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy seluruh sisa kode (main.py, app.py, dll)
COPY . .

# 6. Buka jalur komunikasi di port 7860 (Standar Hugging Face)
EXPOSE 7860

# 7. Perintah wajib untuk menyalakan mesin FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]