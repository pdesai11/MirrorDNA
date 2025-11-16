"""
REST API for MirrorDNA Protocol.

Provides HTTP/REST access to all MirrorDNA operations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, Depends, status, Query
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "REST API requires FastAPI and Pydantic. "
        "Install with: pip install 'mirrordna[api]' or pip install fastapi uvicorn pydantic"
    )

from .identity import IdentityManager
from .continuity import ContinuityTracker
from .memory import MemoryManager
from .state_snapshot import capture_snapshot, save_snapshot
from .timeline import Timeline
from .storage import JSONFileStorage
from .exceptions import MirrorDNAException
from .health import HealthChecker


# =================================================================
# Pydantic Models
# =================================================================

class IdentityCreate(BaseModel):
    """Request model for creating an identity."""
    identity_type: str = Field(..., description="Type of identity (user, agent, system)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class IdentityResponse(BaseModel):
    """Response model for identity."""
    identity_id: str
    identity_type: str
    created_at: str
    public_key: str
    metadata: Optional[Dict[str, Any]] = None


class SessionCreate(BaseModel):
    """Request model for creating a session."""
    identity_id: str
    parent_session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Response model for session."""
    session_id: str
    identity_id: str
    parent_session_id: Optional[str] = None
    created_at: str
    ended_at: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class MemoryWrite(BaseModel):
    """Request model for writing memory."""
    tier: str = Field(..., description="Memory tier (short_term, long_term, episodic)")
    content: str = Field(..., description="Memory content")
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    """Response model for memory."""
    memory_id: str
    tier: str
    content: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None
    access_count: int = 0


class SnapshotCreate(BaseModel):
    """Request model for creating snapshot."""
    identity_state: Dict[str, Any]
    continuity_state: Dict[str, Any]
    vault_state: Dict[str, Any]


class SnapshotResponse(BaseModel):
    """Response model for snapshot."""
    snapshot_id: str
    timestamp: str
    version: str
    checksum: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    checks: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    details: Optional[Dict[str, Any]] = None


# =================================================================
# FastAPI Application
# =================================================================

