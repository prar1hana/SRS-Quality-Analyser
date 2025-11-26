import gradio as gr
from quality_checker import RequirementAnalyzer


def extract_text(file):
    if file is None:
        return "No file uploaded.", "No marked text.", "No summary.", "0", "0", "0"

    file_path = file.name
    text = ""

    try:
        if file_path.endswith(".pdf"):
            import fitz
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text()

        elif file_path.endswith((".docx", ".doc")):
            import mammoth
            from bs4 import BeautifulSoup
            with open(file_path, "rb") as doc_file:
                result = mammoth.convert_to_html(doc_file)
                soup = BeautifulSoup(result.value, "html.parser")
                text = soup.get_text("\n")

        elif file_path.endswith((".html", ".htm")):
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                text = soup.get_text("\n")

        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        else:
            return "Unsupported file format.", "No marked text.", "No summary.", "0", "0", "0"

    except Exception as e:
        return f"Error extracting text: {e}", "No marked text.", "No summary.", "0", "0", "0"

    analyzer = RequirementAnalyzer()
    marked_text, summary_report, summary = analyzer.get_text_report(text)

    return (
        text,                              # Extracted text
        marked_text,                       # Text with inline markings
        summary_report,                    # Summary report (human readable)
        str(summary["missing_info"]),      # Missing Info count
        str(summary["ambiguous_pronouns"]),# Ambiguous Pronoun count
        str(summary["total_issues"])       # Total issues count
    )


# Gradio Interface
interface = gr.Interface(
    fn=extract_text,
    inputs=gr.File(label="📄 Upload your SRS document (PDF, DOC, DOCX, TXT, HTML)"),
    outputs=[
        gr.Textbox(label="📜 Extracted Text", lines=15, placeholder="Raw extracted text from file..."),
        gr.Textbox(label="🧩 Marked Text (with Issues)", lines=20, placeholder="Lines with ⚠️ and ❌ markers..."),
        gr.Textbox(label="🧠 Summary Report", lines=10, placeholder="Detailed issue summary..."),
        gr.Textbox(label="⚠️ Missing Info Count", lines=1),
        gr.Textbox(label="🤔 Ambiguous Pronoun Count", lines=1),
        gr.Textbox(label="📊 Total Issues", lines=1),
    ],
    title="SRS Quality Checker",
    description="Upload your SRS file to extract text, mark ambiguous pronouns and missing information, and view summary statistics."
)


if __name__ == "__main__":
    interface.launch()
