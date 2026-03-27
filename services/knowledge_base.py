"""
Knowledge Base Service
RAG-based search and retrieval for customer support queries
"""
from pathlib import Path
import re
from typing import List, Dict, Tuple
from datetime import datetime


class KnowledgeBaseService:
    """Service for searching and retrieving information from knowledge base"""
    
    def __init__(self, kb_folder: str = "Knowledge_Base"):
        """Initialize knowledge base service"""
        self.kb_folder = Path(__file__).parent.parent / kb_folder
        self.kb_folder.mkdir(exist_ok=True)
        self.documents = {}
        self.load_documents()
    
    def load_documents(self):
        """Load all markdown documents from knowledge base"""
        self.documents = {}
        
        for md_file in self.kb_folder.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            doc_name = md_file.stem
            
            # Parse document into sections
            sections = self._parse_markdown_sections(content)
            self.documents[doc_name] = {
                'file': md_file,
                'sections': sections,
                'content': content
            }
    
    def _parse_markdown_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown content into sections"""
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        for line in content.split('\n'):
            # Check for headers
            if line.startswith('## '):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = line.replace('## ', '').strip()
                current_content = []
            elif line.startswith('# '):
                # Skip main title
                continue
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search knowledge base for relevant information
        
        Args:
            query: User's question/query
            top_k: Number of top results to return
        
        Returns:
            List of relevant sections with scores
        """
        query_lower = query.lower()
        query_keywords = self._extract_keywords(query_lower)
        
        results = []
        
        # Search through all documents
        for doc_name, doc_data in self.documents.items():
            # Search in sections (more specific than full document)
            for section_name, section_content in doc_data['sections'].items():
                section_score = self._calculate_relevance(
                    query_lower,
                    query_keywords,
                    section_content.lower()
                )
                
                if section_score > 0:
                    # Only return the relevant section, not full document
                    results.append({
                        'document': doc_name,
                        'section': section_name,
                        'content': section_content.strip(),
                        'score': section_score,
                        'file': str(doc_data['file'])
                    })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common words
        stop_words = {
            'what', 'is', 'are', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'how', 'when', 'where', 'why', 'who',
            'can', 'could', 'would', 'should', 'will', 'do', 'does', 'did',
            'have', 'has', 'had', 'be', 'been', 'being', 'i', 'you', 'we', 'they',
            'me', 'your', 'my', 'our', 'their', 'about', 'get', 'got', 'much',
            'many', 'some', 'any', 'this', 'that', 'these', 'those', 'am', 'is',
            'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'please',
            'help', 'tell', 'know', 'want', 'like', 'find', 'looking', 'info'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', query)
        
        # Filter stop words
        keywords = [word for word in words if word not in stop_words]
        
        return keywords
    
    def _calculate_relevance(self, query: str, keywords: List[str], content: str) -> float:
        """Calculate relevance score between query and content"""
        score = 0.0
        
        # Exact phrase match (highest score)
        if query in content:
            score += 10.0
        
        # Keyword matches with boosted scoring for specific terms
        for keyword in keywords:
            if keyword in content:
                # Count occurrences
                count = content.count(keyword)
                
                # Boost score for price/course related keywords
                if keyword in ['price', 'cost', 'much', 'fee', 'tuition']:
                    score += min(count * 3, 8)  # Higher boost for price queries
                elif keyword in ['course', 'training', 'batch', 'duration']:
                    score += min(count * 3, 8)  # Higher boost for course queries
                else:
                    score += min(count * 2, 5)  # Max 5 points per keyword
        
        # Section header boost
        for keyword in keywords:
            if f"## {keyword}" in content.lower() or f"# {keyword}" in content.lower():
                score += 3.0
        
        # Boost if content contains price patterns (e.g., $2,499)
        if any(kw in query for kw in ['much', 'price', 'cost']) and re.search(r'\$[\d,]+', content):
            score += 5.0
        
        return score
    
    def get_answer(self, query: str) -> Dict:
        """
        Get answer for a query from knowledge base
        
        Args:
            query: User's question
        
        Returns:
            Dictionary with answer and sources
        """
        # Search for relevant information
        results = self.search(query, top_k=3)
        
        if not results:
            return {
                'found': False,
                'answer': "I couldn't find specific information about this in our knowledge base. Let me connect you with a human support agent who can help.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Compile answer from top results
        answer_parts = []
        sources = []
        
        for i, result in enumerate(results, 1):
            if result['score'] >= 3.0:  # Only include high-confidence results
                answer_parts.append(f"From {result['document']} ({result['section']}):\n{result['content'][:500]}")
                sources.append(f"{result['document']} - {result['section']}")
        
        if not answer_parts:
            return {
                'found': False,
                'answer': "I found some related information but I'm not entirely sure. Let me connect you with a human support agent for accurate assistance.",
                'sources': [],
                'confidence': 0.3
            }
        
        # Calculate confidence
        confidence = min(results[0]['score'] / 10.0, 1.0)
        
        return {
            'found': True,
            'answer': '\n\n'.join(answer_parts),
            'sources': sources,
            'confidence': confidence,
            'top_result': results[0]
        }
    
    def classify_query(self, query: str) -> Dict:
        """
        Classify query type
        
        Args:
            query: User's question
        
        Returns:
            Dictionary with classification
        """
        query_lower = query.lower()
        
        # Support ticket keywords (issues, problems)
        support_keywords = [
            'not working', 'broken', 'error', 'issue', 'problem', 'bug',
            'complaint', 'refund', 'cancel', 'angry', 'upset', 'disappointed',
            'urgent', 'asap', 'emergency', 'critical', 'failed', 'wrong'
        ]
        
        # General inquiry keywords (information seeking)
        inquiry_keywords = [
            'what is', 'tell me about', 'information', 'where is', 'when is',
            'how much', 'price', 'cost', 'hours', 'location', 'contact',
            'course', 'training', 'product', 'service', 'offer', 'discount'
        ]
        
        # Check for support issues
        support_score = sum(1 for keyword in support_keywords if keyword in query_lower)
        
        # Check for general inquiries
        inquiry_score = sum(1 for keyword in inquiry_keywords if keyword in query_lower)
        
        # Classify
        if support_score >= 2 or any(word in query_lower for word in ['angry', 'upset', 'disappointed', 'complaint']):
            return {
                'type': 'support_ticket',
                'priority': 'high' if any(word in query_lower for word in ['urgent', 'asap', 'emergency']) else 'normal',
                'confidence': 0.8
            }
        elif inquiry_score >= 1 or support_score == 0:
            return {
                'type': 'general_inquiry',
                'priority': 'normal',
                'confidence': 0.7
            }
        else:
            return {
                'type': 'uncertain',
                'priority': 'normal',
                'confidence': 0.5
            }
    
    def generate_response(self, query: str) -> Dict:
        """
        Generate complete response for a query
        
        Args:
            query: User's question
        
        Returns:
            Dictionary with response details
        """
        # Classify the query
        classification = self.classify_query(query)
        
        if classification['type'] == 'support_ticket':
            # This needs human support
            return {
                'requires_human': True,
                'type': 'support_ticket',
                'priority': classification['priority'],
                'message': "This appears to be a support issue that requires human assistance.",
                'suggested_action': 'create_ticket'
            }
        
        # Get answer from knowledge base
        kb_result = self.get_answer(query)
        
        if kb_result['found'] and kb_result['confidence'] >= 0.6:
            # Confident answer - can auto-respond
            return {
                'requires_human': False,
                'type': 'general_inquiry',
                'answer': kb_result['answer'],
                'sources': kb_result['sources'],
                'confidence': kb_result['confidence'],
                'message': "I found information to answer your question!",
                'suggested_action': 'auto_respond'
            }
        else:
            # Low confidence - escalate to human
            return {
                'requires_human': True,
                'type': 'general_inquiry',
                'message': "I'm not entirely sure about this. Let me get a human to provide accurate information.",
                'suggested_action': 'create_ticket',
                'partial_info': kb_result.get('answer', '')
            }


# Test the service
if __name__ == "__main__":
    kb = KnowledgeBaseService()
    
    # Test queries
    test_queries = [
        "What is your refund policy?",
        "Where are your offices located?",
        "How much does the Full Stack course cost?",
        "My software is not working!",
        "What are your business hours?",
        "Do you offer internships?"
    ]
    
    print("=" * 60)
    print("KNOWLEDGE BASE SERVICE TEST")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        classification = kb.classify_query(query)
        print(f"Classification: {classification['type']} (confidence: {classification['confidence']})")
        
        result = kb.generate_response(query)
        print(f"Requires Human: {result['requires_human']}")
        print(f"Suggested Action: {result['suggested_action']}")
        
        if 'answer' in result:
            print(f"Answer Preview: {result['answer'][:200]}...")
        
        print()
