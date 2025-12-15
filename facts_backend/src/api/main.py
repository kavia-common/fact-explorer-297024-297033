from typing import Dict, List, Optional
import random
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# App metadata and tags for OpenAPI
app = FastAPI(
    title="Facts API",
    description="Serve random facts and manage user favorites. Provides endpoints for random fact retrieval and favorites management.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Health and diagnostics"},
        {"name": "facts", "description": "Random facts retrieval"},
        {"name": "favorites", "description": "Manage favorites for users"},
    ],
)

# Allow frontend on 3000 and generic use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for demo purposes only
FACTS: List[str] = [
    "Bananas are berries, but strawberries aren't.",
    "Honey never spoils; archaeologists have tasted 3,000-year-old honey.",
    "Octopuses have three hearts.",
    "A day on Venus is longer than a year on Venus.",
    "There are more stars in the universe than grains of sand on Earth.",
    "Your nose and ears never stop growing.",
    "Wombat poop is cube-shaped.",
    "Cows have best friends and get stressed when separated.",
    "The Eiffel Tower can be 15 cm taller during summer.",
    "Sharks existed before trees.",
]

# In-memory map: user_id -> list of favorite facts (strings)
USER_FAVORITES: Dict[str, List[str]] = {}


class Fact(BaseModel):
    """Pydantic model representing a single fact string with id-like key."""
    text: str = Field(..., description="The textual content of the fact")


class FavoriteRequest(BaseModel):
    """Payload to add/remove a favorite fact."""
    text: str = Field(..., description="The fact text to save as a favorite")


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Health check endpoint.
    Returns:
        dict: A simple status indicating the service is healthy.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/facts/random",
    response_model=Fact,
    tags=["facts"],
    summary="Get a random fact",
    description="Returns a single random fact. The pool is static in-memory for this demo."
)
def get_random_fact(seed: Optional[int] = Query(default=None, description="Optional seed for deterministic result during tests.")) -> Fact:
    """Return a random fact from the in-memory list.
    Args:
        seed (Optional[int]): Optional deterministic seed (useful for tests).
    Returns:
        Fact: Object with a random fact text.
    """
    if not FACTS:
        raise HTTPException(status_code=404, detail="No facts available")
    rnd = random.Random(seed) if seed is not None else random
    return Fact(text=rnd.choice(FACTS))


# Helpers
def _get_user_favorites(user_id: str) -> List[str]:
    """Internal: Get a user's favorites list, creating it if not present."""
    if user_id not in USER_FAVORITES:
        USER_FAVORITES[user_id] = []
    return USER_FAVORITES[user_id]


# PUBLIC_INTERFACE
@app.get(
    "/facts/favorites",
    tags=["favorites"],
    summary="List favorites for current user",
    description="Lists favorite facts for the current (demo) user using userId query or defaults to 'default'.",
)
def list_favorites(userId: Optional[str] = Query(default="default", description="User identifier. Defaults to 'default' if omitted.")) -> List[Fact]:
    """List favorite facts for a user."""
    favs = _get_user_favorites(userId)
    return [Fact(text=f) for f in favs]


# PUBLIC_INTERFACE
@app.post(
    "/facts/favorites",
    tags=["favorites"],
    summary="Add a favorite fact for current user",
    description="Adds a fact to favorites for the current (demo) user using userId query or defaults to 'default'.",
    response_model=Fact,
    responses={201: {"description": "Created"}},
)
def add_favorite(payload: FavoriteRequest, userId: Optional[str] = Query(default="default", description="User identifier. Defaults to 'default' if omitted.")):
    """Add a favorite fact for a user."""
    favs = _get_user_favorites(userId)
    if payload.text not in favs:
        favs.append(payload.text)
    return Fact(text=payload.text)


# PUBLIC_INTERFACE
@app.delete(
    "/facts/favorites",
    tags=["favorites"],
    summary="Remove a favorite fact for current user",
    description="Removes a fact from favorites for the current (demo) user using userId query or defaults to 'default'.",
)
def remove_favorite(text: str = Query(..., description="Exact fact text to remove"), userId: Optional[str] = Query(default="default", description="User identifier. Defaults to 'default' if omitted.")):
    """Remove a favorite fact for a user."""
    favs = _get_user_favorites(userId)
    try:
        favs.remove(text)
    except ValueError:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"removed": True, "text": text}


# PUBLIC_INTERFACE
@app.get(
    "/users/{user_id}/favorites",
    tags=["favorites"],
    summary="List favorites by user id",
    description="Alternative route to list favorites by explicit user id.",
)
def list_user_favorites(user_id: str = Path(..., description="User identifier path param")) -> List[Fact]:
    """List favorite facts for a specified user id."""
    favs = _get_user_favorites(user_id)
    return [Fact(text=f) for f in favs]
