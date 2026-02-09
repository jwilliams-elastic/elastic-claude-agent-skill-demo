# Skill: Tesla Company Profile Q&A

## Domain
automotive

## Description
Answers questions about Tesla's business model, operations, customer journey, manufacturing, battery technology, and strategy based on the Bain & Company Tesla Company Profile document. Provides accurate citations with document name and page numbers.

## Business Rules
This skill provides question-answering capabilities on the Tesla Company Profile PDF document:

1. **Citation Requirement**: All answers must include citations in the format: `[TeslaCompanyProfile.pdf, Page X]`
2. **Multi-Page Answers**: When information spans multiple pages, all relevant page numbers must be cited
3. **Content Scope**: Answers are limited to information contained within the PDF document
4. **No Speculation**: If information is not in the document, the skill should indicate this clearly

## Document Coverage
The Tesla Company Profile (46 pages) covers:
- Executive summary and mission (Page 1)
- Master plan timeline and strategy (Page 2)
- Organizational structure (Page 3)
- Key financial numbers and market position (Page 4)
- Battery technology and cost improvements (Pages 5-6)
- Vehicle models and pricing (Page 7)
- Customer journey overview (Page 8)
- Showroom and retail strategy (Page 9)
- Direct-to-consumer sales model (Pages 10-16)
- Financing options (Page 17)
- Over-the-Air (OTA) updates (Pages 18-20)
- Owner account and mobile app (Page 21)
- Service operations (Page 22)
- SKU simplification (Page 23)
- Operating model and manufacturing (Pages 24-33)
- Incentives and state regulations (Pages 34-36)
- Distribution network (Pages 37-38)
- Trade-in process (Pages 39-41)
- Sales tax handling (Page 42)
- Competitor information (Pages 43-46)

## Input Parameters
- `question` (string): The question to answer about Tesla based on the PDF content

## Output
Returns an answer with:
- `answer` (string): The response to the question based on PDF content
- `citations` (list): List of citations in format {"source": "TeslaCompanyProfile.pdf", "pages": [page_numbers]}
- `confidence` (string): "high", "medium", or "low" based on how directly the content addresses the question

## Usage Example
```python
from tesla_qa import answer_question

result = answer_question(
    question="What is Tesla's mission statement?"
)

print(f"Answer: {result['answer']}")
print(f"Citations: {result['citations']}")
```

## Tags
automotive, tesla, electric-vehicles, business-model, question-answering, document-qa

## Implementation
The Q&A logic is implemented in `tesla_qa.py` and references content from:
- `pdf_content.csv` - Page-by-page content from the PDF document
- `page_topics.csv` - Topic index mapping pages to key subjects
- `metadata.csv` - Document metadata

## Test Execution
```python
from tesla_qa import answer_question

# Call the skill function
result = answer_question(
    question=input_data.get('question')
)

# Format output
output = {
    'answer': result.get('answer'),
    'citations': result.get('citations'),
    'confidence': result.get('confidence')
}
```
