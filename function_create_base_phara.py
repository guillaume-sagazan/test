import os
import pandas as pd
import numpy as np
from datetime import date, datetime
import logging
import locale
import re

nbr_jour_total = 1095

def template_funct_csp(nbr_period: int = 5):
    """Create template funct CSP"""
    list_period = ["tauxPeriode", "periode"]
    list_all_period = [
        nameperiod + str(num)
        for num in range(1, nbr_period + 1)
            for nameperiod in list_period
        ]
    list_col_template = ["categorieObjectiveId", "anciennete"] +\
        list_all_period
    df_template_csp = pd.DataFrame(columns=list_col_template)
    return df_template_csp

def convert_date_str_to_date_numeric(
        date_str: str
        ) -> str:
    locale.setlocale(locale.LC_TIME, 'fr_FR')
    list_date_split = date_str.split(" ")
    num_day = int(list_date_split[0])
    numero_mois = datetime.strptime(list_date_split[1], '%B').month
    num_year = int(list_date_split[2])
    date_resultat = datetime(num_year, numero_mois, num_day)
    return date_resultat

def add_meta_data_to_template_csp(
        df_template: pd.DataFrame,
        date_effectif: str,
        iccd: int
        ) -> pd.DataFrame:
    df_template_copy = df_template.copy()
    df_template_copy["dateArretDesTexte"] = convert_date_str_to_date_numeric(
        date_str = date_effectif)
    df_template_copy["ccnld"] = iccd
    return df_template_copy

def add_date_creation_to_template(
        df_template: pd.DataFrame
        ) -> pd.DataFrame:
    df_template_copy = df_template.copy()
    df_template_copy["creation"] = date.today()
    return df_template_copy

def extract_IDCC_from_text(texte: str) -> str:
    texte = texte.replace( "\\xa0", " ")
    resultat = re.search(r'(IDCC \d+)', texte)
    code_IDCC = resultat.group().split(" ")[-1]
    return code_IDCC

def import_file_data(
        path_file: str,
        sheet_name: str,
        header: list | int = [0, 1]
        ) -> pd.DataFrame:
    df_import_files = pd.read_excel(
        path_file,
        sheet_name=sheet_name,
        header=header,
        skiprows=0,
        index_col=0)
    df_import_files.dropna(axis=0, how="all", inplace=True)
    df_import_files.dropna(axis=1, how="all", inplace=True)
    return df_import_files

def import_file_meta_data(
        path_input: str
        ) -> pd.DataFrame:
    try:
        df_meta_data = import_file_data(
            path_file = path_input,
            sheet_name = 'Meta data',
            header = 0
            )
    except Exception:
        df_meta_data = pd.DataFrame()
    return df_meta_data

def import_file_idcc(
        path_input: str
        ) -> pd.DataFrame:
    try:
        df_idcc = import_file_data(
            path_file = path_input,
            sheet_name = "IDCC",
            header = [0, 1]
            )
    except Exception:
        df_idcc = pd.DataFrame()
    return df_idcc

def import_file_maintien_de_salaire(
        path_input: str
        ) -> pd.DataFrame:
    try:
        df_maintien_de_salaire = import_file_data(
            path_file = path_input,
            sheet_name = 'Maintien de salaire'
            )
    except Exception:
        df_maintien_de_salaire = pd.DataFrame()
    return df_maintien_de_salaire

def reshearch_list_IDCC(df_data: pd.DataFrame):
    list_IDCC = []
    for texte in df_data[('IDCC', 'title')]:
        list_IDCC.append(extract_IDCC_from_text(texte))
    return list_IDCC

def check_validity_all_code_IDCC(
        code_IDCC: str,
        list_code_IDCC: list,
        name_file: str
        ) -> list:
    list_code_IDCC_to_complet = [code_IDCC]
    for code_idcc in list_code_IDCC:
        if not (code_idcc is None or code_idcc == ""):
            list_code_IDCC_to_complet.append(code_idcc)
    list_code_IDCC_completed = list(np.unique(list_code_IDCC_to_complet))
    if len(list_code_IDCC_completed) == 0:
        logging.warning(f"No value IDCC for {name_file}")
    return list_code_IDCC_completed

def get_list_all_IDCC(
        path_input_file: str,
        code_IDCC: str | int,
        name_file: str
        ) -> list:
    try:
        df_IDCC = import_file_idcc(
            path_input = path_input_file
            )
        list_IDCC = reshearch_list_IDCC(df_IDCC)
        list_IDCC_check = check_validity_all_code_IDCC(
            code_IDCC = str(code_IDCC),
            list_code_IDCC = list_IDCC,
            name_file = name_file
        )
    except Exception:
        list_IDCC_check = [code_IDCC]
    return list_IDCC_check

def extract_meta_date(
        path_input_file: str
        ) -> tuple:
    try:
        df_meta_data = import_file_meta_data(
            path_input = path_input_file
            )
        date_effectif = df_meta_data.loc[0, "Effective date"].strip()
        effective_date = convert_date_str_to_date_numeric(
            date_str = date_effectif)
        code_idcc = df_meta_data.loc[0, "IDCC"]
    except Exception:
        effective_date = None
        code_idcc = None
    return (effective_date, code_idcc)

def get_meta_data(
        path_file: str,
        name_file: str
        ) -> pd.DataFrame:
    """
    Return a dataframe that containt the information :
        effective data as string,
        IDCC as List    
    """
    effective_date, code_idcc = extract_meta_date(path_file)
    
    list_all_idcc = get_list_all_IDCC(
        path_input_file=path_file,
        code_IDCC=code_idcc,
        name_file=name_file
        )
    
    dict_data_meta = {
        "dataEff": effective_date,
        "ccnId": list_all_idcc
        }
    df_data_meta = pd.DataFrame(dict_data_meta)
    return df_data_meta

