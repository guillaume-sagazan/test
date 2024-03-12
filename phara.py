import os
import pandas as pd
from function_extraction import extract_name_folder, set_up_logging, \
    get_export_folder_path, extract_suffix_files
from function_create_base_phara import *

# Import les data a partir des pages HTLM
path_source = os.getcwd()
name_folder_files_xlsx_extracted = "export_extraction"
path_folder_extracted = os.path.join(path_source, name_folder_files_xlsx_extracted)
list_name_files_xlsx_extracted = extract_name_folder(path=path_folder_extracted)

# Path transcodifiation
transco_folder_path = "dictionnaire de recherche/transcodification.xlsx"
path_folder_transco = get_export_folder_path(
    path_source, transco_folder_path)
data_transco_CSP = pd.read_excel(path_folder_transco, sheet_name="CSP")
data_transco_IDCC = pd.read_excel(
        path_folder_transco, sheet_name="IDCC", index_col=0
        ).to_dict(index=1)

# Path Export 
export_folder_path = "export phara"
name_output = "table_CCN_export.xlsx"
path_export_folder = get_export_folder_path(path_source, export_folder_path)
path_export_folder = get_export_folder_path(path_export_folder, name_output)

nbr_jour_total = 1095
# Configure les log
set_up_logging(path_source)

# creation template
list_template_maintien_salaire = []
list_name_files_with_data_but_not_for_prevoyance = []
list_name_files_empty = []

# numero_file = 43
# name_xslx_file = 'Charcuterie de détail.xlsx'
name_xslx_file = 'Création et événement  entreprises techniques.xlsx'


list_name_with_data_prevoyance = []
list_name_with_data_other_prevoyance = []
for numero_file, name_xslx_file in enumerate(list_name_files_xlsx_extracted):
    #try:
        # Download the input
        path_input_file = os.path.join(path_folder_extracted, name_xslx_file)
        name_file = extract_suffix_files(name_xslx_file)
        print(f"Début de la recherche dans {name_file}.\
                Numéro du fichier : {numero_file+1} /" + \
                f" {len(list_name_files_xlsx_extracted)}")
        
        # Import files
        data_maintien_de_salaire = import_file_maintien_de_salaire(
            path_input = path_input_file
            )
        if not data_maintien_de_salaire.empty:
            try:
                df_maintien_de_salaire, is_prevoyance = \
                    generate_maintien_du_salaire_dataframe_formated(
                    data_maintien_de_salaire_from_input = data_maintien_de_salaire
                    )
                if not df_maintien_de_salaire.empty and is_prevoyance:
                    list_name_with_data_prevoyance.append((name_file, numero_file))
                if not is_prevoyance:
                    list_name_with_data_other_prevoyance.append(
                        (name_file, df_meta_data)
                        )
                df_maintien_de_salaire_with_meta_data = \
                    update_dataframe_with_meta_data(
                        data_to_update = df_maintien_de_salaire,
                        data_transco_IDCC = data_transco_IDCC,
                        path_input_file = path_input_file,
                        name_file = name_file
                        )
                list_template_maintien_salaire.append(
                    df_maintien_de_salaire_with_meta_data
                )
                
            except Exception :
                df_meta_data = \
                    update_dataframe_with_meta_data(
                        data_to_update = pd.DataFrame(),
                        data_transco_IDCC = data_transco_IDCC,
                        path_input_file = path_input_file,
                        name_file = name_file
                        )
                list_name_files_with_data_but_not_for_prevoyance.append(
                    (name_file, df_meta_data)
                    )
        else:
            df_meta_data = \
                update_dataframe_with_meta_data(
                    data_to_update = pd.DataFrame(),
                    data_transco_IDCC = data_transco_IDCC,
                    path_input_file = path_input_file,
                    name_file = name_file
                    )
            list_name_files_empty.append(
                (name_file, df_meta_data)
            )
    #except Exception:
    #    print(f"{Exception}")

if len(list_template_maintien_salaire) != 0 and \
    all(
         [isinstance(template, pd.DataFrame) 
            for template in list_template_maintien_salaire]):
    df_aggreg_all_file = pd.concat(list_template_maintien_salaire)
    df_template_empty_by_idcc = fill_empty_df_with_basic_data(
        list_of_df_empty = list_name_files_empty +\
            list_name_files_with_data_but_not_for_prevoyance
        )
    df_to_export = pd.concat([df_aggreg_all_file, df_template_empty_by_idcc])
else:
    message_error = "No data has been detected during the process."
    logging.error(message_error)
    raise ValueError(message_error)

df_to_export = df_to_export.drop_duplicates(['categorieObjectiveId', 'anciennete', 'ccnId'])
df_to_export.to_excel(path_export_folder)
