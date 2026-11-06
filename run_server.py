import uvicorn
from pathlib import Path
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    print("=" * 65)
    print("  >> APNAMART AI SALES ASSISTANT (ApnaMart Sahayak)")
    print("  >> Official Storefront: https://apnamarts.shop/ ('Sab Kuch, Ek Hi Jagah')")
    print("  >> Powered by LangGraph StateGraph + Groq LPU + all-mpnet-base-v2 (768-D)")
    print("  >> Server running at: http://localhost:8000")
    print("=" * 65)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
