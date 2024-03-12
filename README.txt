------------------------------------READ ME---------------------------------------------------------------
NB : Ce code est adapté à la CCN Bureaux d'études techniques.
Au niveau de la ligne 95, nous avons crée un fichier Excel qui contient seulement la ligne
de la CCN des Bureaux d'études techniques pour des raisons de tests.
Pour que le code traite toute la liste des CCN, il suffit de changer le fichier 'information_Bureaux.xlsx'
par celui que nous avons crée 'CCN_ref.xlsx'.


1- Installer toutes ces bibliothèques avec pip install dans le terminal :

bs4
pandas
openpyxl
time
os
selenium
webdriver_manager.chrome
nltk
pdfplumber

2- Dans la ligne 46, il faut avoir le fichier 'page_exportee.html' dans le dossier. 
Ce fichier est la page html exportée de la liste de toutes les CCN.

3- Il faut avoir le fichier chromedriver.exe avec la bonne version de Chrome installé sur votre machine
PS : Faire attention aux MàJ automatiques de Google Chrome.

4- Au niveau de la ligne 178 il faut changer le chemin vers votre dossier.

5- Au niveau de la ligne 182 il faut changer le chemin qui pointe vers le fichier html.

6- Au niveau de la ligne 291 il faut changer le chemin qui pointe vers le fichier html.