def mapping_csp_word() -> dict:
    mapping = {
        'cadre dir': 1,
        'cadre supérieur': 1,
        'cadre': [1, 2],
        'non cadre': [3, 4, 5],
        'non-cadre': [3, 4, 5],
        'etam': [3, 4],
        'agents de maîtrise': 3,
        'maîtrise': 3,
        'employé': 4,
        'employés techniques': 4,
        'ouvrier': 5,
        "tous": [1, 2, 3, 4, 5]
        }
    return mapping

def get_list_word_csp_to_find() -> list:
    list_of_word_associate_with_csp = \
        ['cadre dir', 'cadre', 'cadre supérieur',
         'non cadre', 'non-cadre', 'etam',
        'agents de maîtrise', 'maîtrise', 'employé',
        'employés techniques', 'ouvriers', 'ouvrier'
        ]
    return list_of_word_associate_with_csp

def associated_list_of_word_to_id_csp(
        list_of_column_that_contains_csp: list,
        dict_mapping_category_csp: dict
        ) -> tuple[list, list]:
    """
    Associate the list of words with the associated ID
    """
    list_of_unique_value = list(
        np.unique(list_of_column_that_contains_csp))
    list_value_associated = []
    for word_test in list_of_unique_value:
        if word_test in dict_mapping_category_csp:
            list_value_associated.append(
                dict_mapping_category_csp[word_test])
        else:
            list_value_associated.append(
                dict_mapping_category_csp[word_test])
    return list_value_associated, list_of_unique_value

def select_the_good_id_csp_from_list_choice(
        list_value_associated: list,
        list_word_associated: list,
        dict_mapping_category_csp: dict,
        ) -> list:
    """
    extract all category valable for the dataframe in input
    """
    value_of_ref = []
    list_tmp = []
    for enu, elm in enumerate(list_word_associated):
        if len(elm.split("-")) > 1:
            list_tmp.append(list_value_associated[enu])
    if len(list_tmp) != 0:
        list_value_associated = list_tmp

    for value_proposed in list_value_associated:
        if isinstance(value_proposed, int):
            value_of_ref = [value_proposed]
        elif isinstance(value_proposed, list):
            if len(value_of_ref) >= len(value_proposed) or \
                len(value_of_ref) == 0:
                value_of_ref = value_proposed
    if len(value_of_ref) == 0:
        value_of_ref = dict_mapping_category_csp['tous']
    return value_of_ref

def extract_csp_from_header(
        list_columns_data: list
        ) -> list:
    """
        If one category if found then it will be apply for the all dataframe
    """
    list_of_word_associate_with_csp = get_list_word_csp_to_find()
    dict_mapping_category_csp = mapping_csp_word()
    list_of_column_that_contains_csp = []
    for list_col in list_columns_data:
        for word_csp_teste in list_of_word_associate_with_csp:
            if any([
                re.search(word_csp_teste, list_col[index_level].lower())
                        for index_level in range(len(list_col))
                ]):
                list_of_column_that_contains_csp.append(word_csp_teste)
    # Associate the list of words with the associated ID
    list_value_associated, list_word_associated =\
        associated_list_of_word_to_id_csp(
            list_of_column_that_contains_csp,
            dict_mapping_category_csp
            )
    # extract all category valable for the dataframe in input
    value_of_ref = select_the_good_id_csp_from_list_choice(
        list_value_associated,
        list_word_associated,
        dict_mapping_category_csp,
        )
    return value_of_ref

def association_data_inside_table_for_csp(
        word_teste: str,
        dict_word: dict
        ) -> str:
    list_word_correct = []
    for word in dict_word:
        if re.search(word, word_teste):
            list_word_correct.append(word)
    if len(list_word_correct) == 0:
        value = None
    else:
        value = dict_word[list_word_correct[-1]]
    return value

def extract_csp_from_table(data: pd.DataFrame) -> pd.DataFrame:
    """
    Renvoi le dataframe avec une nouvelle colonne Id_csp si au moin un colonne contient 
    de l'information à propos des CSP et renvooi un boolean indiquant la présence d'une telle 
    colonne
    """
    dict_mapping = mapping_csp_word()
    for col in data.columns:
        test_col_csp = data[col].apply(
            lambda cat: association_data_inside_table_for_csp(
                word_teste = cat.lower(),
                dict_word = dict_mapping
                )
            )
        if any([None != elm for elm in test_col_csp]):
            data["Id_csp"] = test_col_csp
    return data

def extract_and_add_csp(
        df_maintien_de_salaire: pd.DataFrame
        ) -> pd.DataFrame:
    """
    Clean the dataframe to extract columns and data then adapt is format.
    In function of hearder then of data check the presence of CSP information.
    If nothing found in data then look for the columns.
    Create a columns to the existing dataframe name : Id_csp
    """
    try:
        df_extract_prevoyance_clean = select_extract_data_for_prevoyance(
            data_extracted = df_maintien_de_salaire
            )
        list_col_clean_csp = extract_csp_from_header(
                list_columns_data = df_maintien_de_salaire
                )
        if not df_extract_prevoyance_clean.empty:
            df_transform_clean = transforme_data_extracted(
                df_extract_prevoyance_clean)

            df_with_category_csp = extract_csp_from_table(
                data = df_transform_clean)

            if not "Id_csp" in df_with_category_csp:
                df_with_category_csp["Id_csp"] = df_with_category_csp.apply(
                    lambda row: list_col_clean_csp, axis=1)
            else:
                df_with_category_csp["Id_csp"] = \
                    df_with_category_csp["Id_csp"].apply(
                        lambda id_csp: id_csp 
                        if not (id_csp is None) or not (id_csp is np.nan) 
                            else list_col_clean_csp
                    )
        else:
            message_error = "An error occured in the extraction of data." +\
                 "No Data for prevoyance has been detected"
            logging.error(message_error)
            raise ValueError(message_error)
    except Exception:
        message_error = "An error occured in the extraction of data"
        logging.error(message_error)
        raise ValueError(message_error) 
    return df_with_category_csp

