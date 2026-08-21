from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.services.signature_loader import load_signatures_from_yaml
from app.services.scan import (
    run_discovery_scan,
    ScanResult,
    run_environment_scan,
    EnvironmentScanResult,
)


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI Asset Discovery and Governance Platform",
    version="1.0.0"
)


# Allow React frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Check whether the signature registry loads successfully
signatures_loaded = False

try:
    load_signatures_from_yaml(settings.signatures_path)
    signatures_loaded = True

except Exception as e:
    print(f"Warning: Failed to load signatures: {e}")
    signatures_loaded = False


# Request model for POST /scan
class ScanRequest(BaseModel):
    application: str = Field(
        min_length=1,
        description="Name of the application being scanned"
    )

    root_dir: str = Field(
        min_length=1,
        description="Absolute or relative path of the application directory"
    )


# Request model for POST /environment-scan
class EnvironmentScanRequest(BaseModel):
    root_dir: str = Field(
        min_length=1,
        description="Absolute or relative path of the parent environment directory"
    )


@app.get("/")
def root():
    return {
        "message": "AI Asset Discovery Platform API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "signatures_loaded": signatures_loaded
    }


@app.post("/scan", response_model=ScanResult)
def scan_directory(request: ScanRequest):

    # Convert the provided directory into a Path object
    path = Path(request.root_dir)

    # Validate that the directory exists
    if not path.exists() or not path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Provided directory '{request.root_dir}' "
                "does not exist or is not a directory."
            )
        )

    try:
        # Run the complete AI asset discovery pipeline
        result = run_discovery_scan(
            application=request.application,
            root_dir=path
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing scan: {str(e)}"
        )


@app.post("/environment-scan", response_model=EnvironmentScanResult)
def scan_environment(request: EnvironmentScanRequest):

    # Convert the provided directory into a Path object
    path = Path(request.root_dir)

    # Validate that the directory exists
    if not path.exists() or not path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Provided directory '{request.root_dir}' "
                "does not exist or is not a directory."
            )
        )

    try:
        # Run the multi-application environment discovery pipeline
        result = run_environment_scan(root_dir=path)

        return result

    except FileNotFoundError as e:
        # No application subdirectories found under root_dir
        raise HTTPException(status_code=400, detail=str(e))

    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing environment scan: {str(e)}"
        )