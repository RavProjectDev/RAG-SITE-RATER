from fastapi.testclient import TestClient
from rag.app.main import app
from unittest.mock import patch, MagicMock
import io

client = TestClient(app)


@patch("rag.app.api.v1.upload.preprocess_raw_transcripts", return_value=[])
@patch("rag.app.api.v1.upload.generate_embedding")
def test_upload_valid_srt(mock_embed, mock_preprocess):
    mock_embed.return_value.vector = [0.1, 0.2, 0.3]
    mock_conn = MagicMock()
    mock_conn.insert.return_value = None
    with client as c:
        c.app.state.mongo_conn = mock_conn
        file_content = "1\n00:00:00,000 --> 00:00:01,000\nHello world!"
        files = [
            ("files", ("test.srt", io.BytesIO(file_content.encode()), "text/plain"))
        ]
        response = c.post("/api/v1/upload/", files=files)
        assert response.status_code == 200
        assert "results" in response.json()


def test_upload_invalid_filetype():
    file_content = "not an srt file"
    files = [("files", ("test.txt", io.BytesIO(file_content.encode()), "text/plain"))]
    response = client.post("/api/v1/upload/", files=files)
    print(response.json())
    assert response.status_code == 400
    assert "must be an .srt file" in response.json()["detail"]


@patch(
    "rag.app.api.v1.upload.preprocess_raw_transcripts", side_effect=Exception("fail")
)
def test_upload_internal_error(mock_preprocess):
    file_content = "1\n00:00:00,000 --> 00:00:01,000\nHello world!"
    files = [("files", ("test.srt", io.BytesIO(file_content.encode()), "text/plain"))]
    response = client.post("/api/v1/upload/", files=files)
    assert response.status_code == 500
    assert "fail" in response.json()["detail"]
