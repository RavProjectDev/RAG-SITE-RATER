from fastapi import APIRouter, Depends, HTTPException

from rag.app.exceptions import BaseAppException
from rag.app.schemas.data import (
    EmbeddingConfiguration,
)

from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.dependencies import (
    get_embedding_conn,
    get_metrics_conn,
    get_embedding_configuration,
)
from rag.app.schemas.requests import UploadRequest
from rag.app.schemas.response import UploadResponse
from rag.app.exceptions.upload import BaseUploadException

router = APIRouter()
from rag.app.services.data_upload_service import pre_process_uploaded_documents


@router.post("/")
async def upload_files(
    upload_request: UploadRequest,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    metrics_conn: MetricsConnection = Depends(get_metrics_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
):
    """
      Upload endpoint for subtitle (.srt) files.

      Accepts multiple .srt files via multipart/form-data, processes
      their textual content into data chunks, generates vector embeddings
      for each chunk, and stores the embeddings in the database.

      Request:
      --------
    b'{"_id":"55806772-3246-4eaf-88a3-4448eb39846e","_updatedAt":"2025-07-15T20:31:24Z","slug":"kedusha-and-malchus","title":"Kedusha and Malchus","transcriptURL":"https://cdn.sanity.io/files/ybwh5ic4/primary/2fbb38de4c27f54dfe767841cde0dae92c4be543.srt"}'
      Response:
      ---------
      JSON object containing:
          {
              "results": [
                  {
                      "vector": [...],
                      "dimension": <int>,
                      "data": {
                          "text": <str>,
                          ...
                      }
                  },
                  ...
              ]
          }

      Raises:
      -------
      HTTPException (400):
          If any uploaded file is not an .srt file.

      HTTPException (500):
          For any unexpected server-side errors.
    """
    try:
        embeddings = await pre_process_uploaded_documents(
            upload_request=upload_request,
            metrics_conn=metrics_conn,
            embedding_configuration=embedding_configuration,
        )

    except BaseUploadException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": e.message,
                "code": e.code,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": BaseAppException.code,
                "message": str(e),
            },
        )
    try:
        res = await embedding_conn.insert(embeddings)
    except BaseUploadException as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": str(e),
                "code": e.code,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": str(e),
                "code": BaseAppException.code,
            },
        )

    if not res:
        raise HTTPException(400)
    return UploadResponse(
        message="Successfully uploaded files",
    )
