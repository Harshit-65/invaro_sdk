import aiohttp
import asyncio
from aiohttp import FormData
from .exceptions import InvaroError

class InvaroClient:
    def __init__(self, api_key, base_url="https://api.invaro.ai/api/v1", poll_interval=5):
        self.api_key = api_key
        self.base_url = base_url
        self.poll_interval = poll_interval
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            **kwargs.pop("headers", {})
        }

        async with self.session.request(method, url, headers=headers, **kwargs) as response:
            data = await response.json()
            
            if not response.ok:
                error_msg = data.get("error", await response.text())
                raise InvaroError(f"{response.status}: {error_msg}")
            
            return data

    async def _poll_job(self, job_id, endpoint_template):
        while True:
            result = await self._request("GET", endpoint_template.format(job_id=job_id))
            
            # Handle both response structures
            if "data" in result:
                status = result["data"]["status"]
            else:
                status = result["status"]
                result = {"data": result}  # Normalize the response structure
            
            if status == "completed":
                return result["data"]
            elif status == "failed":
                raise InvaroError(f"Job {job_id} failed")
            
            await asyncio.sleep(self.poll_interval)

    async def upload_documents(self, files):
        endpoint = "/parse/upload"
        form_data = FormData()

        for file in files:
            form_data.add_field(
                "files",
                open(file, "rb"),
                filename=file.split("/")[-1],
                content_type="application/octet-stream"
            )

        response = await self._request("POST", endpoint, data=form_data)
        return response["data"]

    async def process_statements(self, document_id, wait_for_completion=False):
        endpoint = "/parse/statements"
        response = await self._request("POST", endpoint, json={"document_id": document_id})
        
        if wait_for_completion:
            return await self._poll_job(response["data"]["job_id"], "/parse/statements/{job_id}")
        return response["data"]

    async def process_statements_batch(self, document_ids, wait_for_completion=False):
        endpoint = "/parse/statements/batch"
        payload = {"files": [{"document_id": doc_id} for doc_id in document_ids]}
        response = await self._request("POST", endpoint, json=payload)
        
        if wait_for_completion:
            return await asyncio.gather(*[
                self._poll_job(job_id, "/parse/statements/{job_id}")
                for job_id in response["data"]["job_ids"]
            ])
        return response["data"]

    async def get_statement_status(self, job_id):
        response = await self._request("GET", f"/parse/statements/{job_id}")
        return response["data"]

    async def process_invoices(self, document_id, wait_for_completion=False):
        endpoint = "/parse/invoices"
        response = await self._request("POST", endpoint, json={"document_id": document_id})
        
        if wait_for_completion:
            return await self._poll_job(response["data"]["job_id"], "/parse/invoices/{job_id}")
        return response["data"]

    async def process_invoices_batch(self, document_ids, wait_for_completion=False):
        endpoint = "/parse/invoices/batch"
        payload = {"files": [{"document_id": doc_id} for doc_id in document_ids]}
        response = await self._request("POST", endpoint, json=payload)
        
        if wait_for_completion:
            return await asyncio.gather(*[
                self._poll_job(job_id, "/parse/invoices/{job_id}")
                for job_id in response["data"]["job_ids"]
            ])
        return response["data"]

    async def get_invoice_status(self, job_id):
        response = await self._request("GET", f"/parse/invoices/{job_id}")
        return response["data"]
