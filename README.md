# Invaro SDK

Python SDK for the Invaro AI API, providing easy access to document parsing services.

## Local Development Setup

1. Clone the repository:

```bash
git clone https://github.com/Harshit-65/invaro_sdk.git
cd invaro-sdk
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install the package in development mode:

```bash
pip install -e .
```

## Usage Example

```python
import asyncio
from invaro import InvaroClient, InvaroError

async def main():
    API_KEY = "your_api_key_here"

    async with InvaroClient(API_KEY) as client:
        # Upload documents
        upload_result = await client.upload_documents(["invoice.pdf", "statement.pdf"])

        # Process a statement
        statement_doc_id = upload_result["files"][0]["doc_id"]
        statement_data = await client.process_statements(statement_doc_id, wait_for_completion=True)
        print("Statement data:", statement_data)

        # Process an invoice
        invoice_doc_id = upload_result["files"][1]["doc_id"]
        invoice_data = await client.process_invoices(invoice_doc_id, wait_for_completion=True)
        print("Invoice data:", invoice_data)

if __name__ == "__main__":
    # For Windows systems
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
```

## Features

- Asynchronous API client
- Document upload support
- Bank statement processing
- Invoice processing
- Batch processing capabilities
- Job status polling

## API Reference

### InvaroClient

```python
client = InvaroClient(api_key, base_url="https://api.invaro.ai/api/v1", poll_interval=5)
```

#### Methods

- `upload_documents(files: List[str])`: Upload multiple documents
- `process_statements(document_id: str, wait_for_completion: bool = False)`: Process a bank statement
- `process_statements_batch(document_ids: List[str], wait_for_completion: bool = False)`: Process multiple statements
- `get_statement_status(job_id: str)`: Get statement processing status
- `process_invoices(document_id: str, wait_for_completion: bool = False)`: Process an invoice
- `process_invoices_batch(document_ids: List[str], wait_for_completion: bool = False)`: Process multiple invoices
- `get_invoice_status(job_id: str)`: Get invoice processing status

## Error Handling

The SDK uses the `InvaroError` exception class for error handling:

```python
try:
    result = await client.process_statements(doc_id)
except InvaroError as e:
    print(f"Error: {str(e)}")
```

## Windows Support

For Windows systems, you may need to set the event loop policy:

```python
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```
