import os
from datetime import datetime
from google.cloud import firestore
from typing import List, Dict, Any

class FirestoreChatManager:
    def __init__(self, collection_name="chat_sessions"):
        """Initialize Firestore chat manager."""
        self.db = firestore.Client()
        self.collection_name = collection_name
        self.collection = self.db.collection(collection_name)
    
    def create_chat_session(self, user_id: str = None) -> str:
        """Create a new chat session and return the session ID."""
        session_data = {
            "user_id": user_id or "anonymous",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0
        }
        doc_ref = self.collection.add(session_data)[1]
        return doc_ref.id
    
    def add_message(self, session_id: str, role: str, content: str, sources: List[Dict] = None):
        """Add a message to a chat session."""
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "sources": sources or []
        }
        
        # Add message to subcollection
        self.collection.document(session_id).collection("messages").add(message_data)
        
        # Update session metadata
        session_ref = self.collection.document(session_id)
        session_ref.update({
            "updated_at": datetime.utcnow(),
            "message_count": firestore.Increment(1)
        })
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages from a chat session."""
        messages = []
        messages_ref = self.collection.document(session_id).collection("messages")
        
        for doc in messages_ref.order_by("timestamp").stream():
            message_data = doc.to_dict()
            message_data["id"] = doc.id
            messages.append(message_data)
        
        return messages
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        sessions = []
        query = self.collection.where("user_id", "==", user_id).order_by("updated_at", direction=firestore.Query.DESCENDING)
        
        for doc in query.stream():
            session_data = doc.to_dict()
            session_data["id"] = doc.id
            sessions.append(session_data)
        
        return sessions
    
    def delete_session(self, session_id: str):
        """Delete a chat session and all its messages."""
        # Delete all messages in the session
        messages_ref = self.collection.document(session_id).collection("messages")
        for doc in messages_ref.stream():
            doc.reference.delete()
        
        # Delete the session document
        self.collection.document(session_id).delete()
    
    def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]):
        """Update session metadata."""
        self.collection.document(session_id).update({
            **metadata,
            "updated_at": datetime.utcnow()
        }) 