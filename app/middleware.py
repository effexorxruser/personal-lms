from fastapi import FastAPI


def configure_middleware(app: FastAPI) -> None:
    # Phase 1 has no custom middleware yet; keep the hook explicit for later phases.
    return None
