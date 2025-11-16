from agents.extensions.models.litellm_model import LitellmModel
import os
from contextvars import ContextVar

XAI_API_KEY = os.getenv("XAI_API_KEY")

xai_grok_4_fast_reasoning_model: LitellmModel = LitellmModel(model="xai/grok-4-fast-reasoning", api_key=XAI_API_KEY)

# Context variable to store the selected model for the current async context
_model_context: ContextVar[str] = ContextVar("model_context", default="o4_mini")

def set_model_context(model: str):
    """Set the model for the current async context."""
    _model_context.set(model)

def get_model(requested_model: str = None):
    """
    Get the model to use for inference.

    Args:
        requested_model: Optional model override. If not provided, uses the context model.

    Returns:
        The model instance or string identifier.
    """
    # Use the provided model, otherwise get from context
    model_choice = requested_model if requested_model is not None else _model_context.get()

    if model_choice == "xai_grok_4_fast_reasoning":
        model = xai_grok_4_fast_reasoning_model
    elif model_choice == "o4_mini":
        model = "o4-mini"
    else:
        raise ValueError(f"No valid model selected: {model_choice}")
    return model