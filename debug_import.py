import traceback
import sys

print("__name__:", __name__)
print("__package__:", __package__)
print("sys.path:", sys.path)
try:
    import backend.main  # or backend.loaders.stm if you want to isolate
except Exception:
    traceback.print_exc()
    raise