def select_extract_data_for_prevoyance(
        data_extracted: pd.DataFrame
        ) -> pd.DataFrame:
    """
    data_extracted : Dataframe that contain all sub dataframe 
    that come from the extraction. Extract only the specified part
    """
    list_data_collect = []
    list_col_second_index = []
    col_extract = data_extracted.columns
    #Look inside columns
    for list_col in col_extract:
        if any([
            re.search("prévoyance", list_col[index_level])
                for index_level in range(len(list_col))
            ]):
            list_data_collect.append(data_extracted[list_col])
            list_col_second_index.append(data_extracted[list_col].iloc[0])
    if list_data_collect != []:
        df_extract_prevoyance = pd.concat(list_data_collect, axis=1)
        df_extract_prevoyance.columns = df_extract_prevoyance.iloc[0]
        df_extract_prevoyance = df_extract_prevoyance.reset_index()
        df_extract_prevoyance_clean = df_extract_prevoyance.dropna(
            subset=['index']).drop(columns="index")
    else:
        # look inside the first row
        for list_col in col_extract:
            list_data_collect.append(data_extracted[list_col])
        df_extract_prevoyance = pd.concat(list_data_collect, axis=1)
        df_extract_prevoyance.columns = df_extract_prevoyance.iloc[0]
        df_extract_prevoyance = df_extract_prevoyance.reset_index()
        df_extract_prevoyance_clean = df_extract_prevoyance.dropna(
            subset=['index']).drop(columns="index")
        list_col = df_extract_prevoyance_clean.columns
        if not any([
            re.search("prévoyance", list_col[index_level])
                for index_level in range(len(list_col))
            ]):
            df_extract_prevoyance_clean = pd.DataFrame()
    return df_extract_prevoyance_clean

def normalized_text(df_data: pd.DataFrame) -> pd.DataFrame:
    df_data_normalized = df_data.replace( "\\xa0", " ")
    df_data_normalized.columns = [
        name_col.replace( "\\xa0", " ") 
            for name_col in df_data_normalized.columns
            ]
    return df_data_normalized

def transforme_data_extracted(
        data_clean: pd.DataFrame
        ) -> pd.DataFrame:
    list_nbr_nan = data_clean.isna().sum(axis=1).values
    list_data = []
    for enu, each_index in enumerate(data_clean.index):
        shift_nan = list_nbr_nan[enu]
        list_data.append(
            data_clean.loc[each_index, :].shift(shift_nan)
        )
    df_formated_with_blank_value = pd.concat(list_data, axis=1).T
    name_first_col = df_formated_with_blank_value.columns[0]
    df_formated_with_blank_value[name_first_col] = \
        df_formated_with_blank_value[name_first_col].fillna(method='ffill')
    df_transform = df_formated_with_blank_value.dropna(axis=0, how='any')
    df_normalized = normalized_text(df_data = df_transform)
    return df_normalized

def get_colonne_that_contains_word(
        list_col: list[str],
        word: str
        ) -> str:
    """
        Find one column from list_col that contains the word.
        If No word hase been found return None.
        list_col can not be empty. 
    """
    list_word_is_contains = [
        re.search(word, str(columns)) != None for columns in list_col
    ]
    if len(list_word_is_contains) == 0:
        message_error = "The length of columns is null"
        raise ValueError(message_error)
    col_find = None
    if any(list_word_is_contains):
        arg_word_find = np.argmax(list_word_is_contains)
        col_find = list_col[arg_word_find]
    elif any(["duree" in col for col in list_col]):
        col_find = "duree"
    else:
        message_warning = "No data that describe the anciennete fund."
        logging.warning(message_warning)
    return col_find

def check_list_born_valid_anciennete(list_borne: list) -> list:
    try:
        new_list_borne_int = [int(borne) for borne in list_borne]
    except TypeError:
        raise TypeError("wrong element from list_borne detected")
    return new_list_borne_int

def extract_borne_inf_from_anciennete(
        list_borne: list[str],
        texte: str,
        is_borne_not_incluse: bool
        ) -> float | None:
    """
    is_borne_not_incluse: bool if True that means that the borne is not incluse
    if False is incluse
    """
    list_borne_int = check_list_born_valid_anciennete(list_borne)
    regex_month = r'mois'
    is_month_in_texte = re.search(regex_month, texte)
    fract_year = 1
    if is_month_in_texte:
        fract_year = 1/12
    borne_inf = None
    if len(list_borne_int) != 0:
        borne_inf = (np.min(list_borne_int) + is_borne_not_incluse) * fract_year
    return borne_inf

def verifier_dictionnaire_borne_anciennete(dictionnaire: dict) -> int:
    # Filtrer les valeurs différentes de None
    list_defaut_value = [valeur
        for key, valeur in dictionnaire.items() 
            if "phrase" in key and valeur is not None
            ]
    list_not_defaut_value = [valeur
        for key, valeur in dictionnaire.items() 
            if not("phrase" in key) and valeur is not None
            ]

    valeurs_differentes_default_value = set(list_defaut_value)
    valeurs_differentes_not_default_value = set(list_not_defaut_value)

    if len(valeurs_differentes_not_default_value) >= 1:
        value = valeurs_differentes_not_default_value.pop() \
            if valeurs_differentes_not_default_value else None
    elif len(valeurs_differentes_default_value) >= 1:
        value = valeurs_differentes_default_value.pop() \
            if valeurs_differentes_default_value else None
    else:
        logging.warning("No value has been found or all are equal to None")
        value = None
    return value

