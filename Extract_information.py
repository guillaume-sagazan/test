import os
from function_extraction import *

# Import les data a partir des pages HTLM
path_source = os.getcwd()
name_folder_files_htlm = 'export_html'
path_folder_htlm = os.path.join(path_source, name_folder_files_htlm)
list_name_files = extract_name_folder(path_folder_htlm)

# Import le dictionnaires   
name_folder_dictionary = 'dictionnaire de recherche/dictionnaire des notions.xlsx'
path_folder_dictionary = os.path.join(path_source, name_folder_dictionary)
dict_dictionary_tabs = import_dictionary_tabs(path_folder_dictionary)
dict_tested_word = get_dictionary_of_tested_words(dict_dictionary_tabs)

# Export 
export_folder_path = "export_extraction"

# Configure les log
set_up_logging(path_source)

# Initialise le dictionnaire des statistiques
dataframe_statistic = get_dataframe_statistic_empty()
dataframe_global_statistic = get_dataframe_global_statistic_empty()
separator_tilte = "|||" # parametre de separation des titles dans l'arborescence

for numero_file, name_HTLM_file in enumerate(list_name_files):
    try:
        # Download the input
        path_input_file = os.path.join(path_folder_htlm, name_HTLM_file)
        html_content = load_htlm(path_input_file)

        # Créer un objet Beautiful Soup
        soup = create_parser(html_content)
        list_sections = group_by_section(soup)

        # Export files 
        name_file = extract_suffix_files(name_HTLM_file)
        path_export_folder = get_export_folder_path(path_source, export_folder_path)
        path_to_save_files = os.path.join(path_export_folder, name_file + ".xlsx")

        # intermediaire
        dict_notion = {}
        print(f"Début de la recherche dans {name_file}.\
            Numéro du fichier {numero_file+1} / {len(list_name_files)}")
        
        # Extract meta data from file
        df_meta_data = extract_meta_data(soup)

        for key_words_to_test, dict_words_to_test in dict_tested_word.items():
            list_arborescence = []
            # initialise dict containing data of text extract
            dict_paragraph = {}
            dict_table = {}
            dict_title = {}
            
            dict_hash_incorporate_paragraph = {}
            dict_hash_incorporate_table = {}
            dict_hash_incorporate_title = {}
            indice_section = 0
            section =  list_sections[0]
            for indice_section, section in enumerate(list_sections):
                etat_logging = [name_file, indice_section, key_words_to_test]
                # print(etat_logging)
                dict_section =  extract_information_from_section(section, etat_logging)
                list_arborescence = extract_arborescence(
                    list_arborescence,
                    section
                    )
                str_title_arborescence = extract_title_from_arborescence_to_string(
                    list_arborescence,
                    separator_tilte=separator_tilte
                    )                
                dict_paragraph, dict_hash_incorporate_paragraph = \
                        get_text_from_paragraph_containing_words(
                            dict_words_to_test,
                            dict_section,
                            dict_paragraph,
                            dict_hash_incorporate_paragraph,
                            str_title_arborescence,
                            etat_logging
                            )
                dict_table, dict_hash_incorporate_table = \
                    get_text_from_table_containing_words(
                        dict_words_to_test,
                        dict_section,
                        dict_table,
                        dict_hash_incorporate_table,
                        str_title_arborescence,
                        etat_logging
                    )
                    
                dict_title, dict_hash_incorporate_title = \
                    get_text_from_title_containing_words(
                        dict_words_to_test,
                        dict_section,
                        dict_title,
                        dict_hash_incorporate_title,
                        str_title_arborescence,
                        etat_logging
                    )
                
            dict_notion = add_elm_to_dict_notion(
                dict_paragraph,
                dict_table,
                dict_title,
                key_words_to_test,
                dict_notion
                )
        
        # update the statistic report 
        dataframe_statistic_for_a_file = get_dataframe_statistic(
            dict_notion,
            name_file
            )
        dataframe_statistic = dataframe_statistic._append(dataframe_statistic_for_a_file)
        dataframe_global_statistic_for_a_file = get_dataframe_global_statistic(
            df_meta_data,
            list_sections,
            name_file
            )
        dataframe_global_statistic = dataframe_global_statistic._append(
            dataframe_global_statistic_for_a_file
            )

        # save the file of data extracted
        save_files_extracted(path_to_save_files, dict_notion, df_meta_data)

    except ValueError:
        print("warning an issue occurred")
        logging.warning(name_file)

save_statistics(
    path_source,
    dataframe_statistic,
    dataframe_global_statistic.iloc[1:]
    )
