import random

import pytest


@pytest.fixture(autouse=True)
def set_global_seeds():
    """Autouse fixture ensuring global test determinism across seedable engines."""
    random.seed(42)
    try:
        import numpy as np

        np.random.seed(42)
    except ImportError:
        pass

    try:
        import torch

        torch.manual_seed(42)
    except ImportError:
        pass
