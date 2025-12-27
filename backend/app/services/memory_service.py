"""Long-term memory service using Mem0 for persistent fact storage"""
import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from mem0 import Memory

from app.config import get_settings

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Long-term memory service for storing and retrieving user facts/preferences.
    Uses Mem0 for intelligent memory management with vector search.
    """

    def __init__(self):
        """Initialize the memory service with Mem0"""
        settings = get_settings()
        
        # Configure vector store - use Qdrant Cloud if configured, else local
        if settings.qdrant_url and settings.qdrant_api_key:
            # Qdrant Cloud configuration (production)
            vector_store_config = {
                "provider": "qdrant",
                "config": {
                    "collection_name": "jarvis_memories",
                    "embedding_model_dims": 768,
                    "url": settings.qdrant_url,
                    "api_key": settings.qdrant_api_key,
                }
            }
            logger.info("Using Qdrant Cloud for memory storage")
        else:
            # Local Qdrant configuration (development)
            vector_store_config = {
                "provider": "qdrant",
                "config": {
                    "collection_name": "jarvis_memories",
                    "embedding_model_dims": 768,
                    "path": "./qdrant_data",
                }
            }
            logger.info("Using local Qdrant for memory storage")
        
        # Configure LLM and embedder - prefer OpenAI if available (more stable with Mem0)
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            # OpenAI configuration (most stable)
            llm_config = {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                }
            }
            embedder_config = {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                }
            }
            logger.info("Using OpenAI for Mem0 LLM/embedder")
        else:
            # Gemini configuration (fallback)
            llm_config = {
                "provider": "gemini",
                "config": {
                    "api_key": settings.gemini_api_key,
                    "model": "gemini-2.0-flash",
                }
            }
            embedder_config = {
                "provider": "gemini", 
                "config": {
                    "api_key": settings.gemini_api_key,
                    "model": "models/text-embedding-004",
                }
            }
            logger.info("Using Gemini for Mem0 LLM/embedder")
        
        # Build full config
        config = {
            "llm": llm_config,
            "embedder": embedder_config,
            "vector_store": vector_store_config,
            "version": "v1.1"
        }
        
        # In-memory cache for fast reads: {user_id: [memory_list]}
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        
        try:
            self.memory = Memory.from_config(config)
            logger.info("✓ Memory service initialized with Mem0")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            self.memory = None
    
    def load_user_memories(self, user_id: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Load all memories for a user into cache. Call on login for fast access.
        
        Args:
            user_id: User identifier
            force_refresh: If True, bypass cache and fetch from Qdrant
            
        Returns:
            List of user memories
        """
        if not force_refresh and user_id in self._cache:
            print(f"📦 CACHE HIT: {len(self._cache[user_id])} memories for user {user_id[:8]}...")
            logger.info(f"Cache hit for user {user_id}: {len(self._cache[user_id])} memories")
            return self._cache[user_id]
        
        # Fetch from Qdrant and cache
        memories = self._fetch_all_from_qdrant(user_id)
        self._cache[user_id] = memories
        print(f"🔄 CACHE LOADED: {len(memories)} memories from Qdrant for user {user_id[:8]}...")
        logger.info(f"Loaded {len(memories)} memories into cache for user {user_id}")
        return memories
    
    def _fetch_all_from_qdrant(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all memories directly from Qdrant (bypasses cache)"""
        if not self.memory:
            return []
        
        try:
            results = self.memory.get_all(user_id=user_id)
            if isinstance(results, dict) and 'results' in results:
                results = results['results']
            return results
        except Exception as e:
            logger.error(f"Failed to fetch from Qdrant: {e}")
            return []
    
    def _invalidate_cache(self, user_id: str):
        """Invalidate cache for a user after write operations"""
        if user_id in self._cache:
            del self._cache[user_id]
            print(f"❌ CACHE INVALIDATED for user {user_id[:8]}...")
            logger.info(f"Cache invalidated for user {user_id}")

    def add_memory(self, user_id: str, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Store a new memory for a user.
        
        Args:
            user_id: User identifier
            text: The fact/preference to remember
            metadata: Optional metadata (source, category, etc.)
            
        Returns:
            Result with memory ID and status
        """
        if not self.memory:
            return {"success": False, "error": "Memory service not initialized"}
        
        try:
            result = self.memory.add(
                text,
                user_id=user_id,
                metadata=metadata or {"source": "explicit"}
            )
            # Invalidate cache to force refresh on next read
            self._invalidate_cache(user_id)
            logger.info(f"✓ Added memory for user {user_id}: {text[:50]}...")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return {"success": False, "error": str(e)}

    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories using semantic search.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of relevant memories
        """
        if not self.memory:
            return []
        
        try:
            results = self.memory.search(
                query,
                user_id=user_id,
                limit=limit
            )
            # Mem0 may return {'results': [...]} or just a list
            if isinstance(results, dict) and 'results' in results:
                results = results['results']
            logger.info(f"Found {len(results)} memories for query: {query[:30]}...")
            return results
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a user (uses cache for fast access).
        
        Args:
            user_id: User identifier
            
        Returns:
            List of all memories
        """
        # Use cached version for faster reads
        return self.load_user_memories(user_id)

    def delete_memory(self, memory_id: str, user_id: str = None) -> bool:
        """
        Delete a specific memory by ID.
        
        Args:
            memory_id: The memory ID to delete
            user_id: Optional user ID for cache invalidation
            
        Returns:
            True if deleted successfully
        """
        if not self.memory:
            return False
        
        try:
            self.memory.delete(memory_id=memory_id)
            # Invalidate cache if user_id provided
            if user_id:
                self._invalidate_cache(user_id)
            logger.info(f"✓ Deleted memory {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False

    def delete_all_memories(self, user_id: str) -> bool:
        """
        Delete all memories for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted successfully
        """
        if not self.memory:
            return False
        
        try:
            self.memory.delete_all(user_id=user_id)
            # Invalidate cache
            self._invalidate_cache(user_id)
            logger.info(f"✓ Deleted all memories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete all memories: {e}")
            return False

    def get_relevant_context(self, user_id: str, query: str, limit: int = 3) -> str:
        """
        Get relevant memories as context string for AI responses.
        
        Args:
            user_id: User identifier
            query: The current conversation/query
            limit: Max memories to include
            
        Returns:
            Formatted context string
        """
        memories = self.search_memories(user_id, query, limit=limit)
        
        if not memories:
            return ""
        
        context_parts = ["Relevant things I remember about you:"]
        for mem in memories:
            memory_text = mem.get("memory", mem.get("text", ""))
            if memory_text:
                context_parts.append(f"- {memory_text}")
        
        return "\n".join(context_parts)
    
    def get_cached_context(self, user_id: str) -> str:
        """
        Get all cached memories as context string (fast, no Qdrant call if cached).
        
        Args:
            user_id: User identifier
            
        Returns:
            Formatted context string with all user memories
        """
        memories = self.load_user_memories(user_id)  # Uses cache
        
        if not memories:
            return ""
        
        context_parts = ["Things I remember about you (always use 'you/your' when mentioning these):"]
        for mem in memories:
            if isinstance(mem, dict):
                memory_text = mem.get("memory", mem.get("text", ""))
            else:
                memory_text = str(mem)
            if memory_text:
                context_parts.append(f"- {memory_text}")
        
        return "\n".join(context_parts)


# Singleton instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create the memory service singleton"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service


def preload_user_memories(user_id: str) -> int:
    """
    Preload memories for a user on login (only loads if not already cached).
    
    Args:
        user_id: User identifier
        
    Returns:
        Number of memories loaded
    """
    service = get_memory_service()
    # Don't force refresh - use cache if available for speed
    memories = service.load_user_memories(user_id, force_refresh=False)
    return len(memories)
