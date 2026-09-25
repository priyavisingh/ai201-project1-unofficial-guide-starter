from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
COURSES_PATH = PROJECT_ROOT / "data" / "courses.json"
CHUNKS_PATH = PROJECT_ROOT / "data" / "chunks.json"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
TOP_K = 5

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "openai/gpt-oss-120b"
COLLECTION_NAME = "gt_compe_courses"
