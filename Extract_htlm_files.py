from bs4 import BeautifulSoup

import openpyxl
import time
import bs4
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import nltk
import pdfplumber
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer , PunktTrainer
from function_download_html import *

## CCN file created
# Path and names to files containing the names's CCN and their path
fichier_html = 'page_exportee.html'  # Remplacez par le nom de votre fichier HTML exporté
nom_fichier_excel = 'CCN_ref.xlsx'  # Nom du fichier Excel de sortie
ligne_depart = 967  # Ligne de départ pour l'analyse
informations = extraire_informations_html(fichier_html, ligne_depart)

# output foleder Path for the html content
dossier_export = 'export_html'

# Se connecter au site avec les identifiants
url_login = "https://securega.gestion-des-acces.fr/login?service=https%3a%2f%2fwww.elnet.fr%2fGa%2fLogin%3ffromHulk%3d%252fdocumentation%252fDocument%253fid%253dY5LSTCC-1"  # Remplacez par l'URL de connexion
identifiant = 'ELG7KLLSY'
mot_de_passe = '8KK9SD'

# Path of the webdriver
path_executable_webdriver = 'chromedriver.exe'

#---------------------------------------------------------------------------------------
# Charger le fichier Excel
wb = donwload_workbook(nom_fichier_excel)
ws = wb.active
ws = delete_row_from_workbook(ws, "Zoos")
# Remplacer les caractères spécifiques dans la colonne "Texte"
ws = clean_row_of_workbook_for_colonne_texte(ws)
# Enregistrer les modifications dans le même fichier Excel
wb.save(nom_fichier_excel)

#--------------------------------EXPORT HTML------------------------------------------
# Lire le fichier Excel avec les liens href
df_name_and_link_of_ccn = pd.read_excel(nom_fichier_excel)

# Create folder to export if it doesnot exist
if not os.path.exists(dossier_export):
    os.makedirs(dossier_export)

# Initialiser le navigateur Selenium
driver = get_initialization(path_executable_webdriver)
driver_connected = get_connection_to_website(driver, url_login, identifiant, mot_de_passe)

# Soumettre le formulaire de connexion
accept_button(driver_connected, 'id', 'soumettre', is_with_pause=True)

# Accepter les cookies s'il y a une fenêtre contextuelle
# Attendre 2 secondes pour que la fenêtre contextuelle s'affiche (ajustez le délai si nécessaire)
accept_button(driver_connected, 'id', '_tealiumModalClose', is_with_pause=True)
accept_button(driver_connected, 'id', 'didomi-notice-agree-button', is_with_pause=False)

# Parcourir chaque ligne du DataFrame
for _, row in df_name_and_link_of_ccn.iterrows():
    text = row['Texte']
    lien = row['Lien']

    # Naviguer vers le lien href
    driver.get(lien)
    scroll_all_page(driver)
    # Récupérer le contenu HTML généré par JavaScript
    content = extract_content(driver) 
    save_html_content_in_folder(text, content, path_export_folder=dossier_export) 

# Fermer le navigateur Selenium
driver.quit()