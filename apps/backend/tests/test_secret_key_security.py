import pytest
from app.config import validate_production_security

def test_production_default_secret_key_fails():
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_security(environment="production", secret_key="insecure_dev_key")
    assert "Insecure default SECRET_KEY detected in production" in str(exc_info.value)
    # Garante que a chave não é vazada na mensagem de erro
    assert "insecure_dev_key" not in str(exc_info.value)

def test_production_change_this_default_fails():
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_security(environment="production", secret_key="change-this-to-a-random-secret-key")
    assert "Insecure default SECRET_KEY detected in production" in str(exc_info.value)

def test_production_missing_or_none_secret_key_fails():
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_security(environment="production", secret_key="")
    assert "SECRET_KEY must be explicitly configured" in str(exc_info.value)

def test_production_whitespace_secret_key_fails():
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_security(environment="production", secret_key="   ")
    assert "SECRET_KEY must be explicitly configured" in str(exc_info.value)

def test_production_custom_secure_secret_key_passes():
    test_key = "super-secure-production-random-key-12345"
    assert validate_production_security(environment="production", secret_key=test_key) is True

def test_development_default_secret_key_passes():
    assert validate_production_security(environment="development", secret_key="insecure_dev_key") is True
    assert validate_production_security(environment="development", secret_key="change-this-to-a-random-secret-key") is True

def test_test_environment_default_secret_key_passes():
    assert validate_production_security(environment="test", secret_key="insecure_dev_key") is True
    assert validate_production_security(environment="testing", secret_key="insecure_dev_key") is True

def test_environment_case_insensitivity_triggers_protection():
    for env_val in ["production", "Production", "PRODUCTION", "  production  "]:
        with pytest.raises(RuntimeError):
            validate_production_security(environment=env_val, secret_key="insecure_dev_key")

def test_error_message_does_not_leak_secret_value():
    secret_val = "sensitive_leaked_key_999"
    with pytest.raises(RuntimeError) as exc_info:
        validate_production_security(environment="production", secret_key="")
    assert secret_val not in str(exc_info.value)
