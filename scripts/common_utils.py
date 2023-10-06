import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
OUTPUT_CSV_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "generated_csv_files"
)
