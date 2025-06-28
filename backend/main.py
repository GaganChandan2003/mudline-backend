from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from app.config import settings
from app.database import engine, Base
from app.booking_routes import router as booking_router
from app.user_routes import router as user_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting MudlineX application")
    
    # Create database tables (in development)
    if settings.DEBUG:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MudlineX application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Complete truck booking and material transportation system",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all exceptions"""
    logger.error(
        "Unhandled exception occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


# TODO: Include API routers when they are created
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user_router, tags=["Users"])
# app.include_router(trucks.router, prefix="/api/v1/trucks", tags=["Trucks"])
app.include_router(booking_router)
# app.include_router(locations.router, prefix="/api/v1/locations", tags=["Locations"])
# app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
# app.include_router(ratings.router, prefix="/api/v1/ratings", tags=["Ratings"])
# app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 