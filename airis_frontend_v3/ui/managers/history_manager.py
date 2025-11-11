"""
History manager for the Airis application.
Handles storage, retrieval, and management of AI chat request history.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class HistoryEntry:
    """Represents a single history entry."""
    id: str
    timestamp: str
    query: str
    response: str
    query_type: str  # 'text', 'screenshot', 'image'
    status: str  # 'completed', 'error', 'processing'
    duration: float = 0.0
    tokens_used: int = 0

class HistoryManager:
    """Manages the history of AI chat requests and responses."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.history_file = self._get_history_file_path()
        self.history_entries: List[HistoryEntry] = []
        self.max_entries = 1000  # Maximum number of entries to store
        
        self.load_history()
    
    def _get_history_file_path(self) -> Path:
        """Gets the path to the history file."""
        # Create history directory in user's home folder
        home_dir = Path.home()
        airis_dir = home_dir / ".airis"
        airis_dir.mkdir(exist_ok=True)
        return airis_dir / "history.json"
    
    def add_entry(self, query: str, response: str, query_type: str, 
                  status: str = "completed", duration: float = 0.0, 
                  tokens_used: int = 0) -> str:
        """Adds a new entry to the history."""
        entry_id = self._generate_id()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = HistoryEntry(
            id=entry_id,
            timestamp=timestamp,
            query=query,
            response=response,
            query_type=query_type,
            status=status,
            duration=duration,
            tokens_used=tokens_used
        )
        
        self.history_entries.insert(0, entry)  # Add to beginning
        
        # Limit the number of entries
        if len(self.history_entries) > self.max_entries:
            self.history_entries = self.history_entries[:self.max_entries]
        
        self.save_history()
        return entry_id
    
    def update_entry(self, entry_id: str, **kwargs):
        """Updates an existing entry."""
        for entry in self.history_entries:
            if entry.id == entry_id:
                for key, value in kwargs.items():
                    if hasattr(entry, key):
                        setattr(entry, key, value)
                break
        self.save_history()
    
    def get_recent_entries(self, limit: int = 50) -> List[HistoryEntry]:
        """Gets the most recent entries."""
        return self.history_entries[:limit]
    
    def search_entries(self, query: str) -> List[HistoryEntry]:
        """Searches entries by query text."""
        query_lower = query.lower()
        return [
            entry for entry in self.history_entries
            if query_lower in entry.query.lower() or query_lower in entry.response.lower()
        ]
    
    def get_entries_by_type(self, query_type: str) -> List[HistoryEntry]:
        """Gets entries by query type."""
        return [entry for entry in self.history_entries if entry.query_type == query_type]
    
    def delete_entry(self, entry_id: str) -> bool:
        """Deletes an entry by ID."""
        for i, entry in enumerate(self.history_entries):
            if entry.id == entry_id:
                del self.history_entries[i]
                self.save_history()
                return True
        return False
    
    def clear_history(self):
        """Clears all history entries."""
        self.history_entries.clear()
        self.save_history()
    
    def load_history(self):
        """Loads history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history_entries = [
                        HistoryEntry(**entry) for entry in data.get('entries', [])
                    ]
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history_entries = []
    
    def save_history(self):
        """Saves history to file."""
        try:
            data = {
                'entries': [asdict(entry) for entry in self.history_entries],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gets usage statistics."""
        total_entries = len(self.history_entries)
        completed_entries = len([e for e in self.history_entries if e.status == "completed"])
        error_entries = len([e for e in self.history_entries if e.status == "error"])
        
        query_types = {}
        total_duration = 0
        total_tokens = 0
        
        for entry in self.history_entries:
            query_types[entry.query_type] = query_types.get(entry.query_type, 0) + 1
            total_duration += entry.duration
            total_tokens += entry.tokens_used
        
        return {
            'total_entries': total_entries,
            'completed_entries': completed_entries,
            'error_entries': error_entries,
            'query_types': query_types,
            'total_duration': total_duration,
            'total_tokens': total_tokens,
            'average_duration': total_duration / max(total_entries, 1)
        }
    
    def _generate_id(self) -> str:
        """Generates a unique ID for an entry."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def export_history(self, file_path: str) -> bool:
        """Exports history to a file."""
        try:
            data = {
                'exported_at': datetime.now().isoformat(),
                'total_entries': len(self.history_entries),
                'entries': [asdict(entry) for entry in self.history_entries]
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False