def search_borne_min_from_anciennete(
        list_name_regex: list,
        list_regex: list,
        list_borne_not_incluse: list,
        texte: str
        ) -> float:
    dict_result = {
        key: extract_borne_inf_from_anciennete(
            list_borne=re.findall(regex, texte),
            texte=texte,
            is_borne_not_incluse=is_borne_not_incluse)
            for key, regex, is_borne_not_incluse 
                in zip(list_name_regex, list_regex, list_borne_not_incluse)
            }
    borne_inf = verifier_dictionnaire_borne_anciennete(dict_result)
    return borne_inf

def extract_born_min_from_col_annciennete(
        data_anciennete: pd.DataFrame,
        col_anciennete: str
        ) -> pd.DataFrame:
    regex_s1  = r'(\d+)'
    regex_sup1 = r'>.?(\d+)'
    regex_supegal1 = r'≥.?(\d+)'
    regex_inf1 = r'<.?(\d+)'
    regex_infgal1 = r'≤.?(\d+)'

    list_regex = [
        regex_s1, regex_sup1,
        regex_supegal1, regex_inf1,
        regex_infgal1
        ]
    
    list_name_regex = [
        "phrase_1", "sup_1", "sup_egal_1","inf_1", "inf_egal_1"
        ]

    list_borne_not_incluse = [
        False, False, False, False, False  
        ]
    data_anciennete["born_min"] = data_anciennete[col_anciennete].apply(
        lambda texte: search_borne_min_from_anciennete(
            list_name_regex, list_regex, list_borne_not_incluse, texte)
            )
    return data_anciennete

def extract_born_min_from_col_duree_and_period(
        data_to_add_duree_period: pd.DataFrame,
        ) -> pd.DataFrame:
    """
    En plus des de l'extraction des bornes extraits les periodes
    Faire fonctionner la fonctionner qui permet de catch les pérides et les bornes
    Regex à revour pour jour 1.
    """
    data_duree = data_to_add_duree_period.copy()
    regex_jour_1 = r'(\d+\s*\d*)e\s*jour'
    regex_jour_2 = r'(\d+\s*\d*)$'
    regex_ans = r'(\d+)\s*an'
    value_category_default = None
    max_period = int(
        [col for col in data_duree.columns
        if re.search(r'period_\d', col)][-1][-1]
            )
    list_row_cat = []
    for enu, word_duree in enumerate(data_duree["duree"]): 
        word_duree = word_duree.replace('\xa0', '')
        value_category_default_new = data_duree.loc[enu, [
            col for col in data_duree.columns
                if re.search('catégorie', col.lower())
                ][-1]]
    
        if value_category_default_new != value_category_default:
            if enu > 1:
                list_row_cat.append(row_data_for_cat)
            max_period_enu = max_period
            value_category_default = value_category_default_new
            row_data_for_cat = data_duree.loc[
                data_duree.index == enu, :].copy()
            
        # word_duree = "jusqu'au 240e jour, jusqu'au 365e jour après 10 ans d'ancienneté"
        # enu = 1
        dict_extracted_data = {
            "jour": 0,
            "ans": 0
            }
        
        list_word = word_duree.split(",") 
        for nbr_elm_in_word, elm_word in enumerate(list_word):
            if re.search(regex_jour_1, elm_word):
                dict_extracted_data["jour"] = \
                    int(re.search(regex_jour_1, elm_word).group(1))
                    
            if re.search(regex_jour_2, elm_word):
                dict_extracted_data["jour"] = \
                    int(re.search(regex_jour_2, elm_word).group(1))
                             
            if re.search(regex_ans, elm_word):
                dict_extracted_data["ans"] = \
                    int(re.search(regex_ans, elm_word).group(1))
            if nbr_elm_in_word == 0:
                if dict_extracted_data["jour"] != 1095:
                    row_data_for_cat.loc[:, "born_min"] = \
                        dict_extracted_data["ans"]
                    row_data_for_cat.loc[:, f"taux_{max_period_enu}"] = \
                        data_duree.loc[enu, f"taux_{max_period}"]
                    row_data_for_cat.loc[:, f"period_{max_period_enu}"] = \
                        dict_extracted_data["jour"]
                    max_period_enu += 1
                else:
                    row_data_for_cat.loc[:, f"taux_{max_period_enu}"] = \
                        data_duree.loc[enu, f"taux_{max_period}"]
                    row_data_for_cat.loc[:, f"period_{max_period_enu}"] = \
                        row_data_for_cat.loc[:, f"period_{max_period_enu-1}"] + 1
                    if f"period_{max_period_enu-2}" in row_data_for_cat:
                        row_data_for_cat.loc[:, f"period_{max_period_enu-1}"] = \
                            row_data_for_cat.loc[:, f"period_{max_period_enu-2}"] + 1
                    max_period_enu += 1
            else:
                max_index = row_data_for_cat.index.max()
                row_data_for_cat.loc[max_index + 1, :] =\
                    row_data_for_cat.loc[max_index,:].copy()
                row_data_for_cat.loc[max_index + 1, "born_min"] = \
                    dict_extracted_data["ans"] + 0
                row_data_for_cat.loc[max_index + 1, f"taux_{max_period_enu-1}"] = \
                    data_duree.loc[enu, f"taux_{max_period}"]
                row_data_for_cat.loc[max_index + 1, f"period_{max_period_enu-1}"] = \
                    dict_extracted_data["jour"] + 0

    list_row_cat.append(row_data_for_cat)
    
    return pd.concat(list_row_cat)

