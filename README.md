8Q_code
=======

work with LDA

1) pdfParser.py 
parse PDF documents and prepare structure with Title and Abstarct
input: path to forder with library
output: .txt file near each PDF wile with abstract


2) corpusPreparation.py
prepares corpus with all data
input: path to forder with library
output: abstracts.json

3) buildModel.py
builds
- Dictionary
- TF-IDF model
- Index
- LDA model
input: abstracts.json
output: models

4) searcher.py
for particular SearchQuery builds all data
input: models
output:
- information about clusters
- information about papers

5) socketServer.py
runs searcher.py and answeres SearchQueries