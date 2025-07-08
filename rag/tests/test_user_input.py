from rag.app.services.preprocess.user_input import pre_process_user_query


def test_pre_process_user_query_removes_question_words():
    q = "What is the Torah?"
    result = pre_process_user_query(q)
    assert "What" not in result and "is" not in result and "the" not in result
    assert "Torah?" in result


def test_pre_process_user_query_strip():
    q = "   How does this work?   "
    result = pre_process_user_query(q)
    assert result.strip() == result


def test_pre_process_user_query_empty():
    q = ""
    result = pre_process_user_query(q)
    assert result == ""
