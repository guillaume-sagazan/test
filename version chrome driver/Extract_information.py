import re
import sys
import os
import numpy as np
import pandas as pd
from function_extraction import *
from bs4 import BeautifulSoup

# Import les data a partir des pages HTLM
path_source = os.getcwd()
name_folder_files_htlm = 'pages HTLM'
path_folder_htlm = os.path.join(path_source, name_folder_files_htlm)
list_name_files = extract_name_folder(path_folder_htlm)

name_HTLM_page = list_name_files[1]
name_file = os.path.join(path_folder_htlm, name_HTLM_page)
html_content = load_htlm(name_file)

# Import le dictionnaires   
name_folder_dictionary = 'dictionnaire de recherche/dictionnaire des notions.xlsx'
path_folder_dictionary = os.path.join(path_source, name_folder_dictionary)
dict_dictionary_tabs = import_dictionary_tabs(path_folder_dictionary)
dict_tested_word = get_dictionary_of_tested_words(dict_dictionary_tabs)


# Configure les log
set_up_logging(path_source)

# Deffinision de la regex
regex_teste = "Maintien du salaire"
# A faire céer un fichier qui contient les dictionnaires de mots
dict_of_notion = {'NAF': 'naf', "Maintien de salaire": "Maintien du salaire" }

# Initialisation des objects qui contiendrons l'information
list_dict_sections = []
dict_category_of_notion = {}

# Créer un objet Beautiful Soup
soup = create_parser(html_content)
list_sections = group_by_section(soup)
save_soup_object(soup)

regex_teste = "Maintien du salaire" # "Délai de prévenance"
expression = "Délai de prévenance"

list_dict_sections = []
list_hash_incorporate = []
list_title = []
dict_from_regex_to_text_table = {}
dict_from_regex_to_text_paragraph = {}
dict_from_regex_to_text_title = {}
for indice_section, section in enumerate(list_sections):
    dict_section =  extract_information_from_section(section)

    # title
    title_tested = [dict_section['title']]
    is_title_previous_use, list_title = check_previous_title(list_title, dict_section['title'])
    is_word_tested_in_text_title = search_regex_in_list(title_tested, regex_teste)

    # paragraphe
    paragraphs_tested = dict_section['paragraph']
    is_word_tested_in_text_paragraph = search_regex_in_list(paragraphs_tested, regex_teste)
    is_word_not_consume, list_hash_incorporate = search_word_not_consume(
                                                        list_hash_incorporate,
                                                        paragraphs_tested,
                                                        )
    is_data_paragraph_valid = is_title_previous_use & is_word_tested_in_text_paragraph \
                    & is_word_not_consume
    dict_from_regex_to_text_paragraph = fill_dict_with_text_contains_regex_for_paragraph(
                                            paragraphs_tested,
                                            regex_teste,
                                            dict_from_regex_to_text_paragraph,
                                            is_data_paragraph_valid
                                            )
    
    # table
    indice_of_table, is_indice_exist = extract_indice_that_contains_regex_in_table(dict_section,
                                                                                   regex_teste)
    if is_indice_exist:
        table_tested = dict_section['table'][indice_of_table]
        header_list = extract_header(table_tested)
        structured_data = extract_all_balise_tr(table_tested)
        is_word_not_consume, list_hash_incorporate = search_word_not_consume(
                                                         list_hash_incorporate,
                                                         header_list
                                                         )
        is_data_table_valid = is_word_not_consume & is_title_previous_use
        dict_from_regex_to_text_table = fill_dict_with_dataframe_contains_regex_for_table(
                                                header_list,
                                                structured_data,
                                                regex_teste,
                                                dict_from_regex_to_text_table,
                                                is_data_table_valid)
    
    # add elment if there present in the title and not in the paragraph and table
    if is_word_tested_in_text_title and not(is_indice_exist or is_word_tested_in_text_paragraph):
        dict_from_regex_to_text_title = fill_dict_with_dataframe_contains_regex_for_title(
                                            dict_from_regex_to_text_title,
                                            dict_section,
                                            regex_teste)
    
    dict_category_of_notion = update_dict(
        [dict_from_regex_to_text_paragraph, dict_from_regex_to_text_table,
         dict_from_regex_to_text_title],
         expression,
         dict_category_of_notion)

dict_from_regex_to_text_paragraph = 
dell_doublon_on_list_of_dict(dict_from_regex_to_text_paragraph, regex_teste)
dell_doublon_on_list_of_dict(dict_from_regex_to_text_table, regex_teste) # suppress doublon

len(dict_from_regex_to_text_table[regex_teste])
la = dict_from_regex_to_text_table

la[regex_teste][1]

dict_section['paragraph']
    