
import gradio as gr
import query

import sys
import io
import contextlib



def run_query(message, history):
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

    # Clean up output (remove DB count line)
    output = buffer.getvalue().strip().splitlines()
    answer_lines = [line for line in output if not line.startswith("Database contains")]
    return "\n".join(answer_lines)


demo = gr.ChatInterface(
    fn= run_query,
    examples=["What is education policy?", 
              "What are school vouchers?", 
              "How does federal education funding work?"],
    title="Edu Policy Bot "
)

demo.launch(share=True)
