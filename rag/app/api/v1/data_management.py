from fastapi import APIRouter, Depends, HTTPException, Request

from rag.app.db.connections import EmbeddingConnection
from rag.app.dependencies import (
    get_embedding_conn,
    get_embedding_configuration,
)
from rag.app.exceptions import BaseAppException
from rag.app.exceptions.upload import BaseUploadException
from rag.app.models.data import SanityData
from rag.app.schemas.data import (
    EmbeddingConfiguration,
)
from rag.app.schemas.response import UploadResponse

from rag.app.services.data_upload_service import upload_document

router = APIRouter()


@router.post("/create")
async def upload_files(
    upload_request: SanityData,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
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
        await upload_document(upload_request, embedding_conn, embedding_configuration)

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

    return UploadResponse(message="success")


@router.patch("/update")
async def update_files(
    body: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
):
    print(await body.json())
    return


@router.delete("/delete")
async def delete_files(
    body: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
):
    print(await body.json())
    return
