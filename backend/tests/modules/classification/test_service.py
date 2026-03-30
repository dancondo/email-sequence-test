from app.modules.classification.schemas import ClassificationResult, ReplyIntent


def test_classify_reply_delegates_to_provider(
    classification_service, mock_classification_provider
):
    expected = ClassificationResult(
        intent=ReplyIntent.INTERESTED,
        confidence=0.95,
        reasoning="Candidate expressed interest",
    )
    mock_classification_provider.classify_reply.return_value = expected

    result = classification_service.classify_reply("I'd love to learn more!")

    assert result is expected
    mock_classification_provider.classify_reply.assert_called_once_with(
        "I'd love to learn more!"
    )