def add_born_min_to_df(
        data: pd.DataFrame
        ) -> dict:
    """
        df_data: Dataframe that containt the data Ancienneté or durée
        Create 2 columns min, 
        by default the min borne is 0 and max borne inf
    """
    data_with_born_min = data.copy()
    col_anciennete = get_colonne_that_contains_word(
       list_col = data.columns, word = "Ancienneté")
    if "duree" in col_anciennete:
        data_with_born_min = extract_born_min_from_col_duree_and_period(
            data_to_add_duree_period = data_with_born_min
            )
    elif col_anciennete != "duree":
        data_with_born_min = \
            extract_born_min_from_col_annciennete(
                data_anciennete = data_with_born_min,
                col_anciennete = col_anciennete
                )
    else:
        data_with_born_min["born_min"] = 0
    return data_with_born_min

# def extract_tx_period_from_header_table
def extract_tx_period_from_header_table(data: pd.DataFrame) -> pd.DataFrame:
    indicator_period = 0
    data_copy = data.copy()
    for name_col in data.columns:
        regex_tx = r'(\d+,\d+|\d+)\s*\%'
        word_check = re.search(regex_tx, name_col) 
        if word_check:
            indicator_period += 1
            value_rate = float(word_check.group(1).replace(",", ".")) / 100
            data_copy[f"taux_{indicator_period}"] = value_rate
            data_copy[f"period_{indicator_period}"] = \
                data_copy[name_col].apply(
                    lambda period: int(re.search(r'(\d+)', period).group(1))
                    if re.search(r'(\d+)', period)
                    else 1095)
    return data_copy, indicator_period


# def extract_tx_period_from_data_table
def get_tx_period_from_data_for_csp(
        word_test: str) -> str:
    try:
        list_data_period = []
        is_already_pass = False
        word_test = word_test.replace("\xa0", " ")
        regex_tx = r'(\d+,\d+|\d+)\s*\%'
        regex_period = r'(\d+)\s*(jours|$|e)'
        if re.search(r'\+', word_test):
            is_already_pass = True
            list_word = word_test.split("+")
            for word in list_word:
                tx_period = float(re.search(regex_tx, word).group(1)) / 100
                nbr_period = int(re.search(regex_period, word).group(1))
                list_data_period.append( [tx_period, nbr_period] )
        
        regex_type1 = r'(\d+,\d+|\d+)\s*%\s*à\s*compter\s*du\s*(\d+)\s*e' +\
            r'\s*jour\s*pendant\s*(\d+)\s*jours\s*puis\s*(\d+,\d+|\d+)\s*%'
        if re.search(regex_type1, word_test):
            is_already_pass = True
            tx_period_1 = 0
            tx_period_2 = float(re.search(regex_type1, word_test).group(1)) / 100
            tx_period_3 = float(re.search(regex_type1, word_test).group(4)) / 100
            nbr_period_1 = int(re.search(regex_type1, word_test).group(2)) - 1
            nbr_period_2 = int(re.search(regex_type1, word_test).group(3)) 
            nbr_period_3 = nbr_jour_total - (nbr_period_1 + nbr_period_2)
            list_data_period = [
                [tx_period_1, nbr_period_1], [tx_period_2, nbr_period_2],
                [tx_period_3, nbr_period_3]
            ]
        regex_type2 = r'(\d+,\d+|\d+)\s*%\s*à\s*compter\s*du\s*(\d+)\s*'
        if re.search(regex_type2, word_test) and not is_already_pass:
            is_already_pass = True
            tx_period_1 = 0
            tx_period_2 = float(re.search(regex_type2, word_test).group(1)) / 100
            nbr_period_1 = int(re.search(regex_type2, word_test).group(2)) - 1
            nbr_period_2 = nbr_jour_total - nbr_period_1
            list_data_period = [
                [tx_period_1, nbr_period_1], [tx_period_2, nbr_period_2]
                ]
        if not is_already_pass:
            try:
                tx_period = float(re.search(regex_tx, word_test).group(1)) / 100
            except Exception:
                tx_period = None
            try:
                nbr_period = int(re.search(regex_period, word_test).group(1))
            except Exception:
                nbr_period = None
            list_data_period = [[tx_period, nbr_period]]
    except Exception:
        message_warning = f"None of the regex has captured the data: {word_test}"
        logging.warning(message_warning)
        list_data_period = [[None, None]]
    return list_data_period

def extract_tx_period_from_data_table(data: pd.DataFrame) -> pd.DataFrame:
    indicator_period_add = 0
    data_copy = data.copy()
    for name_col in data_copy.columns:
        if re.search("Maintien du salaire", name_col):
            serie_traite = data_copy[name_col]
            for index_serie in serie_traite.index:
                list_of_tx_period = get_tx_period_from_data_for_csp(
                    word_test=serie_traite.loc[index_serie])
                for indicator_period, period_data in enumerate(list_of_tx_period):
                    data_copy.loc[
                        index_serie,
                        [f"taux_{indicator_period+1}", f"period_{indicator_period+1}"]
                        ] = period_data
                    indicator_period_add = max(indicator_period+1, indicator_period_add)
    return data_copy, indicator_period_add

