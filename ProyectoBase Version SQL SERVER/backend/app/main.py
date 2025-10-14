from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth, clientes, cuentas, tarjetas, transacciones, cajeros, cajero, retiros_sin_tarjeta, retiros_con_tarjeta
from app.database import engine, Base
import os

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema Bancario Pichincha",
    description="API para el Sistema Bancario del Banco Pichincha",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["autenticación"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["clientes"])
app.include_router(cuentas.router, prefix="/api/cuentas", tags=["cuentas"])
app.include_router(tarjetas.router, prefix="/api/tarjetas", tags=["tarjetas"])
app.include_router(cajero.router, prefix="/api/cajero", tags=["cajero"])  # Endpoints del cajero ATM
app.include_router(retiros_sin_tarjeta.router, tags=["retiros-sin-tarjeta"])
app.include_router(retiros_con_tarjeta.router, tags=["retiros-con-tarjeta"])
app.include_router(transacciones.router, prefix="/api/transacciones", tags=["transacciones"])
app.include_router(cajeros.router, prefix="/api/cajeros", tags=["cajeros"])

# Servir archivos estáticos del frontend
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al Sistema Bancario Pichincha",
        "version": "1.0.0",
        "documentacion": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "banco": "Pichincha"}
