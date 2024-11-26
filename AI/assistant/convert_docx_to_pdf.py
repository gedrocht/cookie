import subprocess
import sys
import os

sys.path.append('../')
from utils import util

def log(msg):
    util.log(msg, "DCXPDF")

def convert(docx_path):
    source_path = docx_path + ".docx"
    pdf_path = source_path.replace(".docx", ".pdf")
    output_dir = os.path.dirname(os.path.abspath(docx_path))

    command = [
        "libreoffice", "--headless", "--convert-to", "pdf", source_path, "--outdir", output_dir
    ]

    try:
        log(f"Converting {source_path} to {pdf_path}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        log(f"An error occurred: {e}")