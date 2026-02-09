"""
Tesla Company Profile Q&A Module

Provides question-answering capabilities on the Tesla Company Profile PDF document
with accurate citations including document name and page numbers.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_csv_as_list(filename: str) -> List[Dict[str, Any]]:
    """Load a CSV file and return as list of dictionaries."""
    csv_path = Path(__file__).parent / filename
    result = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric values
            for k, v in list(row.items()):
                if v == '':
                    continue
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result.append(row)
    return result


def load_key_value_csv(filename: str) -> Dict[str, Any]:
    """Load a key-value CSV file as a flat dictionary."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', '')
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                result[key] = value
    return result


def load_pdf_content() -> Dict[int, Dict[str, str]]:
    """Load PDF content indexed by page number."""
    content_list = load_csv_as_list("pdf_content.csv")
    return {int(item['page']): item for item in content_list}


def load_topic_index() -> List[Dict[str, Any]]:
    """Load topic index for keyword-based page lookup."""
    return load_csv_as_list("page_topics.csv")


def load_metadata() -> Dict[str, Any]:
    """Load document metadata."""
    return load_key_value_csv("metadata.csv")


def parse_pages(pages_str: str) -> List[int]:
    """Parse a comma-separated page string into a list of integers."""
    if isinstance(pages_str, int):
        return [pages_str]
    return [int(p.strip()) for p in str(pages_str).split(',')]


def find_relevant_pages(question: str, topic_index: List[Dict], pdf_content: Dict) -> List[int]:
    """
    Find pages relevant to the question based on keyword matching.

    Args:
        question: The user's question
        topic_index: Topic-to-pages mapping
        pdf_content: Page content dictionary

    Returns:
        List of relevant page numbers, sorted by relevance
    """
    question_lower = question.lower()
    page_scores = {}

    # Score pages based on topic keyword matches
    for topic in topic_index:
        keywords = topic.get('keywords', '').lower().split(', ')
        topic_name = topic.get('topic', '').lower()
        pages = parse_pages(topic['pages'])

        # Check for keyword matches
        for keyword in keywords:
            if keyword and keyword in question_lower:
                for page in pages:
                    page_scores[page] = page_scores.get(page, 0) + 2

        # Check for topic name match
        if topic_name and topic_name.replace('_', ' ') in question_lower:
            for page in pages:
                page_scores[page] = page_scores.get(page, 0) + 3

    # Score pages based on direct content matches
    question_words = set(re.findall(r'\b\w{4,}\b', question_lower))
    for page_num, page_data in pdf_content.items():
        content_lower = page_data.get('content', '').lower()
        title_lower = page_data.get('title', '').lower()

        # Check for word matches in content
        for word in question_words:
            if word in content_lower:
                page_scores[page_num] = page_scores.get(page_num, 0) + 1
            if word in title_lower:
                page_scores[page_num] = page_scores.get(page_num, 0) + 2

    # Sort by score and return top pages
    sorted_pages = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
    return [page for page, score in sorted_pages if score > 0]


def extract_answer_content(question: str, relevant_pages: List[int], pdf_content: Dict) -> str:
    """
    Extract relevant content from the identified pages.

    Args:
        question: The user's question
        relevant_pages: List of relevant page numbers
        pdf_content: Page content dictionary

    Returns:
        Combined relevant content from the pages
    """
    if not relevant_pages:
        return ""

    content_parts = []
    for page_num in relevant_pages[:5]:  # Limit to top 5 pages
        if page_num in pdf_content:
            page_data = pdf_content[page_num]
            content_parts.append(f"[Page {page_num} - {page_data.get('title', 'Untitled')}]: {page_data.get('content', '')}")

    return "\n\n".join(content_parts)


def format_citations(pages: List[int], document_name: str) -> List[Dict[str, Any]]:
    """
    Format page numbers into citation objects.

    Args:
        pages: List of page numbers
        document_name: Name of the source document

    Returns:
        List of citation dictionaries
    """
    if not pages:
        return []

    return [{
        "source": document_name,
        "pages": pages[:5]  # Limit to most relevant pages
    }]


