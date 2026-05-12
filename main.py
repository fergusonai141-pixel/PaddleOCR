import os

# 1. Configurare Stabilitate Paddle (TREBUIE făcute la începutul absolut, înainte de import paddle)
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_use_pir_api"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import logging
from fastapi import FastAPI, HTTPException
from paddleocr import PaddleOCR
import httpx
import io
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr-api")

app = FastAPI(title="Profit Pal OCR API")

# Variabilă globală pentru motor și eroare
ocr = None
init_error = None

try:
    logger.info("Se încarcă motorul PaddleOCR (mod simplificat)...")
    # Lăsăm setările implicite pentru a evita erorile de tip "Unknown argument"
    ocr = PaddleOCR()
    logger.info("Motorul a fost încărcat cu succes!")
except Exception as e:
    init_error = str(e)
    logger.error(f"Eroare la încărcarea motorului: {e}")
    ocr = None

@app.post("/ocr")
async def process_ocr(request: dict):
    if ocr is None:
        raise HTTPException(
            status_code=500, 
            detail=f"Motorul OCR nu este disponibil. Eroare inițializare: {init_error}"
        )
    
    # Suportă ambele variante de chei
    image_url = request.get("image") or request.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="Lipsește câmpul 'image' sau 'image_url'")
    
    try:
        # Descărcare imagine
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Nu s-a putut descărca imaginea")
            
        # Conversie pentru Paddle
        img = Image.open(io.BytesIO(response.content)).convert('RGB')
        img_np = np.array(img)
        
        # Infernță
        logger.info(f"Se procesează imaginea...")
        result = ocr.ocr(img_np, cls=True)
        
        # Formatare rezultat (simplificat pentru Profit Pal)
        final_text = []
        if result and result[0]:
            for line in result[0]:
                final_text.append({
                    "text": line[1][0],
                    "confidence": float(line[1][1]),
                    "bbox": line[0]
                })
        
        return {"result": final_text}
        
    except Exception as e:
        logger.error(f"Eroare procesare: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
