import os
import sys

# Make `webui.server` importable from tests
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Default-skip the eager catalog warmup so tests that build their own
# Flask app with create_app() don't fork a background thread that would
# race against per-test cache resets. Tests that *want* warmup (e.g.
# test_app_warmup) override this explicitly.
os.environ.setdefault("SKIP_CATALOG_WARMUP", "1")
