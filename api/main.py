import sys
import os
import psycopg2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kvkk101.vercel.app"], 
    allow_methods=["POST"],
    allow_headers=["*"],
)

class QuizSubmit(BaseModel):
    isim_soyisim: str

DATABASE_URL = os.getenv("DB_URL")

@app.post("/api/submit")
def submit(data: QuizSubmit):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantı adresi (DATABASE_URL) bulunamadı.")

    try:
        # Neon DB'ye bağlan
        conn = psycopg2.connect(DATABASE_URL)
        
        with conn:
            with conn.cursor() as cursor:
                
                insert_query = """
                    INSERT INTO anaveri (isim_soyisim) 
                    VALUES (%s) 
                    RETURNING id;
                """
                cursor.execute(insert_query, (data.isim_soyisim,))
                
                inserted_id = cursor.fetchone()[0]
                
        # Bağlantıyı kapat
        conn.close()

        return {"mesaj": "Kaydedildi", "id": inserted_id}

    except Exception as e:
        # Hata durumunda bağlantıyı kapatmayı garanti altına al
        if 'conn' in locals() and not conn.closed:
            conn.close()
        raise HTTPException(status_code=500, detail=f"Kayıt başarısız: {str(e)}")