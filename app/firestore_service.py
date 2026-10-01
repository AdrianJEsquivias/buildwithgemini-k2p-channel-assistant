"""Firestore client and data layer for K2P Channel Assistant.
Hardcodes the GCP project ID string to avoid project number issues on Agent Platform.
"""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-02df96e1c54a"
COLLECTION_NAME = "k2p_channels"


def get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def list_k2p_channels(subfamily: Optional[str] = None) -> List[Dict[str, Any]]:
    """List K2P channels from Firestore, optionally filtered by subfamily."""
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)
    if subfamily:
        query = query.where("subfamily", "==", subfamily)
    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_k2p_channel(channel_name: str) -> Optional[Dict[str, Any]]:
    """Get a K2P channel document by channel name (e.g., 'TREK-1', 'TASK-3')."""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(channel_name.upper())
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    # Fallback to query by name case-insensitively or gene_symbol
    query = db.collection(COLLECTION_NAME).where("name", "==", channel_name.upper()).limit(1).stream()
    for doc in query:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def save_k2p_channel(
    channel_name: str,
    gene_symbol: str,
    subfamily: str,
    gating_triggers: List[str],
    pharmacology: Dict[str, List[str]],
    summary: str,
    key_references: List[str]
) -> Dict[str, Any]:
    """Create or update a K2P channel document in Firestore."""
    db = get_firestore_client()
    doc_id = channel_name.upper()
    doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
    payload = {
        "name": channel_name.upper(),
        "gene_symbol": gene_symbol,
        "subfamily": subfamily,
        "gating_triggers": gating_triggers,
        "pharmacology": pharmacology,
        "summary": summary,
        "key_references": key_references,
    }
    doc_ref.set(payload, merge=True)
    payload["id"] = doc_id
    return payload
