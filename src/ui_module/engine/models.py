from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

class Action(BaseModel):
    """
    Represents an action triggered by a user interaction.
    """
    id: str = Field(..., description="Unique identifier for the action type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Context data for the action")
    target: Optional[str] = Field(None, description="Target path or view ID if negotiation")

class Component(BaseModel):
    """
    Base model for all UI components.
    """
    type: str = Field(..., description="Component type (e.g., button, table, form)")
    id: Optional[str] = Field(None, description="Unique ID for the component instance")
    props: Dict[str, Any] = Field(default_factory=dict, description="Component-specific properties")
    children: Optional[List[Union["Component", str]]] = Field(None, description="Child components")
    actions: Optional[Dict[str, Action]] = Field(None, description="Map of event names to Actions")

class View(BaseModel):
    """
    Represents a full UI page/view.
    """
    id: str = Field(..., description="Unique identifier for the view")
    title: Optional[str] = Field(None, description="Page title")
    layout: Component = Field(..., description="Root component of the view")
    data: Dict[str, Any] = Field(default_factory=dict, description="Initial data for the view")

class Envelope(BaseModel):
    """
    Standard request envelope for all UI operations.
    """
    session_id: str
    user_id: Optional[str] = None
    device_context: Optional[str] = None
    theme_preference: Optional[str] = None

class SessionState(BaseModel):
    """
    Represents the transient state of a user session.
    """
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary session data")
    current_path: Optional[str] = None
