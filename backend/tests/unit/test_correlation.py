from app.observability.correlation import clear_correlation_id, generate_correlation_id, get_correlation_id, set_correlation_id


def test_correlation_id_context() -> None:
    generated = generate_correlation_id()
    set_correlation_id(generated)

    assert get_correlation_id() == generated

    clear_correlation_id()
    assert get_correlation_id() is None