def extract_tx_period_from_table(data: pd.DataFrame) -> pd.DataFrame:
    data_with_table, indicator_from_header = \
        extract_tx_period_from_header_table(data)
    indicator_from_table = 0
    if indicator_from_header == 0:
        data_with_table, indicator_from_table = \
            extract_tx_period_from_data_table(data)
    if indicator_from_header == 0 and indicator_from_table == 0:
        message_warning = f"None of columns hase been found"
        logging.warning(message_warning)
    return data_with_table

def update_data_to_add_born_min_with_row(
        data: pd.DataFrame,
        col_of_category: list,
        is_min: bool,
        value_to_affeced: int | float
        ) -> pd.DataFrame:
    data_to_update = data.copy()
    data_to_update.reset_index(inplace=True)
    if is_min:
        groupindex_born_limit = data_to_update.groupby(
            col_of_category)["born_min"].idxmin()
    else:
        groupindex_born_limit = data_to_update.groupby(
            col_of_category)["born_min"].idxmax()
    data_born_limit = data_to_update.loc[groupindex_born_limit, :]
    for indice_row in data_born_limit.index:
        row = data_born_limit.loc[indice_row, :]
        if row["born_min"] != value_to_affeced:
            max_index = data_to_update.index.max()
            data_to_update.loc[max_index+ 1,:] = \
                row
            data_to_update.loc[max_index+ 1, "born_min"] =\
                value_to_affeced
    if 'index' in data_to_update.columns:
        data_to_update.drop('index', inplace=True, axis=1)
    return data_to_update

def add_all_born_inf(data: pd.DataFrame) -> pd.DataFrame:
    data_to_complete = data.copy()
    col_categorie = [
        col 
        for col in data_to_complete.columns
            if re.search("catégorie", col.lower())
            ]
    if len(col_categorie) == 0:
        data_to_complete["categorie"] = "All"
        col_categorie = ["categorie"]
    data_to_complete["born_min"] = data_to_complete["born_min"].astype(float)
    data_to_complete = update_data_to_add_born_min_with_row(
        data = data_to_complete,
        col_of_category = col_categorie,
        is_min = True,
        value_to_affeced = 0
        )
    data_to_complete = update_data_to_add_born_min_with_row(
        data = data_to_complete,
        col_of_category = col_categorie,
        is_min = False,
        value_to_affeced = 43
        )
    df_of_all_born_min = pd.DataFrame(
        list(range(44)) + [0.5],
        columns=["born_min"])
    df_possible_value_for_categorie = pd.DataFrame(
        {col_categorie[0]: data_to_complete[col_categorie[0]].unique()}
        )
    df_born_min_template = pd.merge(
        df_of_all_born_min,
        df_possible_value_for_categorie,
        how='cross')
    #df_final[    df_final.columns[5:]] #créer la born maximal 43
    df_final = pd.merge(
        data_to_complete,
        df_born_min_template,
        on=['born_min', col_categorie[0]], how='right'
        ).sort_values(by = [col_categorie[0], 'born_min'])
    df_final = df_final.fillna(method='ffill')

    df_final["Id_csp"] = df_final["Id_csp"].apply(
        lambda id_csp: id_csp if not id_csp is np.nan
            else [1,2,3,4,5]
            )
    if col_categorie == ["categorie"]:
        df_final = df_final.drop(col_categorie, axis=1, inplace=False)
    return df_final

def add_all_csp_adapt_format_column(
        data: pd.DataFrame
        ) -> pd.DataFrame:
    data_to_complete = data.copy()
    # Créer un DataFrame résultant
    df_csp_index_to_join = pd.DataFrame(
        data_to_complete['Id_csp'].explode()
        ).rename({'Id_csp': 'categorieObjectiveId'}, axis=1)

    # Jointure on the index to add multiple csp on a column
    df_interm = data_to_complete.merge(
        df_csp_index_to_join['categorieObjectiveId'],
        how="outer",
        on=None, left_index=True, right_index=True
        )
    return df_interm

def format_data_to_template_csp(
        data: pd.DataFrame,
        length_col_initial: int
        ) -> pd.DataFrame:
    """
    data is the dataframe issued from the different step of enrichment.
    length_col_initial is the number of colum issued from the table of exportation.
    Return : a dataframe that hase the same column that the template csp.
        Add for the last columns the tauxperiod and period
    """
    df_template_csp = template_funct_csp()
    df_to_format = data.copy()
    # Adapt the coluns names
    df_intern_col_selected = df_to_format[
        df_to_format.columns[length_col_initial + 1:]
        ]
    mapping_name_col = {
        "taux_1" : "tauxPeriode1",
        "period_1" : "periode1",
        "taux_2" : "tauxPeriode2",
        "period_2" : "periode2",
        "taux_3" : "tauxPeriode3",
        "period_3" : "periode3",
        "taux_4" : "tauxPeriode4",
        "period_4" : "periode4",
        "taux_5" : "tauxPeriode5",
        "period_5" : "periode5",
        "born_min" : "anciennete"
        }
    dict_col_adapted = dict(
        zip(
            df_intern_col_selected.columns[:-1],
            [mapping_name_col[column]
                for column in df_intern_col_selected.columns[:-1]]
            )
        )
    df_formated = df_intern_col_selected.rename(dict_col_adapted, axis=1)
    df_template_csp[df_formated.columns] = df_formated
    list_col_period = [col for col in df_template_csp.columns if re.search('period', col)]
    list_taux_period = [col for col in df_template_csp.columns if re.search('tauxPeriode', col)]

    # Defined default value for first column that contains null 
    rows_col_period = df_template_csp[list_col_period].isna().idxmax(axis=1)
    rows_sum_period = nbr_jour_total - df_template_csp[list_col_period].sum(axis=1)
    for row, col in zip(rows_col_period.index, rows_col_period) :
        df_template_csp.loc[row, col] = rows_sum_period[row]

    rows_col_tauxperiod = df_template_csp[list_taux_period].isna().idxmax(axis=1)
    for row, col in zip(rows_col_tauxperiod.index, rows_col_tauxperiod) :
        df_template_csp.loc[row, col] = 0
    
    return df_template_csp

