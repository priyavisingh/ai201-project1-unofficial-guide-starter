from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHUNKS_PATH = PROJECT_ROOT / "data" / "chunks.json"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
TOP_K = 5

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
COLLECTION_NAME = "gt_professor_reviews"