def determine_confidence(relevant_pages: List[int], question: str, content: str) -> str:
    """
    Determine confidence level based on match quality.

    Args:
        relevant_pages: Number of relevant pages found
        question: The original question
        content: The extracted content

    Returns:
        Confidence level: "high", "medium", or "low"
    """
    if not relevant_pages:
        return "low"

    question_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
    content_lower = content.lower()

    # Count how many question words appear in content
    matches = sum(1 for word in question_words if word in content_lower)
    match_ratio = matches / len(question_words) if question_words else 0

    if len(relevant_pages) >= 2 and match_ratio >= 0.5:
        return "high"
    elif len(relevant_pages) >= 1 and match_ratio >= 0.3:
        return "medium"
    else:
        return "low"


def answer_question(question: str) -> Dict[str, Any]:
    """
    Answer a question about Tesla based on the PDF content.

    Args:
        question: The question to answer

    Returns:
        Dictionary containing:
        - answer: The response based on PDF content
        - citations: List of citations with source and page numbers
        - confidence: Confidence level of the answer
    """
    # Load data
    pdf_content = load_pdf_content()
    topic_index = load_topic_index()
    metadata = load_metadata()
    document_name = metadata.get('document_name', 'TeslaCompanyProfile.pdf')

    # Find relevant pages
    relevant_pages = find_relevant_pages(question, topic_index, pdf_content)

    if not relevant_pages:
        return {
            "answer": "I could not find information directly addressing this question in the Tesla Company Profile document.",
            "citations": [],
            "confidence": "low"
        }

    # Extract content from relevant pages
    content = extract_answer_content(question, relevant_pages, pdf_content)

    # Determine confidence
    confidence = determine_confidence(relevant_pages, question, content)

    # Format citations
    citations = format_citations(relevant_pages[:5], document_name)

    # Build answer with the relevant content
    answer = f"Based on the Tesla Company Profile document:\n\n{content}"

    # Add citation reference to answer
    citation_pages = relevant_pages[:5]
    citation_str = ", ".join([f"Page {p}" for p in citation_pages])
    answer += f"\n\n[Citation: {document_name}, {citation_str}]"

    return {
        "answer": answer,
        "citations": citations,
        "confidence": confidence
    }


def get_page_content(page_number: int) -> Optional[Dict[str, str]]:
    """
    Get content for a specific page.

    Args:
        page_number: The page number to retrieve

    Returns:
        Dictionary with page title and content, or None if not found
    """
    pdf_content = load_pdf_content()
    metadata = load_metadata()

    if page_number in pdf_content:
        page_data = pdf_content[page_number]
        return {
            "source": metadata.get('document_name', 'TeslaCompanyProfile.pdf'),
            "page": page_number,
            "title": page_data.get('title', ''),
            "content": page_data.get('content', '')
        }
    return None


def list_topics() -> List[Dict[str, Any]]:
    """
    List all topics covered in the document with their page references.

    Returns:
        List of topic dictionaries with topic name, pages, and keywords
    """
    topic_index = load_topic_index()
    metadata = load_metadata()
    document_name = metadata.get('document_name', 'TeslaCompanyProfile.pdf')

    return [{
        "source": document_name,
        "topic": topic.get('topic', ''),
        "pages": parse_pages(topic.get('pages', '')),
        "keywords": topic.get('keywords', '').split(', ')
    } for topic in topic_index]


def main():
    """Example usage of the Tesla Q&A system."""
    print("=" * 70)
    print("Tesla Company Profile Q&A System")
    print("=" * 70)

    # Example questions
    questions = [
        "What is Tesla's mission statement?",
        "How many employees does Tesla have?",
        "What are Tesla's battery cost reduction strategies?",
        "How does Tesla's direct-to-consumer sales model work?",
        "What is the price of the Model 3?",
        "How does Tesla handle vehicle service?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        print("-" * 50)
        result = answer_question(question)
        print(f"Confidence: {result['confidence']}")
        print(f"Citations: {result['citations']}")
        print(f"Answer preview: {result['answer'][:500]}...")
        print()

    print("=" * 70)
    print("\nAvailable Topics:")
    for topic in list_topics():
        print(f"  - {topic['topic']}: Pages {topic['pages']}")


if __name__ == "__main__":
    main()
