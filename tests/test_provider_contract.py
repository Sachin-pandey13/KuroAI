import time

from backend.capabilities.providers.base_provider import BaseProvider
from backend.contracts.capability import CapabilityType, ToolRequest, ToolResponse


def verify_provider_contract(
    provider: BaseProvider,
    capability_type: CapabilityType,
    valid_params: dict,
    invalid_params: dict,
):
    """
    Shared contract test suite that every provider must satisfy.
    Verifies standardized behavior across the ecosystem.
    """
    assert provider.provider_name is not None
    assert isinstance(provider.supported_models, list)

    # 1. Test Valid Request
    valid_request = ToolRequest(
        capability_type=capability_type,
        parameters=valid_params,
        preferred_model=provider.supported_models[0] if provider.supported_models else None,
    )

    start_time = time.time()
    response = provider.execute(valid_request)
    (time.time() - start_time) * 1000

    assert isinstance(response, ToolResponse), "Provider must return a valid ToolResponse"
    assert response.request_id == valid_request.request_id, "Provider must preserve request_id"
    assert response.provider_name == provider.provider_name, "Provider must populate provider_name"
    assert response.model_name is not None, "Provider must populate model_name"

    # We allow some fuzziness on execution time in tests, but it should be recorded
    assert response.execution_time_ms >= 0, "Provider must measure execution_time_ms"
    if response.success:
        assert response.error_message is None

    # 2. Test Invalid Request (must return success=False instead of throwing unexpected exceptions)
    invalid_request = ToolRequest(
        capability_type=capability_type,
        parameters=invalid_params,
        preferred_model="invalid_model_that_does_not_exist",
    )

    # Provider should not raise an exception, but return success=False with an error_message
    invalid_response = provider.execute(invalid_request)
    assert not invalid_response.success, "Provider must return success=False on failures"
    assert (
        invalid_response.error_message is not None
    ), "Provider must populate error_message on failure"
    assert invalid_response.request_id == invalid_request.request_id
    assert invalid_response.provider_name == provider.provider_name
