from fastapi import Request

async def security_headers_middleware(request: Request, call_next):
    """
    Middleware para inyectar headers de seguridad robustos en todas las respuestas.
    Previene Clickjacking, XSS, MIME-sniffing, etc.
    """
    response = await call_next(request)
    
    # Headers de seguridad
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy (CSP) diferenciado para APIs y Frontend
    if request.url.path.startswith("/api/"):
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; object-src 'none';"
    else:
        # Permitir fuentes de Google, SDK de inicio de sesión de Google e inline scripts/estilos para el frontend
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://accounts.google.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "frame-src 'self' https://accounts.google.com; "
            "connect-src 'self' http://localhost:3000 http://127.0.0.1:3000; "
            "object-src 'none';"
        )
    
    # Ocultar la tecnología del backend por seguridad
    response.headers["Server"] = "Flymetrics-Secure-API"
    if "x-powered-by" in response.headers:
        del response.headers["x-powered-by"]
        
    return response
