"""Session-based personalization for recommendations."""

from __future__ import annotations

import streamlit as st


def init_session():
    defaults = {
        "liked_paths": [],
        "disliked_paths": [],
        "style_embedding": None,
        "chat_history": [],
        "search_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value if not isinstance(value, list) else list(value)


def record_like(path: str, embedding: list[float] | None):
    if path not in st.session_state.liked_paths:
        st.session_state.liked_paths.append(path)
    if path in st.session_state.disliked_paths:
        st.session_state.disliked_paths.remove(path)
    if embedding is not None:
        _update_style_embedding(embedding, weight=0.25)


def record_dislike(path: str):
    if path not in st.session_state.disliked_paths:
        st.session_state.disliked_paths.append(path)
    if path in st.session_state.liked_paths:
        st.session_state.liked_paths.remove(path)


def _update_style_embedding(embedding: list[float], weight: float = 0.25):
    import numpy as np

    vec = np.array(embedding, dtype=np.float32)
    if st.session_state.style_embedding is None:
        st.session_state.style_embedding = vec.tolist()
        return
    current = np.array(st.session_state.style_embedding, dtype=np.float32)
    blended = (1 - weight) * current + weight * vec
    blended = blended / (np.linalg.norm(blended) + 1e-8)
    st.session_state.style_embedding = blended.tolist()


def blend_with_profile(query_embedding: list[float], alpha: float = 0.75) -> list[float]:
    import numpy as np

    query = np.array(query_embedding, dtype=np.float32)
    profile = st.session_state.style_embedding
    if profile is None:
        return query_embedding
    profile_vec = np.array(profile, dtype=np.float32)
    mixed = alpha * query + (1 - alpha) * profile_vec
    mixed = mixed / (np.linalg.norm(mixed) + 1e-8)
    return mixed.tolist()


def filter_disliked(paths: list[str]) -> list[str]:
    disliked = set(st.session_state.disliked_paths)
    return [p for p in paths if p not in disliked]
