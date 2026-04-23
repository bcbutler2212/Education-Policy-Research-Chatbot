
# import gradio as gr
# import query

# import sys
# import io
# import contextlib



# def run_query(message, history):
#     old_argv = sys.argv.copy()
#     sys.argv = ["python3 query.py", message]

#     buffer = io.StringIO()
#     with contextlib.redirect_stdout(buffer):
#         try:
#             query.main()
#         except Exception as e:
#             return f"Error: {e}"
#         finally:
#             sys.argv = old_argv

#     # Clean up output (remove DB count line)
#     output = buffer.getvalue().strip().splitlines()
#     answer_lines = [line for line in output if not line.startswith("Database contains")]
#     return "\n".join(answer_lines)


# demo = gr.ChatInterface(
#     fn= run_query,
#     examples=["What is education policy?", 
#               "What are school vouchers?", 
#               "How does federal education funding work?"],
#     title="Edu Policy Bot "
# )

# demo.launch(share=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from src import query
from src.services.pdf_service import pdf_service
import sys
import io
import contextlib

app = Flask(__name__)
CORS(app)


def run_query(message: str) -> str:
    old_argv = sys.argv.copy()
    sys.argv = ["python3 query.py", message]

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            query.main()
        except Exception as e:
            return f"Error: {e}"
        finally:
            sys.argv = old_argv

    output = buffer.getvalue().strip().splitlines()
    answer_lines = [
        line for line in output
        if not line.startswith("Database contains")
    ]
    return "\n".join(answer_lines)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"answer": "Please enter a question."}), 400

    answer = run_query(message)
    return jsonify({"answer": answer})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


#@app.route("/pdfs/<filename>", methods=["GET"])
@app.route("/pdfs/<path:filename>", methods=["GET"])
def serve_pdf(filename):
    """Serve PDF files from the docs directory."""
    return pdf_service.serve_pdf(filename)


@app.route("/pdfs", methods=["GET"])
def list_pdfs():
    """List available PDF files."""
    pdfs = pdf_service.list_available_pdfs()
    return jsonify({"pdfs": pdfs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
