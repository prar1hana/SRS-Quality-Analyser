import gradio as gr
import fitz
import mammoth
from bs4 import BeautifulSoup

from quality_checker import RequirementAnalyzer

def extract_text(file, analysis_types):
    if file is None:
        return (
            "No file uploaded", # Extracted Text
            "No file uploaded", # Marked Text
            "No file uploaded", # Summary Report
            "0", # Missing Info Count
            "0", # Ambiguous Pronoun Count
            "0"  # Total Issues
        )
    
    if not analysis_types:
        return (
            "No analysis type selected.",
            "No analysis type selected.",
            "No analysis type selected.",
            "0",
            "0",
            "0"
        )
        
    file_path = file.name
    text = ""
    try:
        if file_path.endswith(".pdf"):

            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text()

        elif file_path.endswith((".docx", ".doc")):

            with open(file_path, "rb") as doc_file:
                result = mammoth.convert_to_html(doc_file)
                soup = BeautifulSoup(result.value, "html.parser")
                text = soup.get_text("\n")

        elif file_path.endswith((".html", ".htm")):
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                text = soup.get_text("\n")

        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            return (
                "Unsupported file format.",
                "Unsupported file format.",
                "Unsupported file format.",
                "0",
                "0",
                "0"
            )

    except Exception as e:
        error_msg = f"Error extracting text: {e}"
        return (
            error_msg,
            error_msg,
            error_msg,
            "0",
            "0",
            "0"
        )

    analyzer = RequirementAnalyzer()
    marked_text, summary_report, summary = analyzer.get_text_report(text, analysis_types)

    return (
        text,
        marked_text,
        summary_report,
        str(summary["missing_info"]),
        str(summary["ambiguous_pronouns"]),
        str(summary["total_issues"])
    )


# Define the analysis type choices
analysis_choices = [
    "Missing Info", 
    "Ambiguous Pronouns"
]

# Create the CheckboxGroup input component
analysis_input = gr.CheckboxGroup(
    choices=analysis_choices,
    value=analysis_choices, # Set both to be checked by default
    label="Select Analysis Types"
)

interface = gr.Interface(
    fn=extract_text,
    inputs=[
        gr.File(label="Upload SRS"),
        analysis_input # Added the new input component
    ],
    outputs=[
        gr.Textbox(label="Extracted Text", lines=15, placeholder="Raw extracted text from file...", interactive=True),
        gr.Textbox(label="Marked Text (with Issues)", lines=20, placeholder="Lines with <<!!!>> (Ambiguous Pronoun) and <<XXX>> (Missing Info) markers", interactive=False),
        gr.Textbox(label="Summary Report & Recommendations", lines=10, placeholder="Detailed issue summary and recommended precise replacements", interactive=False),
        gr.Textbox(label="Missing Info Count (Type 1)", lines=1, interactive=False),
        gr.Textbox(label="Ambiguous Pronoun Count (Type 2)", lines=1, interactive=False),
        gr.Textbox(label="Total Issues", lines=1, interactive=False),
    ],
    title="SRS Quality Checker: Completeness and Clarity Analyzer",
    description="Upload your document to identify placeholders (e.g., TBD) and potentially ambiguous pronouns. **Use the checkboxes below to select which checks to run.**"
)


if __name__ == "__main__":
    interface.launch()