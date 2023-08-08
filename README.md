# ACL Papers parser
Script to parse contextual citation from ACL paper format.

## Dependency Setup
Setup python virtual environment and install the required package:
```
python -m venv acl-parser-env
source acl-parser-env/bin/activate
pip install -r requirements.txt
```
Next, we setup folders required by the script:
```
mkdir acl_papers acl_papers_tei citations
```

### Setup Grobid
Grobid is library to parse publications into components (such as abstract, citations, sections, etc) and convert the output in TEI format.
Full documentation can be found in https://grobid.readthedocs.io/en/latest/
First, we setup grobid using docker container as explained in https://grobid.readthedocs.io/en/latest/Grobid-docker/ (CRF-only image)
```
docker pull lfoppiano/grobid:0.7.3
docker run -t --rm --init -p 8070:8070 lfoppiano/grobid:0.7.3
```
Next, we setup the grobid python client (https://github.com/kermitt2/grobid_client_python)
```
git clone https://github.com/kermitt2/grobid_client_python
cd grobid_client_python
python3 setup.py install
```

The full contextual citation parser can be found in `contextual_cit_parser.py` which
1. Download and put all the publications that will be parsed under `acl_papers`
2. Run `python contextual_cit_parser.py` and the parsed citation can be found under `citations` folder.
The example input and output can be found in `examples`
The output `JSON` schema are as follows:
```
{
    "publication_detail": Publication,
    "abstract": string,
    "citations": [Citation]
}
```
with `Publication` schema is 
```
{
    "title": string,
    "authors": ["surname, forename"],
    "pub_date": string
}
```
and `Citation` schema is
```
{
    "citation_text": string (containing sentence with citation on it),
    "publication": Publication
}
```


