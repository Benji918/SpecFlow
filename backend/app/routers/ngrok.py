from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pyngrok import ngrok, conf
from app.config import settings
import logging

logger = logging.getLogger("uvicorn")

# Configure ngrok with auth token on module load
if settings.NGROK_AUTH_TOKEN:
    conf.get_default().auth_token = settings.NGROK_AUTH_TOKEN

router = APIRouter(prefix="/api/ngrok", tags=["ngrok"])

from pydantic import BaseModel

class TunnelRequest(BaseModel):
    local_port: int = 8000
    protocol: str = "http"

@router.post("/create-tunnel")
async def create_ngrok_tunnel(request: TunnelRequest):
    """
    Create a new ngrok tunnel to a local server.
    """
    if not settings.NGROK_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ngrok is disabled in backend configuration. Please set NGROK_ENABLED=True in your .env file."
        )

    try:
        # Check for existing tunnels first
        tunnels = ngrok.get_tunnels()
        
        if tunnels:
            tunnel = tunnels[0]
            print(tunnel)
            return JSONResponse({
                "success": True,
                "public_url": tunnel.public_url,
                "local_port": tunnel.config.get('addr'),
                "protocol": tunnel.proto,
                "region": settings.NGROK_REGION,
                "tunnel": {
                    "name": tunnel.name,
                    "public_url": tunnel.public_url,
                    "proto": tunnel.proto,
                    "addr": tunnel.config.get('addr'),
                    "region": settings.NGROK_REGION
                },
                "message": "Reusing existing tunnel"
            })

        # Create tunnel
        tunnel = ngrok.connect(
            addr=request.local_port,
            proto=request.protocol
        )

        # Get tunnel details
        tunnel_info = {
            "name": tunnel.name,
            "public_url": tunnel.public_url,
            "proto": tunnel.proto,
            "addr": tunnel.config.get('addr'),
            "region": settings.NGROK_REGION
        }

        return JSONResponse({
            "success": True,
            "public_url": tunnel.public_url,
            "local_port": request.local_port,
            "protocol": request.protocol,
            "region": settings.NGROK_REGION,
            "tunnel": tunnel_info
        })

    except Exception as e:
        error_msg = str(e)
        if "ERR_NGROK_108" in error_msg or "simultaneous ngrok agent sessions" in error_msg:
            # Try to kill existing processes and suggest retry
            logger.info("Session limit reached, attempting to kill dangling ngrok processes...")
            ngrok.kill()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Ngrok session limit reached (ERR_NGROK_108). This often happens when the server reloads. I've attempted to reset the connection. Please wait 5 seconds and try again."
            )
        elif "authentication failed" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ngrok authentication failed. Please check your auth token in the backend .env file."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ngrok tunnel: {error_msg}"
        )


@router.get("/tunnels")
async def list_ngrok_tunnels():
    """
    List all active ngrok tunnels.
    
    Returns:
        List of active tunnels
    """
    try:
        if not settings.NGROK_ENABLED:
            return JSONResponse({
                "success": True, 
                "tunnels": [],
                "message": "Ngrok is disabled in configuration"
            })

        tunnels = ngrok.get_tunnels()
        
        return JSONResponse({
            "success": True,
            "tunnels": [
                {
                    "name": tunnel.name,
                    "public_url": tunnel.public_url,
                    "proto": tunnel.proto,
                    "addr": tunnel.config.get('addr'),
                    "region": settings.NGROK_REGION
                }
                for tunnel in tunnels
            ]
        })

    except Exception as e:
        error_msg = str(e)
        if "ERR_NGROK_108" in error_msg or "simultaneous ngrok agent sessions" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Ngrok session limit reached. You can only have 1 tunnel active on the free plan. Please close any existing tunnels first or upgrade to a paid plan."
            )
        elif "authentication failed" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ngrok authentication failed. Please check your auth token in the backend .env file."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list ngrok tunnels: {error_msg}"
        )


@router.delete("/tunnels")
async def close_all_ngrok_tunnels():
    """
    Close all active ngrok tunnels.
    
    Returns:
        Status of the operation
    """
    try:
        # Force kill all ngrok processes instead of just closing tunnels
        from pyngrok import ngrok as ngrok_process
        ngrok_process.kill()
        
        return JSONResponse({
            "success": True,
            "message": "All ngrok tunnels closed and processes killed"
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close ngrok tunnels: {str(e)}"
        )


@router.delete("/tunnels/{tunnel_name}")
async def close_ngrok_tunnel(tunnel_name: str):
    """
    Close a specific ngrok tunnel.
    
    Args:
        tunnel_name: Name of the tunnel to close
        
    Returns:
        Status of the operation
    """
    try:
        tunnels = ngrok.get_tunnels()
        
        for tunnel in tunnels:
            if tunnel.name == tunnel_name or tunnel.public_url == tunnel_name:
                ngrok.disconnect(tunnel.public_url)
                return JSONResponse({
                    "success": True,
                    "message": f"Tunnel {tunnel_name} closed"
                })

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tunnel {tunnel_name} not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close ngrok tunnel: {str(e)}"
        )