def create_app(
    storage_dir: Optional[Path] = None,
    enable_cors: bool = True,
    cors_origins: List[str] = ["*"]
) -> FastAPI:
    """
    Create FastAPI application.

    Args:
        storage_dir: Storage directory for data
        enable_cors: Enable CORS middleware
        cors_origins: Allowed CORS origins

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="MirrorDNA Protocol API",
        description="REST API for MirrorDNA identity and continuity protocol",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # Add CORS middleware
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Initialize storage
    storage = JSONFileStorage(storage_dir) if storage_dir else JSONFileStorage()

    # Dependencies
    def get_identity_manager():
        return IdentityManager(storage=storage)

    def get_continuity_tracker():
        return ContinuityTracker(storage=storage)

    def get_memory_manager(identity_id: str):
        return MemoryManager(storage=storage, identity_id=identity_id)

    # =================================================================
    # Identity Endpoints
    # =================================================================

    @app.post("/api/v1/identities", response_model=IdentityResponse, status_code=status.HTTP_201_CREATED)
    async def create_identity(
        identity_data: IdentityCreate,
        manager: IdentityManager = Depends(get_identity_manager)
    ):
        """Create a new identity."""
        try:
            identity = manager.create_identity(
                identity_type=identity_data.identity_type,
                metadata=identity_data.metadata
            )

            # Remove private key from response
            identity.pop("_private_key", None)

            return IdentityResponse(**identity)

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/identities/{identity_id}", response_model=IdentityResponse)
    async def get_identity(
        identity_id: str,
        manager: IdentityManager = Depends(get_identity_manager)
    ):
        """Get identity by ID."""
        identity = manager.get_identity(identity_id)

        if not identity:
            raise HTTPException(status_code=404, detail=f"Identity not found: {identity_id}")

        return IdentityResponse(**identity)

    # =================================================================
    # Session Endpoints
    # =================================================================

    @app.post("/api/v1/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
    async def create_session(
        session_data: SessionCreate,
        tracker: ContinuityTracker = Depends(get_continuity_tracker)
    ):
        """Create a new session."""
        try:
            session = tracker.create_session(
                identity_id=session_data.identity_id,
                parent_session_id=session_data.parent_session_id,
                context=session_data.context
            )

            return SessionResponse(**session)

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
    async def get_session(
        session_id: str,
        tracker: ContinuityTracker = Depends(get_continuity_tracker)
    ):
        """Get session by ID."""
        session = tracker.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

        return SessionResponse(**session)

    @app.post("/api/v1/sessions/{session_id}/end")
    async def end_session(
        session_id: str,
        tracker: ContinuityTracker = Depends(get_continuity_tracker)
    ):
        """End a session."""
        try:
            tracker.end_session(session_id)
            return {"status": "ended", "session_id": session_id}

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/sessions/{session_id}/lineage", response_model=List[SessionResponse])
    async def get_session_lineage(
        session_id: str,
        tracker: ContinuityTracker = Depends(get_continuity_tracker)
    ):
        """Get session lineage."""
        lineage = tracker.get_session_lineage(session_id)
        return [SessionResponse(**session) for session in lineage]

    # =================================================================
    # Memory Endpoints
    # =================================================================

    @app.post("/api/v1/memories", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
    async def write_memory(
        memory_data: MemoryWrite,
        identity_id: str = Query(..., description="Identity ID"),
    ):
        """Write a memory."""
        try:
            manager = get_memory_manager(identity_id)

            memory = manager.write_memory(
                tier=memory_data.tier,
                content=memory_data.content,
                metadata=memory_data.metadata
            )

            return MemoryResponse(**memory)

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/memories", response_model=List[MemoryResponse])
    async def read_memories(
        identity_id: str = Query(..., description="Identity ID"),
        tier: Optional[str] = Query(None, description="Memory tier"),
        limit: int = Query(100, description="Max results")
    ):
        """Read memories."""
        try:
            manager = get_memory_manager(identity_id)

            memories = manager.read_memory(tier=tier, limit=limit)
            return [MemoryResponse(**m) for m in memories]

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/memories/search", response_model=List[MemoryResponse])
    async def search_memories(
        identity_id: str = Query(..., description="Identity ID"),
        query: str = Query(..., description="Search query"),
        tier: Optional[str] = Query(None, description="Memory tier"),
        limit: int = Query(100, description="Max results")
    ):
        """Search memories."""
        try:
            manager = get_memory_manager(identity_id)

            results = manager.search_memory(query=query, tier=tier, limit=limit)
            return [MemoryResponse(**m) for m in results]

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    # =================================================================
    # Snapshot Endpoints
    # =================================================================

    @app.post("/api/v1/snapshots", response_model=SnapshotResponse, status_code=status.HTTP_201_CREATED)
    async def create_snapshot(snapshot_data: SnapshotCreate):
        """Create a state snapshot."""
        try:
            snapshot = capture_snapshot(
                identity_state=snapshot_data.identity_state,
                continuity_state=snapshot_data.continuity_state,
                vault_state=snapshot_data.vault_state
            )

            return SnapshotResponse(
                snapshot_id=snapshot.snapshot_id,
                timestamp=snapshot.timestamp,
                version=snapshot.version,
                checksum=snapshot.checksum
            )

        except MirrorDNAException as e:
            raise HTTPException(status_code=400, detail=str(e))

    # =================================================================
    # Timeline Endpoints
    # =================================================================

    @app.get("/api/v1/timeline")
    async def get_timeline_events(
        event_type: Optional[str] = Query(None, description="Filter by event type"),
        actor: Optional[str] = Query(None, description="Filter by actor"),
        limit: int = Query(100, description="Max results")
    ):
        """Get timeline events."""
        try:
            timeline = Timeline()

            events = timeline.export_events()

            # Apply filters
            if event_type:
                events = [e for e in events if e.get("event_type") == event_type]

            if actor:
                events = [e for e in events if e.get("actor") == actor]

            # Apply limit
            events = events[:limit]

            return {"events": events, "count": len(events)}

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # =================================================================
    # Health Check Endpoint
    # =================================================================

    @app.get("/api/v1/health", response_model=HealthResponse)
    async def health_check():
        """Perform health check."""
        try:
            checker = HealthChecker()
            checker.run_all_checks()
            summary = checker.get_summary()

            return HealthResponse(
                status=summary["overall_status"],
                timestamp=summary["timestamp"],
                checks=summary["checks"]
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =================================================================
    # Root Endpoint
    # =================================================================

    @app.get("/")
    async def root():
        """API root endpoint."""
        return {
            "name": "MirrorDNA Protocol API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "health": "/api/v1/health"
        }

    return app


# =================================================================
# CLI Server Runner
# =================================================================

def serve(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    storage_dir: Optional[Path] = None
):
    """
    Run the API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        storage_dir: Storage directory
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError(
            "API server requires uvicorn. "
            "Install with: pip install uvicorn"
        )

    app = create_app(storage_dir=storage_dir)

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )
