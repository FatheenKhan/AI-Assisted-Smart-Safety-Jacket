import spacy

# Download and install the 'en_core_web_sm' model
spacy.cli.download("en_core_web_sm")

# Load the installed model
nlp = spacy.load("en_core_web_sm")
