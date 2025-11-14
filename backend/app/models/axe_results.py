"""
Data models for axe-core results
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AxeCoreResult(BaseModel):
    """Model for axe-core scan results"""
    violations: List[Dict[str, Any]] = []
    incomplete: List[Dict[str, Any]] = []
    passes: List[Dict[str, Any]] = []
    url: Optional[str] = None