def filtre_unique_column(
        data_to_filtre_column: pd.DataFrame,
        length_col_initial: int
        ) -> pd.DataFrame:
    """
    Filtre columns that include 'Cas' to have only one item
    """
    data_filtred = data_to_filtre_column.copy()
    column_df_to_filtre = data_filtred.columns
    column_initial_to_filtre = column_df_to_filtre[:length_col_initial]
    for col_to_check in column_initial_to_filtre:
        if "Cas" in col_to_check:
            data_filtred["Index_Cas"] = \
                data_filtred.groupby(col_to_check).ngroup()
            if data_filtred["Index_Cas"].nunique() > 1:
                #Select the second element 
                mask_filtre_column = data_filtred["Index_Cas"] == 1
                data_filtred = \
                    data_filtred.loc[mask_filtre_column, :]
    
    if "Index_Cas" in data_filtred.columns:
        data_filtred.drop("Index_Cas", axis=1, inplace=True)
    return data_filtred

def adapt_data_for_condition(
        data_to_adapt: pd.DataFrame
        ) -> pd.DataFrame:
    column_df_to_adapt = data_to_adapt.columns
    list_col_to_melt = []
    list_col_unchanged = []
    for col_to_melt in column_df_to_adapt:
        if "maladie" in col_to_melt.lower():
            list_col_to_melt.append(col_to_melt)
        elif "at" in col_to_melt.lower() and \
            "mp" in col_to_melt.lower():
            list_col_to_melt.append(col_to_melt)
        else:
            list_col_unchanged.append(col_to_melt)
    if len(list_col_to_melt) > 0:
        df_after_melt = pd.melt(
            data_to_adapt,
            id_vars=list_col_unchanged,
            value_vars=list_col_to_melt,
            var_name='Cas',
            value_name='duree'
            )
        list_col_reorganized = ['Cas', 'duree'] +\
            list(set(column_df_to_adapt) - set(list_col_to_melt + ['Id_csp']))
        df_after_melt = df_after_melt[list_col_reorganized + ['Id_csp']]
    else:
        df_after_melt = data_to_adapt
    return df_after_melt

def generate_maintien_du_salaire_dataframe_formated(
        data_maintien_de_salaire_from_input: pd.DataFrame
        ) -> pd.DataFrame:
    """
    Extract the information of maintien du salaire for the prevoyance case
    Return The dataframe of data extracted et and boolean that
    shows if 'prevoyance' hase been detected in data
    """
    try:
        df_extracte = extract_and_add_csp(
            df_maintien_de_salaire = data_maintien_de_salaire_from_input
            )
        if df_extracte.empty:
            data_formated_complet = df_extracte
            is_prevoyance = False
        else:
            df_extracte_adapted = adapt_data_for_condition(
                data_to_adapt = df_extracte
                )
            count_columns_exacte = len(df_extracte_adapted.columns) - 1
            data_extract_filtred = filtre_unique_column(
                data_to_filtre_column = df_extracte_adapted,
                length_col_initial = count_columns_exacte
                ) 
            df_extracted_tx_period = extract_tx_period_from_table(
                data = data_extract_filtred
                )
            df_with_born = add_born_min_to_df(
                data = df_extracted_tx_period
                )
            df_complet_with_all_born = add_all_born_inf(
                data = df_with_born
                )

            df_complet_with_all_csp = add_all_csp_adapt_format_column(
                data = df_complet_with_all_born
                )
            data_formated_complet = format_data_to_template_csp(
                data = df_complet_with_all_csp,
                length_col_initial = count_columns_exacte
                )
            is_prevoyance = True
    except Exception as e:
        logging.error(Exception)
        raise e
    return data_formated_complet, is_prevoyance

def update_dataframe_with_meta_data(
        data_to_update: pd.DataFrame,
        data_transco_IDCC: dict,
        path_input_file: str,
        name_file: str
        ) -> pd.DataFrame:
    df_meta_data = get_meta_data(
            path_file = path_input_file,
            name_file = "IDCC"
            )
    if not df_meta_data.empty and not data_to_update.empty:
        data_updated = data_to_update.merge(
                df_meta_data,
                how = 'cross',
                )
        data_updated['ccnId'] = data_updated["ccnId"].apply(
            lambda idcc: data_transco_IDCC["IDCC"][name_file]
                if idcc == '-' and name_file in data_transco_IDCC["IDCC"]
                else idcc
            )
    else:
        data_updated = df_meta_data
        if data_updated.empty:
            data_updated["dataEff"] = None
            if  name_file in  data_transco_IDCC["IDCC"]:
                value_IDCC = data_transco_IDCC["IDCC"][name_file]
                if not np.isnan(value_IDCC):
                    value_IDCC = int(value_IDCC)
            else:
                value_IDCC = None
                message_warning = f"The meta data of the file :" +\
                    f"{name_file} is lacking." 
                logging.warning(message_warning)
            data_updated["ccnId"] = value_IDCC 
        
    data_updated["dateCreation"] = datetime.today()
    return data_updated

