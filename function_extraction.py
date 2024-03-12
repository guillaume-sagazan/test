import re
import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, ResultSet, Tag
from typing import Union, List, Any
import logging


def set_up_logging(path: str):
    # Configuration des logs
    logging.basicConfig(
    level=logging.DEBUG,  # Niveau minimum des logs à afficher
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format des messages de log
    handlers=[
        #logging.StreamHandler(),  # Affiche les logs dans la console
        logging.FileHandler(os.path.join(path, 'log.txt'))  # Écrit les logs dans un fichier
            ])

def import_dictionary_tabs(path: str) -> dict:
    """Import the dictionary used to resherche word"""
    onglets = pd.read_excel(path, sheet_name=None)
    return onglets 

def get_dictionary_of_tested_words(dict_tabs: dict) -> dict:
    """
    Return a new dictionary that contains information on the type of notion studied
        for the keys and for the values a dictionary of the tested word for the category : 
        title, table and paragraph in the form of list.
    """
    dict_notion = {}
    for key in dict_tabs.keys():
        dict_tested_word = {}
        df_key = dict_tabs[key]

        for column in df_key.columns:
            table_word = df_key[column].dropna()
            list_tested_word_column = list(table_word)
            update_dict(list_tested_word_column, column, dict_tested_word)
        dict_notion[key] = dict_tested_word
    return dict_notion

def extract_suffix_files(name_file: str) -> str:
    list_name_split = name_file.split(".")
    name_suffix = "_".join(list_name_split[:-1])
    return name_suffix

def save_soup_object(soup):
    # Obtenir la version formatée et lisible du contenu HTML
    formatted_html = soup.prettify()

    # Écrire le contenu formaté dans un fichier
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(formatted_html)

def extract_name_folder(path: str) -> List[str]:
    """
    Extract the name of the file in the folder specify in path
        Returns a list of name of files
    """
    list_name_fichier = []
    for nom_fichier in os.listdir(path):
        path_complet = os.path.join(path, nom_fichier)
        if os.path.isfile(path_complet):  # Vérifier si c'est un fichier (pas un sous-dossier)
            list_name_fichier.append(nom_fichier)
    return list_name_fichier

