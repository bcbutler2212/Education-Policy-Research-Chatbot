<<<<<<< HEAD
**Getting Started**

- We are using Docker, a service that allows us to all work from the same system environment.
- In order to do this, first download docker onto your machine. You can either do the gui (application with graphics) or just the cli version (in terminal). I did the cli but it shouldn't make a difference
- run this command so that you don't use sudo everytime you run docker: sudo usermod -aG docker $USER
- then run this command: docker education-chatbot
- when you are done with the container, grab the id of the container using docker ps -a and then copy that id and run docker stop [id]

**Common Errors**
-If you are getting an error that says Ollama isn't running (or some variation of that), then you need to install run : ollama serve

-If query.py doesn't say that there are any documents that are in the database, then you need to run "python ingest.py"


**Work Needed**
- Proper citation for the responses --> need to know if its pulling the right text in addition to the correct documents 
- Memory for the chatbot so that you can continue a conversation
- Play around with chunk size to see if that changes accuracy of responses
- Integrate better LLM 
- Play around with metaprompt (in query.py) to see how that changes quality of responses.