def get_template_output_empty() -> pd.DataFrame:
    max_year_anciennete = 43
    df_template = template_funct_csp()
    df_anciennete = pd.DataFrame(
        list(range(max_year_anciennete + 1)) + [0.5],
        columns=["anciennete"])
    df_csp = pd.DataFrame(
        [1, 2, 3, 4, 5],
        columns=["categorieObjectiveId"])
    df_merged = df_anciennete.merge(
        df_csp,
        how="cross",
        )
    df_template["anciennete"] = df_merged["anciennete"]
    df_template["categorieObjectiveId"] = df_merged["categorieObjectiveId"]
    df_template["tauxPeriode1"] = 0
    df_template["periode1"] = nbr_jour_total
    return df_template
    

def fill_empty_df_with_basic_data(
        list_of_df_empty: pd.DataFrame
        ) -> pd.DataFrame:
    list_of_df_fill = []
    for name, df_name in list_of_df_empty:
        if 'ccnId' in df_name.columns and \
                not df_name.isna()['ccnId'].any():
            template = get_template_output_empty()
            tmpl_merged = template.merge(df_name, how="cross")
            list_of_df_fill.append(tmpl_merged)
    if len(list_of_df_fill) > 0:
        df_concat = pd.concat(list_of_df_fill)
    else:
        df_concat = template_funct_csp()
    return df_concat

# Il manque l'extraction des information à partir de Maintien du salaire
# La complétion 

if __name__ == "__name__":
    from function_extraction import extract_name_folder
    path_source = os.getcwd()
    name_folder_files_xlsx_extracted = "export_extraction_test"
    path_folder_extracted = os.path.join(path_source, name_folder_files_xlsx_extracted)
    list_name_files_xlsx_extracted = extract_name_folder(path_folder_extracted)

    df_template_csp = template_funct_csp()

    for names in list_name_files_xlsx_extracted:
        print(names)

    path_input_xlsx = os.path.join(path_folder_extracted, list_name_files_xlsx_extracted[-1][2:])
    path_input_agri = os.path.join(path_folder_extracted, list_name_files_xlsx_extracted[4])
    path_input_bur_etude = os.path.join(path_folder_extracted, list_name_files_xlsx_extracted[-3])

    dt_maintien_de_salaire = import_file_data(
            path_file = path_input_xlsx,
            sheet_name = 'Maintien de salaire'
            )
    df_maintien_de_salaire = import_file_maintien_de_salaire(
                path_input = path_input_xlsx
                )


    dt_agri_maintien_de_salaire = import_file_data(
            path_file = path_input_agri,
            sheet_name = 'Maintien de salaire'
            )
    dt_etude_maintien_de_salaire = import_file_data(
            path_file = path_input_bur_etude,
            sheet_name = 'Maintien de salaire'
            )

    # fuction : Formate data import and normalised
    df_extracte = extract_and_add_csp(df_maintien_de_salaire=dt_maintien_de_salaire)
    df_extracte_agri = extract_and_add_csp(df_maintien_de_salaire=dt_agri_maintien_de_salaire)
    df_extracte_etude = extract_and_add_csp(df_maintien_de_salaire=dt_etude_maintien_de_salaire)

    count_columns_exacte = len(df_extracte.columns) - 1
    count_columns_agri = len(df_extracte_agri.columns) - 1
    count_columns_etude = len(df_extracte_etude.columns) - 1

    df_exacte_tx_period = extract_tx_period_from_table(data = df_extracte)
    df_agri_tx_period = extract_tx_period_from_table(data = df_extracte_agri)
    df_etude_tx_period = extract_tx_period_from_table(data = df_extracte_etude)

    df_exact_with_born_tx_period = add_born_min_to_df(data = df_exacte_tx_period)
    df_agri_with_born_tx_period = add_born_min_to_df(data = df_agri_tx_period)
    df_etude_with_born_tx_period = add_born_min_to_df(data = df_etude_tx_period)

    df_extract_prevoyance_clean = select_extract_data_for_prevoyance(
        data_extracted = dt_maintien_de_salaire
    )

    df_extract_prevoyance_clean_agri = select_extract_data_for_prevoyance(
        data_extracted = dt_agri_maintien_de_salaire
    )

    df_extract_prevoyance_clean_bureau = select_extract_data_for_prevoyance(
        data_extracted = dt_etude_maintien_de_salaire
    )

    list_col_clean_csp = extract_csp_from_header(
            list_columns_data = dt_maintien_de_salaire.columns
            )

    list_col_clean_csp_agri = list_col_clean_csp = extract_csp_from_header(
            list_columns_data = dt_agri_maintien_de_salaire.columns
            )

    df_transform_clean = transforme_data_extracted(df_extract_prevoyance_clean_bureau)
    df_transform_clean_agri = transforme_data_extracted(data_clean=df_extract_prevoyance_clean_agri)

    df_with_category_csp, is_csp_add = extract_csp_from_table(data = df_transform_clean)
    df_with_category_csp_agri, is_csp_add_agri = extract_csp_from_table(data = df_transform_clean_agri)

    df_with_category_csp_agri["Id_csp"] = np.nan

    if not "Id_csp" in df_with_category_csp_agri.columns:
        df_with_category_csp_agri["Id_csp"] = list_col_clean_csp
    else:
        df_with_category_csp_agri["Id_csp"] = \
            df_with_category_csp_agri["Id_csp"].apply(
                lambda id_csp: id_csp if (id_csp is None) or (id_csp is np.nan) 
                    else list_col_clean_csp_agri
            )

    texte = " De 1 à 15 ans révolus"
    texte = "Entre 6 mois et 6 ans"
    texte = "A partir de 31 ans"
    texte = "> 12 ans"
    texte = "autre"

    df_data_with_born_min = add_born_min_to_df(
            data = df_transform_clean
            )

    df_extract_prevoyance_clean = select_extract_data_for_prevoyance(
        data_extracted = dt_etude_maintien_de_salaire
    )

