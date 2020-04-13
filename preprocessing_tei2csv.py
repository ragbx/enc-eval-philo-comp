from bs4 import BeautifulSoup
import lxml
import re
import csv
import os

def getListOfFiles(dirName):
    """
    Fonction qui renvoie sous forme de liste l'ensemble des fichiers
    d'un répertoire.
    """
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return sorted(allFiles)

def chunks(l, n):
    """
    Fonction qui découpe une liste l en n sous-listes.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def tei2csv(tei_file, csv_writer, param):
    """
    Fonction qui transforme un fichier TEI en fichier CSV
    """
    with open(tei_file, 'r') as tei:
        sp = BeautifulSoup(tei, 'lxml')

    type_pos = param['type_pos']

    data = {}
    # extraction des métadonnées
    data['id_piece'] = sp.find('text').get('id')
    print(f"{param['i']}/{param['j']} : {data['id_piece']}")
    data['auteur'] = sp.find('text').get('auteur')
    data['titre'] = sp.find('text').get('titre')
    data['date'] = sp.find('text').get('date')
    data['genre'] = sp.find('text').get('genre')
    data['inspiration'] = sp.find('text').get('inspiration')
    data['structure'] = sp.find('text').get('structure')
    data['type'] = sp.find('text').get('type')
    data['periode'] = sp.find('text').get('periode')
    data['taille'] = sp.find('text').get('taille')
    #data['nvers'] = sp.find('text').get('nvers')

    # traitement des lemmes
    lemmas = []
    for w in sp.find_all('w'):
        pos = w.find('txm:ana', {'type':'#frpos'})
        if type_pos.match(pos.get_text()):
            lemma = w.find('txm:ana', {'type':'#frlemma'})
            lemmas.append(lemma.get_text())

    lemmas_chunks = list(chunks(lemmas, param['chunks_size']))

    for ch in lemmas_chunks:
        data['lemmes'] = " ".join(ch)
        data['nlemmes'] = len(ch)
        csv_writer.writerow(data)

if __name__ == '__main__':
    tei_files = getListOfFiles('corpora/theatre_classique/xml_tagged')

    param = {
        # cf http://bfm.ens-lyon.fr/IMG/pdf/Cattex2009_2.0.pdf
        'type_pos': re.compile("^VER|NOM|ADJqua"),
        'chunks_size': 800,
        'result_file': 'corpora/all_VER_NOM_ADJqua_ok.csv'
    }

    with open(param['result_file'], mode='w') as csv_file:
        fieldnames = ['id_piece', 'auteur', 'titre', 'date', 'genre', 'inspiration', 'structure', 'type', 'periode', 'taille', 'nlemmes', 'lemmes']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        param['i'] = 0
        param['j'] = len(tei_files)
        for tei_file in tei_files:
            param['i'] += 1
            tei2csv(tei_file, writer, param)
