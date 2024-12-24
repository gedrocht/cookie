import re
from fpdf import FPDF
import sys

sys.path.append('../')
from utils import util

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_left_margin(20)  # Equivalent to approx. 0.33 inches
        self.set_right_margin(20)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Arial", size=12)

    def add_formatted_text(self, text):
        # Regex patterns for Markdown formatting
        bold_pattern = r'\*\*(.*?)\*\*'
        italic_pattern = r'_(.*?)_'

        # Split the text by bold formatting and apply styling inline
        parts = re.split(bold_pattern, text)
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Non-bold text, split further by italic formatting
                italic_parts = re.split(italic_pattern, part)
                for j, italic_part in enumerate(italic_parts):
                    if j % 2 == 0:
                        # Normal text
                        self.set_font("Arial", size=12, style="")
                        self.multi_cell(0, 10, italic_part, border=0)
                    else:
                        # Italic text
                        self.set_font("Arial", size=12, style="I")
                        self.multi_cell(0, 10, italic_part, border=0)
            else:
                # Bold text
                self.set_font("Arial", size=12, style="B")
                self.multi_cell(0, 10, part, border=0)

def generate_document(filename, text):
    pdf = PDF()
    pdf.add_formatted_text(text)

    # Save the PDF
    filename = filename.replace(",", "").replace(".", "")
    pdf.output(filename + ".pdf")
    util.log(f"Generated {filename}.pdf")
