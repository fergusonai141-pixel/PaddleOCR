import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from paddleocr import PaddleOCR
import paddle
import httpx
import io
from PIL import Image
import numpy as np

# 1. Configurare Stabilitate Paddle (trebuie făcute înainte de inițializare)
os.environ["FLAGS_use_onednn"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr-api")

app = FastAPI(title="Profit Pal OCR API")

# 2. Inițializare Motor (Versiunea Stabilă 2.7)
# Se face o singură dată la pornire pentru viteză
try:
    logger.info("Se încarcă motorul PaddleOCR...")
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
    logger.info("Motorul a fost încărcat cu succes!")
except Exception as e:
    logger.error(f"Eroare la încărcarea motorului: {e}")
    ocr = None

class OCRRequest(BaseModel):
    image_url: str

@app.get("/health")
async def health():
    return {"status": "up", "engine": "PaddleOCR 2.7"}

@app.post("/ocr")
async def process_ocr(request: OCRRequest):
    if ocr is None:
        raise HTTPException(status_code=500, detail="Motorul OCR nu este disponibil")
    
    try:
        # Descărcare imagine
        async with httpx.AsyncClient() as client:
            response = await client.get(request.image_url, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Nu s-a putut descărca imaginea")
            
        # Conversie pentru Paddle
        img = Image.open(io.BytesIO(response.content)).convert('RGB')
        img_np = np.array(img)
        
        # Infernță
        logger.info(f"Se procesează imaginea de la {request.image_url[:50]}...")
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
