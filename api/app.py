from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import platform

# Import win32print only on Windows
if platform.system() == "Windows":
    import win32print
else:
    win32print = None  # type: ignore

app = FastAPI(title="Dummy CRUD API with Printer", version="0.3.0")

# ----------------------
# CORS CONFIGURATION
# ----------------------
# WARNING: allow_origins=["*"] is convenient for testing but you should restrict
# it to trusted domains in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://tu-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ------------------------------------------
# CRUD EXAMPLE
# ------------------------------------------

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

fake_db: Dict[int, Item] = {}


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: Item):
    if item.id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item.id] = item
    return item


@app.get("/items", response_model=List[Item])
async def read_items():
    return list(fake_db.values())


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id != item.id:
        raise HTTPException(status_code=400, detail="ID mismatch between path and body")
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    fake_db[item_id] = item
    return item


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[item_id]

# ------------------------------------------
# PRINTING LOGIC
# ------------------------------------------

class PrintRequest(BaseModel):
    seccion: str
    orden: str
    precio: str
    tipo: str
    fila: str
    asiento: str
    printer_name: Optional[str] = "BP500"


def _adaptar_codigo(codigo_original: str) -> str:
    lineas = codigo_original.strip().split("\n")
    return "".join(f"{ln.strip()}\r\n" for ln in lineas if ln.strip())


def _build_ticket(pr: PrintRequest) -> str:
    return f"""
^Q140,0,0
^W57
^H5
^P1
^S2
^AD
^C1
^R0
~Q+0
^O0
^D0
^E12
~R255
^XSET,ROTATION,0
^L
Dy2-me-dd
Th:m:s
Y192,464,WindowText25-14
Y46,286,WindowText22-5
Y143,315,WindowText20-33
Y210,264,WindowText18-68
Y267,335,WindowText16-10
Y334,269,WindowText14-76
Y69,466,WindowText12-94
Y166,489,WindowText11-37
Y45,934,WindowText10-2
Y142,963,WindowText9-96
Y209,912,WindowText8-9
Y266,983,WindowText7-8
Y333,917,WindowText6-7
W213,212,5,2,M,8,5,55,3
https://eventonist.com/checkin/?id=MTMzNS0xMzIxLTUxN1Qw
VD,67,376,1,1,0,3E,{pr.precio}
VD,169,396,1,1,0,3E,{pr.orden}
VD,234,397,1,1,0,3E,{pr.seccion}
VD,291,397,1,1,0,3E,{pr.fila}
VD,358,397,1,1,0,3E,{pr.asiento}
VD,66,1024,1,1,0,3E,{pr.precio}
VD,168,1044,1,1,0,3E,{pr.orden}
VD,233,1045,1,1,0,3E,{pr.seccion}
VD,290,1045,1,1,0,3E,{pr.fila}
VD,357,1045,1,1,0,3E,{pr.asiento}
Lo,4,864,452,875
E
"""


def _send_to_printer(raw_code: str, printer_name: str):
    if win32print is None:
        raise RuntimeError("win32print solo está disponible en Windows")
    data_bytes = _adaptar_codigo(raw_code).encode("ascii", errors="ignore")
    handle = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(handle, 1, ("Etiqueta", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, data_bytes)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
    finally:
        win32print.ClosePrinter(handle)


@app.post("/print")
async def print_ticket(req: PrintRequest):
    try:
        raw = _build_ticket(req)
        _send_to_printer(raw, req.printer_name)
        return {"status": "ok", "message": "Ticket enviado"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al imprimir: {e}")

# -------------
# UVICORN ENTRY
# -------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)