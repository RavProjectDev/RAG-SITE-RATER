import httpx
import logging

logging.basicConfig(level=logging.INFO)

from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.schemas.data import EmbeddingConfiguration
from rag.app.schemas.requests import UploadRequest
from rag.app.services.data_upload_service import pre_process_uploaded_documents

MANIFEST_URL = "https://the-rav-project.vercel.app/api/manifest"


async def post_data(payload=None):
    if payload is None:
        payload = {}
    async with httpx.AsyncClient() as client:
        response = await client.post(MANIFEST_URL, json=payload)
        if response.status_code != 200:
            return None
        return response.json()


async def run(
    connection: EmbeddingConnection,
    metrics_conn: MetricsConnection,
    embedding_configuration: EmbeddingConfiguration,
):
    logging.info("[run] Fetching manifest data...")
    manifest = await post_data()
    if manifest is None:
        logging.error("[run] Failed to fetch manifest.")
        return
    logging.info(f"[run] Fetched {len(manifest)} manifest entries.")

    unique_transcript_ids = await connection.get_all_unique_transcript_ids()
    logging.info(
        f"[run] Found {len(unique_transcript_ids)} unique transcript IDs in DB."
    )

    documents_needed_to_be_uploaded: list[UploadRequest] = []

    for doc_id, content in manifest.items():
        if doc_id not in unique_transcript_ids:
            logging.info(f"[run] New document found: {doc_id}")
            documents_needed_to_be_uploaded.append(UploadRequest(id=doc_id, **content))

    if not documents_needed_to_be_uploaded:
        logging.info("[run] No new documents to upload.")
        return

    logging.info(
        f"[run] Preparing to upload {len(documents_needed_to_be_uploaded)} documents..."
    )

    for upload_request in documents_needed_to_be_uploaded:
        logging.info(f"[run] Processing document: {upload_request.id}")
        document_embedding = await pre_process_uploaded_documents(
            upload_request=upload_request,
            metrics_conn=metrics_conn,
            embedding_configuration=embedding_configuration,
        )
        await connection.insert(document_embedding)
        logging.info(f"[run] Inserted embedding for: {upload_request.id}")