def load_htlm(path: str) -> str:
    """Load the HTML file associated with the path of the input"""
    with open(path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    return html_content

def update_dict(
        elm_to_add: Any,
        expression: str,
        dict_text: dict
        ) -> dict:
    """Update the dictionary in input with the value elm_to_add for the keys"""
    if type(elm_to_add) == list:
        elm_to_add = elm_to_add
    else:
        elm_to_add = [elm_to_add]    
    if expression in dict_text.keys():
        dict_text[expression] += elm_to_add
    else:
        dict_text[expression] = elm_to_add
    return dict_text

def create_parser(html_content: str):
    """Create object parser of htlm"""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def catch_paragraphs(
        soup,
        etat_logging: List[Any]
        ):
    """Detecter les éléments qui contiennent du text"""
    try:
        paragraphs_extracted = soup.find_all(["div", "article", "p", "span"]) #  string=True
    #paragraphs = [elm_paragraph.text for elm_paragraph in paragraphs_extracted if elm_paragraph]
    except ValueError as e:
        logging.error(f"{e}. etat_logging: {etat_logging}")
    return paragraphs_extracted


def catch_list(
        soup,
        etat_logging: List[Any]
        ):
    """Detecter les listes : libre, ordonnée"""
    try:
        lists = soup.find_all(['li', 'ol', 'ul'])  # Trouve tous les éléments <p>
    except ValueError as e:
        logging.error(f"{e}. etat_logging: {etat_logging}")
    return lists

def catch_other(
        soup,
        content_paragraph: List[str],
        content_table: List[str],
        content_list: List[str],
        etat_logging: List[Any]
        ):
    """Detecter les cas que ne sont pas pris dans les autre cas de figure"""
    try:
        text = []
        if not content_paragraph and not content_table and not content_list:
            text = [soup.get_text(strip=True)]  
    except ValueError as e:
        logging.error(f"{e}. etat_logging: {etat_logging}")
    return text

def catch_tables(
        soup,
        etat_logging: List[Any]
        ):
    """Detecter les tables"""
    try:
        tables = soup.find_all('table')  # Trouve tous les éléments <table>
    except ValueError as e:
        logging.error(f"{e}. etat_logging: {etat_logging}")
    return tables

def catch_elmnt(soup, elm: str):
    """Detecter les elements selectionnes
        Don't use
    """
    groupe_elm = soup.find_all(elm)  # Trouve tous les éléments <elm>
    return groupe_elm

def extract_header_to_check(table) -> List[str]:
    """Extract the header of a table"""
    # Trouver toutes les balises <th> (en-têtes)
    en_tetes = table.find_all('th')
 
    # Créer une liste pour stocker les en-têtes de colonne
    en_tetes_colonne = []
 
    # Parcourir les en-têtes
    for en_tete in en_tetes:
        # Obtenir le texte de l'en-tête
        texte_en_tete = en_tete.get_text()
     
        # Ajouter le texte à la liste des en-têtes de colonne
        en_tetes_colonne.append(texte_en_tete)
    return en_tetes_colonne

def extract_metadata_headers(header):
    text = header.get_text(strip=True, separator="|||").split('|||')[0]
    colspan = int(header.get('colspan', 1))
    rowspan = int(header.get('rowspan', 1))
    return text, colspan, rowspan

def extract_header_structure(thead) -> List[tuple]:
    """
    Extract the text and their position in the table'header
    """
    header_structure = []
    if thead is not None:
        for enu_rows, tr in enumerate(thead.find_all('tr')):
            if tr is not None:
                for header in tr.find_all(['th', 'td']):
                    header_text, header_colspan, header_rowspan = extract_metadata_headers(header)
                    header_structure.append((header_text,
                                            header_colspan,
                                            header_rowspan,
                                            enu_rows))
    return header_structure

def adapth_header_to_extract(header_structure: List[tuple]) -> dict:
    """Adapte the meta data in order to give them the correct order of the text"""
    data_header = {}
    for header_text, header_colspan, header_rowspan, indicateur_rows in header_structure:
        for row in range(header_rowspan):
            data_header = update_dict([header_text]*header_colspan,
                                      row + indicateur_rows,
                                      data_header)
    column_names = list( zip(*data_header.values()))
    return column_names

def extract_header(table) -> List[str]:
    """Extract the header of a table"""
    try:
        thead = table.find('thead')
        header_structure = extract_header_structure(thead)
        column_names = adapth_header_to_extract(header_structure)
    except ValueError as e:
        logging.warning(e)
        thead = table.find('thead')
        header_structure = extract_header_structure(thead)
        column_names = adapth_header_to_extract(header_structure)
    return column_names

def extract_cell_to_check(table) -> List[str]:
    """Extract the data of a table"""
    # Trouver toutes les balises <td> (colonne)
    cellules = table.find_all('td')
    # Créer une liste pour stocker les données de chaque ligne
    donnees_lignes = []
  
    # Parcourir les cellules de la table
    for cellule in cellules:
        # Obtenir le texte à l'intérieur de la cellule
        texte_cellule = cellule.get_text()
      
        # Ajouter le texte à la liste des données de ligne
        donnees_lignes.append(texte_cellule)
    return donnees_lignes

def general_rule_of_extraction_row_data_from_table(
        cells: List[str]
        ) -> List[str]:
    row_data = [cell.get_text(separator='|||',
                              strip=True).split('|||')[0]
                for cell in cells]
    return row_data

def specific_rule_of_extraction_row_data_from_table(
        cells: List[str]
        ) -> List[str]:
    """use when the table contains some note page"""
    row_data = []
    for cell in cells:
        row_data += [cell.get_text()]
    return row_data

def get_row_data_from_table(
        cells: List[str],
        header_list: List[str]
        ) -> List[str]:
    number_of_data = len(header_list)
    row_data = general_rule_of_extraction_row_data_from_table(cells)
    if len(row_data) != number_of_data:
        row_data = specific_rule_of_extraction_row_data_from_table(cells)
    return row_data

def extract_cell(
        table,
        header_list: List[str]
        ) -> List[str]:
    """Extract the data of a table"""
    data_cell = []
    if table is not None:
        list_tbody = table.find_all('tbody')
        if list_tbody is not None:
            if len(list_tbody) == 1:
                data_rows = list_tbody[-1].find_all('tr')
                for row in data_rows:
                    cells = row.find_all('td')
                    row_data = get_row_data_from_table(cells, header_list)
                    data_cell.append(row_data)
            else:
                data_rows = list_tbody[-1].find_all('tr')
                for row in data_rows:
                    cells = row.find_all('td')
                    row_data = get_row_data_from_table(cells, header_list)
                    data_cell.append(row_data)
    return data_cell

def get_dataframe_valide(
        column_names: List[str],
        data_cells: List[str],
        str_title_arborescence: str
        ) -> pd.DataFrame:
    """
    Return datafram that contains the columns names
    and the data corresponded after adaptaion in order to fit the number of columns
    """
    try:
        max_length = max([len(sublist) for sublist in data_cells])
        if max_length == len(column_names):
            dict_df_columns = {
                (str_title_arborescence, columns_name): [] for columns_name in column_names
                }
            data_cells_adapted = [row + [None]*(max_length-len(row)) for row in data_cells]
            df_table = pd.DataFrame(dict_df_columns)
            for enu, row in enumerate(data_cells_adapted):
                df_table.loc[enu] = row
        else:
            message_warning = f"the shape of column and the data does not fit.\
                               max_length = {max_length} and len(column_names) : {len(column_names)}"
            logging.warning(message_warning)
            df_table = [column_names, data_cells]
    except ValueError as e:
        logging.error(e)
    return df_table

def dell_doublon(list_of_text: List[str]) -> List[str]:
    list_without_doublon = list(set(list_of_text))
    return list_without_doublon

def extract_text_from_paragraph(paragraphs) -> List[str]:
    """Extract the text from a paragraph"""
    #text = paragraph.get_text(skip=True, string=True)
    try:
        if isinstance(paragraphs, ResultSet):
            text = []
            for paragraph in paragraphs:
                text += paragraph.get_text(strip=True, separator="|||").split('|||')
        elif isinstance(paragraphs, str):
            text = paragraph.get_text(strip=True, separator="|||").split('|||')
        else:
            text = []
        text = dell_doublon(text)
    except ValueError as e:
        logging.error(paragraph)
    return text

def extract_all_balise_tr(table) -> List[str]:
    """Extract the data of a table with balise tr"""
    # Trouver toutes les balises <td> (colonne)
    rows = table.find_all('tr')
    # Créer une liste pour stocker les données de chaque ligne
    data_rows = []
    
    # Parcourir les cellules de la table
    for row in rows:
        # Obtenir le texte à l'intérieur de la cellule
        text_rows = row.get_text(separator="//")
        
        # Ajouter le texte à la liste des données de ligne
        data_rows.append(text_rows)
    return data_rows


def search_regex_in_list(
        list_word: str,
        word_search: str
        ) -> bool:
    """
    Search the regex in the list of text present in input
        Returns : bool that indicates if the word is present in the elment of 
    """
    # Utiliser une expression régulière pour chercher le mot dans chaque élément de la liste
    is_word_find = any(re.search(r'\b' + re.escape(word_search) + r'\b', str(mot), re.IGNORECASE) 
                    for mot in list_word)
    return is_word_find

def find_argument_of_list_with_specific_elmnt(list_test: List[Any],
                                              expression: str
                                              ) -> List[int]:
    """Create a list that contains the indice of elmnt present in the test list"""
    list_indices_present = [index for index, text in enumerate(list_test) 
                            if re.search(r'\b' + re.escape(expression) + r'\b', str(text), re.IGNORECASE) 
                            is not None]
    return list_indices_present

def find_value_of_list_with_specific_elmnt(list_text: List[str],
                                           list_indice_text: List[int]
                                           ) -> dict:
    """Create a list that contains the elmnt present in the test list"""
    list_text_extract = [list_text[indice] for indice in list_indice_text]
    return list_text_extract

def search_list_of_regex_in_test(
        text: str,
        list_regex_search: List[str]
        ) -> bool:
    """
    Search a list of word in the text
        Returns : bool that indicates if the word is present in the elment of 
    """
    # Utiliser une compréhension de liste pour vérifier chaque expression de recherche
    list_word_find = [re.search(r'\b' + re.escape(expression) + r'\b', str(text), re.IGNORECASE) 
                      is not None for expression in list_regex_search]
    return list_word_find

def check_new_informations_valid(
        list_hash_incorporate: List[int],
        text_check: str
        ) -> bool:
    """Return booland that indicates if the element is already consume"""
    try:
        hash_tested = hash(text_check)
        is_word_in_list = not(hash_tested in list_hash_incorporate)
        list_hash_incorporate += [hash_tested] * int(is_word_in_list)
    except Exception as e:
        logging.error(e)
        raise ValueError(e)
    return is_word_in_list, list_hash_incorporate

def check_previous_title(
        liste_title: List[str],
        title_tested: str,
        str_title_arborescence: str
        ) -> bool:
    """Check if the title is already present in the title's list consume"""
    title_tested_full = str_title_arborescence + title_tested
    is_title_prevously_use = not(title_tested_full in liste_title)
    liste_title += [title_tested_full] * int(is_title_prevously_use)
    return is_title_prevously_use, liste_title

def search_word_not_consume(
        list_hash_incorporate: List[int],
        list_text_check: List[str]
        ) -> bool:
    """Return if all element is already present in the dictionary final"""
    try:
        list_bool_word_check_already_consume = []
        for text_check in list_text_check:
            is_word_in_list, list_hash_incorporate = check_new_informations_valid(
                                                                        list_hash_incorporate,
                                                                        text_check)
            list_bool_word_check_already_consume.append(is_word_in_list)
    except Exception as e:
        logging.error(e)
        raise ValueError(e)
    return any(list_bool_word_check_already_consume), list_hash_incorporate

def fill_dict_with_text_contains_regex_for_paragraph(
        text_check: str,
        word_tested: str,
        dict_text: dict,
        is_data_valid: bool,
        str_title_arborescence: str
        ) -> dict:
    """
    Fill the input dictionary with a list of text components from 'text_check' 
    corresponding for the 'word_tested'.
    Only if the word tested is find in text_check.
    Only use for paragraphe
    """
    if is_data_valid:
        indice_elm_contains_elm = find_argument_of_list_with_specific_elmnt(text_check,
                                                                            word_tested)
        list_text_extract = find_value_of_list_with_specific_elmnt(text_check,
                                                                   indice_elm_contains_elm)
        dict_update = update_dict(
            [list_text_extract, str_title_arborescence],
            word_tested,
            dict_text
            ) 
    else:
        dict_update = dict_text
    return dict_update

def adapt_list_compare_to_reference_list(
        header_list: int,
        list_to_adapt: List[Any],
        list_of_list_reference: List[Any]
        ) -> List[Any]:
    """Create a new list with the same length as the list of reference """
    length_reference = len(header_list)
    nbr_elmnt_to_complete = length_reference - len(list_to_adapt)
    if  list_of_list_reference != [] and len(list_of_list_reference[-1]) != length_reference:
        list_to_adapt = adapt_list_compare_to_reference_list(
            header_list, list_to_adapt, list_of_list_reference[:-1])[1:]
        return list_to_adapt
    else:
        if  list_of_list_reference != []:
            list_to_adapt = list_of_list_reference[-1][0:nbr_elmnt_to_complete] + list_to_adapt
    return list_to_adapt

def transform_header_and_cell_into_dataframe(
        header_list: List[str],
        structured_data: List[str]
        ):
    """Transform the header and cell lists into a datafram after an adaptation if necessary"""
    if len(structured_data[2:]) == len(header_list):
        list_output_value = []
        list_to_add_output = []
        for data in structured_data[2:]:
            list_structured_row = data.split("//")
            list_structured_completed_row = \
                adapt_list_compare_to_reference_list(
                    header_list,
                    list_structured_row,
                    list_to_add_output
                    )
            list_to_add_output.append(list_structured_completed_row)
        list_output_value += list_to_add_output
        df_structured_table = pd.DataFrame(list_output_value[:len(header_list)],
                                           columns=header_list)
    else:
        message_error = "le format des tables ne convient pas"
        logging.warning(message_error)
        df_structured_table = structured_data
    return df_structured_table

def fill_dict_with_dataframe_contains_regex_for_table(
        header_list: List[str],
        cell_list: List[str],
        expression: str,
        dict_table: dict,
        is_data_valid: bool,
        str_title_arborescence: str
        ) -> dict:
    """
    Fill the input dictionary with a list of text components from 'text_check' 
        corresponding for the 'word_tested'.
    Only if the word tested is find in text_check.
    Only use for table
    """
    try:
        if is_data_valid:
            df_structured_table = get_dataframe_valide(
                header_list,
                cell_list,
                str_title_arborescence
                )
            dict_update = update_dict(
                df_structured_table,
                expression,
                dict_table
                )
        else:
            dict_update = dict_table
    except Exception as e:
        logging.error(e)
        raise e
    return dict_update

def fill_dict_with_dataframe_contains_regex_for_title(
        dict_from_regex_to_text_title: dict,
        dict_section: dict,
        expression: str,
        str_title_arborescence: str
        ):
    """Fill the input dictionary with paragph and table information"""
    try:
        dict_title = update_dict(dict_section['title'],
                                 'title',
                                 {})
        dict_paragraph = update_dict(dict_section['paragraph'],
                                     'paragraph',
                                     dict_title)
        dict_table = update_dict(dict_section['table'],
                                 'table',
                                 dict_paragraph)
        dict_list = update_dict(dict_section['list'],
                                 'list',
                                 dict_table)
        dict_other = update_dict(dict_section['other'],
                                 'other',
                                 dict_list)
        dict_arborescence = update_dict([str_title_arborescence],
                                 'title_arborescence',
                                 dict_other)
        dict_update = update_dict(dict_arborescence,
                                  expression,
                                  dict_from_regex_to_text_title)
    except Exception as e:
        logging.error(e)
        raise e
    return dict_update

def count_table(table):
    """Compte the nombre of table inside a table"""
    return len(table)

def dell_doublon_on_list_of_dict(
        dict_of_text: dict,
        expression: str
        ) -> dict:
    """
    Transform the value of the dictionary content for the expression to dell the duplicata
        present in the dictionary value
    """
    try:

        if expression in dict_of_text.keys():
            list_value_dict = np.array(dict_of_text[expression]).flatten()
            
            list_value_dict_unique = np.unique(list_value_dict)
            dict_of_text[expression] = list(list_value_dict_unique)
    except Exception as e:
        logging.error(e)
        raise e
    return dict_of_text

def group_by_section(soup):
    """get all title and content for the head section"""
    # Trouver toutes les balises de titre (<h1>, <h2>, <h3>, ...)
    list_tag = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    title_tags = soup.find_all(list_tag)

    sections = []
    if title_tags is not None:
        for tag in title_tags:
            section = {
                'title': tag.get_text(strip=True),
                'content': [],
                'tag': tag.name,
                'attrs': tag.attrs
                }
            content_tag = tag.find_next_sibling()
            while content_tag and content_tag.name not in list_tag:
                section['content'].append(content_tag)
                content_tag = content_tag.find_next_sibling()
            sections.append(section)
    return sections

def extract_meta_data_from_section(
        section: List[Any],
        etat_logging: List[Any]
        ):
    # extract meta data
    try:
        if "tag" in section:
            tag = section['tag']
        else:
            tag = "h6" #default value (lowest)
        if "attrs" in section:
            if "class" in section['attrs']:
                typ_class = "_".join(section['attrs']['class'])
            else:
                typ_class = ""
        else:
                typ_class = ""
        identifiant = tag + typ_class
    except ValueError as e:
        logging.error(f"{e}. etat_logging: {etat_logging}")
    return identifiant

def init_dict_for_key_with_empty_list(
        dict_to_check: dict,
        key_word: str
        ) -> dict:
    """
        Initialize a dictionary for a specific key if not in the dictionary tested
    if not return the same object.
    """
    if key_word not in dict_to_check.keys():
        dict_to_check[key_word] = []
    return dict_to_check

def fill_dict_of_data_not_nul(
        list_tested: List[Any],
        dict_to_add: dict,
        key: str
        ) -> dict:
    """Add liste_tested to dict_to_ass only if their are not empty"""
    if list_tested != []:
        dict_to_add[key] = list_tested
    return dict_to_add

def extract_information_from_section(
        section: List[Any],
        etat_logging: List[Any]
        ) -> dict:
    """
    Configurate and extract information from a section
    Apply a reshearch method in the tested content form a section
    """
    output_dict = {
        'identifiant': '',
        'title': '',
        'paragraph': [],
        'table': [],
        'list': [],
        'other': []
        }

    # extract content
    title = section['title']
    list_content = section['content']
    
    # Initialisation 'identifiant'
    output_dict['identifiant'] =  extract_meta_data_from_section(section, etat_logging)
    output_dict['title'] = title

    for each_content in list_content:
        content_paragraph = catch_paragraphs(each_content, etat_logging)
        content_table = catch_tables(each_content, etat_logging)
        content_list = catch_list(each_content, etat_logging)
        content_other = catch_other(each_content,
                                    content_paragraph,
                                    content_table,
                                    content_list,
                                    etat_logging)

        output_dict = fill_dict_of_data_not_nul(content_table, output_dict, 'table')
        output_dict = fill_dict_of_data_not_nul(content_paragraph, output_dict, 'paragraph')
        output_dict = fill_dict_of_data_not_nul(content_list, output_dict, 'list')
        output_dict = fill_dict_of_data_not_nul(content_other, output_dict, 'other')

    return output_dict

def add_position_to_dict(
        dict_position: dict,
        is_regex_present: bool,
        indice_section: str,
        type_of_localisation: str
        ):
    """
    Depreceted.
    Update the dict to add the indice of the setion if the regex is in the section
    """
    if not(type_of_localisation in dict_position.keys()):
        message_error = "the type_of_localisation variable doesnot correspond: "
        message_error += f"{type_of_localisation}"
        raise ValueError(message_error)
    if is_regex_present:
        if not(indice_section in dict_position[type_of_localisation]):
            dict_position[type_of_localisation].append(indice_section)

def return_indice_of_true_if_not_nul(dict_indice: dict) -> int or None:
    list_tested = dict_indice[True]
    if not(list_tested):
        result = None
    else:
        result = list_tested[-1]
    return result

def extract_indice_that_contains_regex_in_table(
        dict_section: dict,
        regex_tested: str
        ):
    """return the the indice that is the larger and contains the regex_tested"""
    dict_indice_present = {True: [], False: []}
    for indice_table, table in enumerate(dict_section['table']):
        # Extrait les texts des tableaux
        header_list = extract_header_to_check(table)
        cell_list = extract_cell_to_check(table)
        # Realise la recherche pour les regex souhaités
        is_word_tested_in_text_header = search_regex_in_list(header_list, regex_tested)
        is_word_tested_in_text_cell = search_regex_in_list(cell_list, regex_tested) 
        is_word_tested_in_text = is_word_tested_in_text_cell or is_word_tested_in_text_header
        dict_indice_present[is_word_tested_in_text].append(indice_table)
        # if regex_tested == "NAF":
        #     print(is_word_tested_in_text_header, is_word_tested_in_text_cell, header_list, dict_indice_present)
    result_indice = return_indice_of_true_if_not_nul(dict_indice_present)
    is_indice_exist = result_indice != None
    return result_indice, is_indice_exist

def update_paragraph_dictionary_if_not_exists(
        words_tested: str,
        dict_section: dict,
        dict_paragraph: dict,
        list_hash_incorporate: List[int],
        str_title_arborescence: str
        ):
    """
    Updates a dictionary by adding the text if it's not already associated with the given word.
    """
    paragraphs_tested = extract_text_from_paragraph(dict_section['paragraph'])
    is_word_tested_in_text_paragraph = search_regex_in_list(paragraphs_tested, words_tested)
    is_word_not_consume, list_hash_incorporate = search_word_not_consume(
                                                        list_hash_incorporate,
                                                        paragraphs_tested,
                                                        )
    
    is_data_paragraph_valid = is_word_tested_in_text_paragraph & is_word_not_consume

    dict_paragraph = fill_dict_with_text_contains_regex_for_paragraph(paragraphs_tested,
                                                                      words_tested,
                                                                      dict_paragraph,
                                                                      is_data_paragraph_valid,
                                                                      str_title_arborescence
                                                                      )
    return dict_paragraph, list_hash_incorporate

def update_table_dictionary_if_not_exists(
        words_tested: str,
        dict_section: dict,
        dict_table: dict,
        list_hash_incorporate: List[int],
        str_title_arborescence: str
        ):
    """
    Updates a dictionary by adding the table if it's not already associated with the given word.
    """
    indice_of_table, is_indice_exist = extract_indice_that_contains_regex_in_table(dict_section,
                                                                                   words_tested)
    if is_indice_exist:
        table_tested = dict_section['table'][indice_of_table]
        header_list = extract_header(table_tested)
        cell_list = extract_cell(table_tested, header_list)
        is_word_not_consume, list_hash_incorporate = search_word_not_consume(
                                                         list_hash_incorporate,
                                                         header_list
                                                         )
        is_data_table_valid = is_word_not_consume
        dict_table = fill_dict_with_dataframe_contains_regex_for_table(
                                                header_list,
                                                cell_list,
                                                words_tested,
                                                dict_table,
                                                is_data_table_valid,
                                                str_title_arborescence)
    return dict_table, list_hash_incorporate

def update_title_dictionary_if_not_exists(
        words_tested: str,
        dict_section: dict,
        dict_title: dict,
        list_title: List[int],
        str_title_arborescence: str
        ) -> dict and List:
        """
        Updates a dictionary by adding the title if it's not already associated with the given word.
        """
        title_tested = [dict_section['title']]
        is_title_previous_use, list_title = \
            check_previous_title(list_title,
                                 dict_section['title'],
                                 str_title_arborescence)
        is_word_tested_in_text_title = search_regex_in_list(title_tested, words_tested)
        # if is_word_tested_in_text_title:
        #     print(str_title_arborescence, words_tested, is_word_tested_in_text_title)
        if is_title_previous_use & is_word_tested_in_text_title:
            dict_title = fill_dict_with_dataframe_contains_regex_for_title(
                                            dict_title,
                                            dict_section,
                                            words_tested,
                                            str_title_arborescence)
        return dict_title, list_title

def get_text_from_paragraph_containing_words(
        dict_words_to_test: dict,
        dict_section: dict,
        dict_paragraph: dict,
        dict_hash_incorporate_paragraph: dict,
        str_title_arborescence: str,
        etat_logging: List[str]
    ):
    """
    Search and Extract from paragraph tested with the words searched
    Args:
        dict_words_to_test: dict that containing the list of words to test
        dict_section: dict that containing the paragraph to test
        dict_paragraph: dict that containing the text that contains for the key associated
        dict_hash_incorporate_paragraph: dict to verify if the information has not already been
            integrated
        Information for the logging
        list_arborescence: list that contain the arborescence of the title
        etat_loggign: List of str that contains :
            radical: str
            indice_section: int
            key_words_to_test: str
    Returns:
        dict_paragraph: dict that containing the text that contains for the key associated
        dict_hash_incorporate_paragraph: update dict_hash_incorporate_paragraph in input
    """
    if not('paragraph' in dict_words_to_test.keys()):
        message_error = f"paragraph is not in the dataframe of tested word. \
                        Information relitif of the execution {etat_logging}"
        logging.error(message_error)
        raise ValueError(message_error)
    for word_to_test in dict_words_to_test['paragraph']:
        dict_hash_incorporate_paragraph = init_dict_for_key_with_empty_list(
                                            dict_hash_incorporate_paragraph,
                                            word_to_test)
        dict_paragraph, dict_hash_incorporate_paragraph[word_to_test] = \
                    update_paragraph_dictionary_if_not_exists(
                        word_to_test,
                        dict_section,
                        dict_paragraph,
                        dict_hash_incorporate_paragraph[word_to_test],
                        str_title_arborescence)
    return dict_paragraph, dict_hash_incorporate_paragraph

def get_text_from_table_containing_words(
        dict_words_to_test: dict,
        dict_section: dict,
        dict_table: dict,
        dict_hash_incorporate_table: dict,
        str_title_arborescence: str,
        etat_logging: List[str]
    ):
    """Search and Extract from table tested with the words searched
    Args:
        dict_words_to_test: dict that containing the list of words to test
        dict_section: dict that containing the table to test
        dict_table: dict that containing the text that contains for the key associated
        dict_hash_incorporate_table: dict to verify if the information has not already been
            integrated
        Information for the logging
        list_arborescence: str that contain the arborescence of the title 
        etat_loggign: List of str that contains :
            radical: str
            indice_section: int
            key_words_to_test: str
    Returns:
        dict_table: dict that containing the text that contains for the key associated
        dict_hash_incorporate_table: update dict_hash_incorporate_table in input
    """
    if not('table' in dict_words_to_test.keys()):
        message_error = f"table is not in the dataframe of tested word.\
                         information is {etat_logging}"
        logging.error(message_error)
        raise ValueError(message_error)
    for word_to_test in dict_words_to_test['table']:
        dict_hash_incorporate_table = init_dict_for_key_with_empty_list(
                                            dict_hash_incorporate_table,
                                            word_to_test)
        dict_table, dict_hash_incorporate_table[word_to_test] = \
                update_table_dictionary_if_not_exists(
                        word_to_test,
                        dict_section,
                        dict_table,
                        dict_hash_incorporate_table[word_to_test],
                        str_title_arborescence)
    return dict_table, dict_hash_incorporate_table

def get_text_from_title_containing_words(
        dict_words_to_test: dict,
        dict_section: dict,
        dict_title: dict,
        dict_hash_incorporate_title: dict,
        str_title_arborescence: str,
        etat_logging: List[str]
    ):
    """Search and Extract from title tested with the words searched
    Args:
        dict_words_to_test: dict that containing the list of words to test
        dict_section: dict that containing the title to test
        dict_title: dict that containing the text that contains for the key associated
        dict_hash_incorporate_title: dict to verify if the information has not already been
            integrated
        Information for the logging
        str_title_arborescence: str that contains information in title
        etat_loggign: List of str that contains :
            radical: str
            indice_section: int
            key_words_to_test: str
    Returns:
        dict_title: dict that containing the text that contains for the key associated
        dict_hash_incorporate_title: update dict_hash_incorporate_title in input
    """
    if not('title' in dict_words_to_test.keys()):
        message_error = f"table is not in the dataframe of tested word.\
                         information is {etat_logging}"
        logging.error(message_error)
        raise ValueError(message_error)
    for word_to_test in dict_words_to_test['title']:
        dict_hash_incorporate_title = init_dict_for_key_with_empty_list(
                                            dict_hash_incorporate_title,
                                            word_to_test)
        dict_title, dict_hash_incorporate_title[word_to_test] = \
            update_title_dictionary_if_not_exists(
                    word_to_test,
                    dict_section,
                    dict_title,
                    dict_hash_incorporate_title[word_to_test],
                    str_title_arborescence)
    return dict_title, dict_hash_incorporate_title

def add_elm_to_dict_notion(
        dict_words_of_paragraph_to_add: dict,
        dict_words_of_table_to_add: dict,
        dict_words_of_title_to_add: dict,
        key: str,
        dict_to_update: dict
        ) -> dict:
    """Add elements only for the specific notion dictionary"""
    if key not in dict_to_update.keys(): 
        dict_words_to_add = {
                            'paragraph': dict_words_of_paragraph_to_add,
                            'table': dict_words_of_table_to_add,
                            'title': dict_words_of_title_to_add
                            }
        dict_to_update[key] = dict_words_to_add
    else:
        message_error = "The value of key proposed have aleady assign. \
            Check in the soucre of the dictionary if the onglet's name are not duplicate."
        logging.error(message_error)
        raise ValueError(message_error)
    return dict_to_update

def get_export_folder_path(
        path_source: str,
        export_folder: str
        ) -> str:
    path_export_folder = os.path.join(path_source, export_folder)
    return path_export_folder

def get_new_columns_multindex(
                              key: str,
                              actual_column_names: List[str]
                              ) -> pd.MultiIndex:
    list_column_names_multindex = []
    for column_name in actual_column_names:
        if isinstance(column_name, str):
            column_name = (column_name,)
        if isinstance(column_name, list):
            column_name = (column_name,)
        list_column_names_multindex.append( (key,) + column_name )
    multi_index_columns = pd.MultiIndex.from_tuples(list_column_names_multindex)
    return multi_index_columns

def get_new_dataframe_with_key_as_first_level_header(
        dataframe: pd.DataFrame,
        key: str
        ) -> pd.DataFrame:
    try:
        dataframe_copy = dataframe.copy()
        new_col_names = get_new_columns_multindex(key, dataframe_copy.columns)
        dataframe_copy.columns = new_col_names
    except ValueError as e:
        logging.error(e)
        raise e
    return dataframe_copy

def get_number_row_in_dataframe(dataframe: pd.DataFrame) -> int:
    try:
        rows_of_data = len(dataframe)

        list_col = dataframe.columns
        rows_of_header = len(list_col)
        for elm_col in list_col:
            if isinstance(elm_col, tuple) or isinstance(elm_col, list):
                rows_of_header = len(elm_col)
    except ValueError as e:
        logging.error(e)
        raise e
    return rows_of_header + rows_of_data

def get_number_col_in_dataframe(dataframe: pd.DataFrame) -> int:
    try:
        list_col = dataframe.columns
        nbr_of_header = len(list_col)
    except ValueError as e:
        logging.error(e)
        raise e
    return nbr_of_header

def get_metadata_to_statistic(
        file_names: str,
        notion_searched: str,
        source: str,
        dict_stat: dict
        ) -> dict:
    dict_stat["file names"] += [file_names]
    dict_stat["notion searched"] += [notion_searched]
    dict_stat["source"] += [source]
    return dict_stat

def get_dictionary_statistic_empty() -> dict:
    dict_stat = {
        "file names": [],
        "notion searched": [],
        "source": [],
        "word found": [],
        "count word found": []
        }
    return dict_stat

def get_dataframe_statistic_empty() -> pd.DataFrame:
    dataframe_statistic = pd.DataFrame.from_dict(get_dictionary_statistic_empty())
    return dataframe_statistic

def get_dataframe_statistic(
        dict_notion: str,
        file_names: str
        ) -> pd.DataFrame:
    dict_stat = get_dictionary_statistic_empty()
    for notion_searched, dict_type_of_elm_found in dict_notion.items():
        for type_of_content, dict_of_elm_found in dict_type_of_elm_found.items():
            if dict_of_elm_found:
                for key_word_found, list_text_found in dict_of_elm_found.items():
                    dict_stat = get_metadata_to_statistic(file_names,
                                                          notion_searched,
                                                          type_of_content,
                                                          dict_stat)
                    nbr_elm_find = len(list_text_found)
                    dict_stat["word found"] += [key_word_found]
                    dict_stat["count word found"] += [nbr_elm_find]
    dataframe_statistic = pd.DataFrame.from_dict(dict_stat)
    return dataframe_statistic

def save_dict_to_files_xlsx(
        list_dict_to_export: List[dict],
        key_words_to_test: str,
        writer: pd.ExcelWriter
        ) -> None:
    """
    Save the dictionary into a files .xlsx
        For each keys of the dictionary : dict_notion a new sheet is created
    """
    nbr_cols_aleady_fill = 0
    for dict_to_export in list_dict_to_export:
        for key, value in dict_to_export.items():
            if  value and all(isinstance(item, pd.DataFrame) for item in value):
                for dataframe in value:
                    dataframe_value = get_new_dataframe_with_key_as_first_level_header(
                                            dataframe, key)
                    nbr_cols = get_number_row_in_dataframe(dataframe_value)
                    dataframe_value.to_excel(
                        writer,
                        sheet_name = key_words_to_test,
                        startcol = nbr_cols_aleady_fill)
                    nbr_cols_aleady_fill += nbr_cols + 3
            if value and isinstance(value, list) and all(isinstance(item, dict) for item in value):
                # Si la valeur est une liste de dictionnaires, créez un DataFrame
                df = pd.DataFrame(value)
                df = get_new_dataframe_with_key_as_first_level_header(df, key)
                nbr_cols = get_number_row_in_dataframe(df)
                df.to_excel(
                    writer,
                    sheet_name=key_words_to_test,
                    startcol=nbr_cols_aleady_fill
                    )
                nbr_cols_aleady_fill += nbr_cols + 3

def get_dictionary_statistic_global_empty() -> dict:
    dict_stat = {
        "file names": [""],
        "number of title": [0],
        "number of paragraph": [0],
        "number of table": [0],
        "number of list": [0],
        "number of other": [0],
        "is section 6 present": [False],
        "is section 7 present": [False],
        "Effective date": None,
        "IDCC": None,
        }
    return dict_stat

def get_dataframe_global_statistic_empty() -> pd.DataFrame:
    dataframe_statistic = pd.DataFrame.from_dict(get_dictionary_statistic_global_empty())
    return dataframe_statistic

def update_dataframe_with_meta_data(
        meta_data: pd.DataFrame,
        df_to_update: pd.DataFrame
        ) -> pd.DataFrame:
    try:
        meta_data_stat = meta_data.count()
        df_to_update["IDCC"] = meta_data_stat["IDCC"]
        df_to_update["Effective date"] = meta_data_stat["Effective date"]
    except Exception :
        df_to_update["IDCC"] = 0
        df_to_update["Effective date"] = 0
    return df_to_update

def get_dataframe_global_statistic(
        meta_data: pd.DataFrame,
        list_sections: List[dict],
        name_file: str
        ) -> pd.DataFrame:
    dict_global_statistic = get_global_statistic_from_content(list_sections, name_file)
    dataframe_statistic = pd.DataFrame.from_dict(dict_global_statistic)
    df_global_stat = update_dataframe_with_meta_data(
        meta_data=meta_data, df_to_update=dataframe_statistic)
    return df_global_stat

def update_dictionary_global_statistic(
        dict_statistic_global: dict,
        key_category_data: str,
        list_data: List
    ) -> dict:
    for key_statistic in dict_statistic_global:
        if key_category_data in key_statistic:
            dict_statistic_global[key_statistic][0] += len(list_data)
    return dict_statistic_global

def update_check_present_of_text_in_title(
        dict_statistic_global: dict,
        title: str,
        word_to_test_section_6: str,
        word_to_test_section_7: str
    ) -> bool:
    if word_to_test_section_7 in title:
        dict_statistic_global["is section 7 present"] = True
    if word_to_test_section_6 in title:
        dict_statistic_global["is section 6 present"] = True
    return dict_statistic_global

def get_global_statistic_from_content(
        list_sections: List[dict],
        name_file: str
        ):
    dict_statistic_global = get_dictionary_statistic_global_empty()
    dict_statistic_global["file names"] = name_file
    for indice_section, section in enumerate(list_sections):
        etat_logging = [name_file, indice_section, "Statistic global"]
        dict_section =  extract_information_from_section(section, etat_logging)
        for key_category_data, list_data in dict_section.items():
            update_dictionary_global_statistic(
                dict_statistic_global,
                key_category_data,
                list_data
                )
            update_check_present_of_text_in_title(
                dict_statistic_global,
                title=dict_section["title"],
                word_to_test_section_6="Maladie, maternité, accident du travail",
                word_to_test_section_7=\
                    "Retraite complémentaire et régimes de prévoyance et de frais de santé"
                )
    return dict_statistic_global
        
def extract_meta_data(soup) -> pd.DataFrame:
    """
    Extract 2 informations:
        - Effective date
        - IDCC
    Download this informations inside a dictionnary
    """
    try:
        list_of_effective_date = []
        effective_date = None
        for str_effective_date in soup.find_all(class_='DATEMAJ'):
            list_of_effective_date.append(
                str_effective_date.text.split(':')[-1]
                )
        if list_of_effective_date:
            effective_date = list_of_effective_date[0]
        list_of_IDCC =[]
        for tb_IDCC in soup.find_all(class_='TYPE0-1COL'):
            list_of_IDCC.append(tb_IDCC)

        header = extract_header(tb_IDCC)
        cells = extract_cell(tb_IDCC, header)

        word_search =  "IDCC"
        value_IDCC = None
        for enu, word in enumerate(header):
            if word_search in word:
                value_IDCC = cells[0][enu]
        
        dict_meta_data = {
            "Effective date": [effective_date],
            "IDCC": [value_IDCC]
        }
        df_meta_data = pd.DataFrame.from_dict(dict_meta_data)
    except Exception:
        message_warning = "There is no Meta data for this CCN."
        logging.warning(message_warning)
        dict_meta_data = {
            "Effective date": [None],
            "IDCC": [None]
        }
        df_meta_data = pd.DataFrame.from_dict(dict_meta_data)
    return df_meta_data

def save_files_extracted(
        path_to_save_files: str,
        dict_notion: dict,
        df_meta_data: pd.DataFrame
        ) -> None :
    with pd.ExcelWriter(path_to_save_files, mode='w') as writer:
        for notion_searched, dict_value in dict_notion.items():
                save_dict_to_files_xlsx(
                        [dict_value["paragraph"], dict_value["table"], dict_value["title"]],
                        notion_searched,
                        writer)
        df_meta_data.to_excel(writer, sheet_name="Meta data")

def get_dataframe_statistic_clean(dataframe_statistic: pd.DataFrame):
    try:
        dataframe_statistic['word found'] = dataframe_statistic['word found'].apply(
        lambda x: None if not x else str(x).replace('(', '').replace(',)', '').replace(')', ''))
    except ValueError as e:
        message_warning = f"The statistic dataframe is not clean du to : {e}"
        logging.warning(message_warning)
    return dataframe_statistic

def save_statistics(
        path_source: str,
        dataframe_statistic: dict,
        dataframe_global_statistic: dict
        ) -> None:
    dataframe_statistic = get_dataframe_statistic_clean(dataframe_statistic)
    path_to_save_files = os.path.join(path_source, "statistic.xlsx")
    with pd.ExcelWriter(path_to_save_files, mode='w') as writer:
        dataframe_statistic.to_excel(
            writer,
            sheet_name="statistic",
            header=True,
            index=False
            )
        dataframe_global_statistic.to_excel(
            writer,
            sheet_name="global statistic",
            header=True,
            index=False
            )

def create_noeud(tag, attrs, title=""):
    noeud = {
        "tag": tag,
        "attrs": attrs,
        "title": title
    }
    return noeud

def check_tag_lower_tags_test(
        arborescence: List[any],
        tag: str,
        attrs: str
        ):
    class_name_PNUM = "PNUM" # Exception for this class because they can contains other title
    liste_indice_noeud = []
    for indice_noeud, noeud in enumerate(arborescence):
        bool_name_class = False
        if "class" in noeud:
            bool_name_class = any(re.search(re.escape(expression), str(class_name_PNUM), re.IGNORECASE) 
                      is not None for expression in attrs['class'])
        if tag < noeud["tag"] and not bool_name_class:
            liste_indice_noeud.append(indice_noeud)
    return liste_indice_noeud

def check_tag_lower_tags(
        arborescence: List[any],
        tag: str
        ):
    liste_indice_noeud = []
    for indice_noeud, noeud in enumerate(arborescence):
        if tag < noeud["tag"]:
            liste_indice_noeud.append(indice_noeud)
    return liste_indice_noeud

def check_tag_present(
        arborescence: List[any],
        tag: str
        ):
    liste_indice_noeud = []
    for indice_noeud, noeud in enumerate(arborescence):
        if tag == noeud["tag"]:
            liste_indice_noeud.append(indice_noeud)
    return liste_indice_noeud

def check_attrs_present(
        arborescence: List[any],
        liste_indice_noeud: List[int],
        attrs: str
        ):
    liste_indice_attrs_noeud = []
    for indice_noeud in liste_indice_noeud:
        noeud = arborescence[indice_noeud]
        if attrs == noeud["attrs"]:
            liste_indice_attrs_noeud.append(indice_noeud)
    return liste_indice_attrs_noeud

def dell_noeud_to_arborescence(
        arborescence: List[any],
        liste_indice_noeud_to_dell: List[int]
        ):
    if liste_indice_noeud_to_dell:
        indice_to_suppress = liste_indice_noeud_to_dell[0]
        new_arborescence = arborescence[:indice_to_suppress]
    else:
        new_arborescence = arborescence
    return new_arborescence

def add_noeud_to_arborescence(
        arborescence: List[any],
        tag: str,
        attrs: str,
        title=""
        ):
    noeud = create_noeud(tag, attrs, title)
    arborescence.append(noeud)
    return arborescence

def extract_arborescence_general_rules(
        list_arborescence: List[dict],
        tag: str,
        attrs: str,
        title: str
        ):
    liste_tag_noeud_lower_present = check_tag_lower_tags(list_arborescence, tag)
    if liste_tag_noeud_lower_present:
        # create a new object or del previous data
        list_arborescence = list_arborescence[:liste_tag_noeud_lower_present[0]]
        list_arborescence = add_noeud_to_arborescence(list_arborescence,
                                                      tag,
                                                      attrs,
                                                      title)

    list_tag_noeud_equal_present = check_tag_present(list_arborescence, tag)
    if list_tag_noeud_equal_present:
        # apply rules to generate in function of the attrs variable
        liste_attrs_noeud_present = check_attrs_present(list_arborescence,
                                                        list_tag_noeud_equal_present,
                                                        attrs)
        if liste_attrs_noeud_present:
            list_arborescence = list_arborescence[:liste_attrs_noeud_present[0]]
        list_arborescence = add_noeud_to_arborescence(list_arborescence,
                                                      tag,
                                                      attrs,
                                                      title)

    if not liste_tag_noeud_lower_present and not list_tag_noeud_equal_present:
        # Ajoute un noeud a l arbre
        list_arborescence = add_noeud_to_arborescence(list_arborescence,
                                                      tag,
                                                      attrs,
                                                      title)
    return list_arborescence

def get_previous_section_from_arborescence(
        list_arborescence: List[dict]
        ) -> dict:
    last_noeud = {}
    if list_arborescence:
        last_noeud = list_arborescence[-1]
    return last_noeud

def extract_arborescence(
        list_arborescence: List[dict],
        section: List[Any]
        ):
    """
    Extract the tag, attrs and the title from the section dictionary in order to register all the previous
    title. The rules for define the structur of summary use tag and attrs.
    An execption is made for title with a tag of h5 or h6 and an attribute of PNUM/d
    """
    tag = section["tag"]
    attrs = section["attrs"]
    title = section["title"]
    is_general_method_use = False
    last_noeud = get_previous_section_from_arborescence(list_arborescence)
    if last_noeud \
        and "class" in last_noeud["attrs"] \
        and "tag" in last_noeud and last_noeud["tag"] in ["h5", "h6"]:
        if any(re.search(re.escape(noeud["attrs"]["class"][0]), "PNUM", re.IGNORECASE) is not None
                for noeud in list_arborescence if "class" in noeud["attrs"]):
            # Ajoute selon la règle des attrs
            list_arborescence, liste_tag_noeud_lower_present = extract_arborescence_rules_attrs(
                list_arborescence, tag, attrs, title)
            if not liste_tag_noeud_lower_present and tag != last_noeud["tag"]:
                list_arborescence = add_noeud_to_arborescence(
                    list_arborescence,
                    tag, attrs, title)
        else:
            is_general_method_use = True
    else:
            is_general_method_use = True
    if is_general_method_use:
        list_arborescence = extract_arborescence_general_rules(
                list_arborescence,
                tag,
                attrs,
                title)
    return list_arborescence

def extract_arborescence_rules_tag(
        list_arborescence: List[dict],
        tag: str,
        attrs: dict,
        title: str
        ) -> List[dict] and List[int]:
    liste_tag_noeud_lower_present = check_tag_lower_tags(list_arborescence, tag)
    if liste_tag_noeud_lower_present:
        # create a new object or del previous data
        list_arborescence = list_arborescence[:liste_tag_noeud_lower_present[0]]
        list_arborescence = add_noeud_to_arborescence(list_arborescence,
                                                      tag,
                                                      attrs,
                                                      title)
    return list_arborescence, liste_tag_noeud_lower_present

def extract_arborescence_rules_attrs(
        list_arborescence: List[dict],
        tag: str,
        attrs: dict,
        title: str
        ) -> List[dict] and List[int]:
    list_tag_noeud_equal_present = check_tag_present(list_arborescence, tag)
    if list_tag_noeud_equal_present:
        # apply rules to generate in function of the attrs variable
        liste_attrs_noeud_present = check_attrs_present(list_arborescence,
                                                        list_tag_noeud_equal_present,
                                                        attrs)
        if liste_attrs_noeud_present:
            list_arborescence = list_arborescence[:liste_attrs_noeud_present[0]]
        list_arborescence = add_noeud_to_arborescence(list_arborescence,
                                                      tag,
                                                      attrs,
                                                      title)
    return list_arborescence, list_tag_noeud_equal_present

def extract_title_from_arborescence_to_string(
        list_arborescence: List[dict],
        separator_tilte: str = "|||"
        ) -> str:
    str_title = ""
    for dict_title in list_arborescence:
        str_title += dict_title["title"]
        str_title += separator_tilte
    return str_title



    




