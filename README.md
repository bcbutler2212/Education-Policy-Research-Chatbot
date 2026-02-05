<<<<<<< HEAD
**Getting Started**
I highly recommend using python's venv to run the query.py program. This makes sure that you won't have any version discrepancies.

Additionally, this program was built to run on Python 3.12. If your computer isn't on this version of python, then you <u>must</u> run using venv

<b>Note</b>: this may be easier using the "uv" package for python, the documentation for that is : https://docs.astral.sh/uv/getting-started/installation/#standalone-installer

You can use "uv" to create a standalone python version that you venv can use. The command I used is : "uv venv --python 3.12 myenv"

*Setting up venv*
run python -m venv <u>name</u>
next: source <u>name</u>/bin/activate

Next, download the requirments from requirments.txt

run pip install -r requirments.txt

Once requriments are downloaded, start chatting with the bot by running:

python3 query.py


**Common Errors**
-If you are getting an error that says Ollama isn't running (or some variation of that), then you need to install run : sudo systmctl start ollama

-If query.py doesn't say that there are any documents that are in the database, then you need to run "python ingest.py"


**Work Needed**
- Proper citation for the responses --> need to know if its pulling the right text in addition to the correct documents 
- Memory for the chatbot so that you can continue a conversation
- Play around with chunk size to see if that changes accuracy of responses
- Integrate better LLM 
- Play around with metaprompt (in query.py) to see how that changes quality of responses.

>>>>>>> Charlie
