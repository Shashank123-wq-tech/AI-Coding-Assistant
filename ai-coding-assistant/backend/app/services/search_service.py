from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk


class SearchService:
    """
    Search indexed repository code using PostgreSQL
    text matching.
    """

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        repository_id: int,
        query: str,
        limit: int = 10,
    ) -> list[dict]:

        query = query.strip()

        if not query:
            return []

        search_pattern = f"%{query}%"

        chunks = (
            self.db.query(CodeChunk)
            .filter(
                CodeChunk.repository_id == repository_id,
                or_(
                    CodeChunk.content.ilike(search_pattern),
                    CodeChunk.file_path.ilike(search_pattern),
                ),
            )
            .all()
        )
        query_lower = query.lower()
        
        scored_results = []
        
        for chunk in chunks:
            content_lower = chunk.content.lower()
            file_path_lower = chunk.file_path.lower()
            
            score = 0
            
            # Exact phrase in content 
            if query_lower in content_lower:
                score += 10
            
            # Exact phrase in file path
            if query_lower in file_path_lower:   
                score += 5
            
            occurence_count = content_lower.count(
                query_lower
            )    
            
            score += occurence_count 
            
            scored_results.append(
                (
                    score,
                    chunk
                )
            )
        
        scored_results.sort(
            key = lambda item: item[0],
            reverse = True
        ) 
        
        scored_results = scored_results[:limit]   
                 

        return [
            {
                "chunk_id": chunk.chunk_id,
                "file_path": chunk.file_path,
                "chunk_type": chunk.chunk_type,
                "language": chunk.language,
                "cell_index": chunk.cell_index,
                "content": chunk.content,
                "metadata": chunk.chunk_metadata,
                "score": score
            }
            for score ,chunk in scored_results
        ]