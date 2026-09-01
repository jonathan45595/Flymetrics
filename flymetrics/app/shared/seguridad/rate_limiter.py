from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

# Inicializar el limitador (usa la IP del cliente por defecto)
# Limite global por defecto: 100 peticiones por minuto por IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def setup_rate_limiter(app: FastAPI):
    """
    Configura el manejador de excepciones global para Rate Limiting
    y asocia el limitador a la aplicación.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
