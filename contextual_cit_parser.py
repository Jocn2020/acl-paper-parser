from bs4 import BeautifulSoup
from grobid_client.grobid_client import GrobidClient

import json
import nltk
nltk.download('punkt')  # Download the required data if not already downloaded
from nltk.tokenize import sent_tokenize
import os
from pdb import set_trace as bp

def extract_paragraphs_with_grobid(pdf_file_path):
    client = GrobidClient(config_path="./grobid_client_python/config.json")
    test = client.process("processFulltextDocument", pdf_file_path, output="grobid_test/", consolidate_citations=True, tei_coordinates=True, force=True)
    print("successfully parse the pdf")

class Publication:
    def __init__(self, soup_object):
        self.title = soup_object.find('title').text
        self.authors = [f"{author.find('surname').text if author.find('surname') else ''}, {author.find('forename').text if author.find('forename') else ''}" 
                        for author in soup_object.select('author:has(persName)')]
        self.pub_date = soup_object.find('date').text if soup_object.find('date') else ''

    def to_json(self):
        return {
            'title': self.title,
            'authors': self.authors,
            'pub_date': self.pub_date
        }
class Citation:
    def __init__(self, publication, citation_text):
        self.publication = publication
        self.citation_text = citation_text
    
    def to_json(self):
        return {
            'citation_text': self.citation_text,
            'publication': self.publication.to_json()
        }

def extract_citations(xml_soup):
    # Get the text content of paragraphs
    contents = [div for div in xml_soup.select('div:has(p)')]
    citations = {}

    # map all xml target to cited papers
    cited_papers = xml_soup.find_all('biblStruct', attrs={"xml:id" : True})
    target_papers = {}
    for paper in cited_papers:
        target_papers[paper['xml:id']] = Publication(paper)

    # search for all reference details
    for content in contents:
        citation = content.find_all('ref', text=lambda text: text and 'et al' in text)
        for cit in citation:
            if cit.has_attr('target'): # some citation is not parsed properly / no link to the cited papers
                ref = cit['target'][1:]
                citations[cit.text] = target_papers[ref]

    return citations

def get_citation_text(xml_soup):
    # Load the spacy NLP model for English
    paragraph_text = ""
    contents = [div for div in xml_soup.select('div:has(p)')]
    for content in contents:
        for p in content.find_all('p'):
            paragraph_text += f'{p.text} '
    
    #@Todo : replace this nltk with spaCy to check the sentence parsing performance
    #nlp = spacy.load("en_core_web_sm")
    # Process the text using nltk
    doc = sent_tokenize(paragraph_text)

    # 1. one sentence before and after
    citation_text = []
    citation = ""
    for sent in doc:
        text = sent.strip()
        if citation != "":
            citation_text.append(citation + " " + text)
            citation = ""
    
        if "et al" in text:
            citation += text
    
    if citation != "":
        citation_text.append(citation)
    return citation_text

def read_tei_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Read the XML content
        xml_content = file.read()

    # Parse the XML content using BeautifulSoup with the 'xml' parser
    soup = BeautifulSoup(xml_content, 'xml')

    abstract_tag = soup.find('abstract')
    abstract = abstract_tag.text if abstract_tag else ''
    publication = Publication(soup.find('fileDesc'))

    # get all citations data
    citation_details = extract_citations(soup)
    
    # get all sentences that contains citation
    citation_sentences = get_citation_text(soup)
    
    citation_list = []
    for text in citation_sentences:
        for citation in citation_details:
            if citation in text:
                citation_list.append(Citation(citation_details[citation], text))
    return publication, abstract, citation_list     

            

# Example PDF file path (replace with your publication PDF)
pdf_folder_path =  'acl_papers'
extract_paragraphs_with_grobid(pdf_folder_path)

file_names = [f for f in os.listdir(pdf_folder_path) if os.path.isfile(os.path.join(pdf_folder_path, f))]
for file in file_names:
    # remove the pdf in file name
    file = ".".join(file.split('.')[:-1])
    publication, abstract, extracted_citations = read_tei_data(f'acl_papers_tei/{file}.tei.xml')

    # convert to json
    with open(f'citations/{file}.json', "w") as json_file:
        json_data = {
            'publication_detail': publication.to_json(),
            'abstract': abstract,
            'citations': [cit.to_json() for cit in extracted_citations]
        }
        json.dump(json_data, json_file)