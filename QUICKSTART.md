# 🚀 INICIO RÁPIDO - Clinical Assistant

## Para empezar AHORA MISMO:

### Opción 1: Docker (Recomendado) 🐳

```bash
# 1. Crear archivo .env con tu token de HuggingFace
echo "HF_TOKEN=tu_token_aqui" > .env

# 2. Iniciar (descarga, construye e inicia todo)
docker-compose up --build

# 3. Abrir navegador
http://localhost:8000
```

**¡Listo!** La aplicación estará corriendo en http://localhost:8000

---

### Opción 2: Local (Desarrollo) 💻

```bash
# 1. Ejecutar script de inicio
./start.sh

# 2. Abrir navegador
http://localhost:8000
```

El script se encarga de:
- ✅ Crear virtualenv
- ✅ Instalar dependencias
- ✅ Iniciar la aplicación

---

## 📝 Notas Importantes

### Primera Vez
- La primera petición tarda **30-60 segundos** (carga modelos)
- Las siguientes son **mucho más rápidas** (5-10 segundos)

### Requisitos Mínimos
- Python 3.11+ (para local)
- Docker (para Docker)
- 8GB RAM mínimo
- Token de HuggingFace

### Token de HuggingFace
1. Ir a https://huggingface.co/settings/tokens
2. Crear nuevo token (lectura)
3. Aceptar licencia de Llama 3.2
4. Añadir a `.env`

---

## 🔧 Comandos Útiles

### Docker
```bash
# Iniciar
docker-compose up

# Detener
docker-compose down

# Ver logs
docker-compose logs -f

# Reconstruir
docker-compose up --build
```

### Local
```bash
# Iniciar
./start.sh

# O manualmente:
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📚 Más Información

- **README completo**: `README.md`
- **Documentación técnica**: `docs/`
- **API Docs**: http://localhost:8000/docs

---

## ❓ Problemas Comunes

### "Models not found"
→ Verifica que existan:
- `backend/models/classifier/`
- `backend/models/t5_summarizer/`
- `backend/models/llama_peft/`

### "HF_TOKEN not set"
→ Crea archivo `.env`:
```bash
echo "HF_TOKEN=hf_tu_token" > .env
```

### Puerto 8000 ocupado
→ Cambia el puerto:
```bash
uvicorn app.main:app --port 8001
```

---

**¡Eso es todo! El proyecto está listo para usar.** 🎉
