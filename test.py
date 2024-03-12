test_date = list_sections[0]["content"][2]
class_mot_date = "DATEMAJ"

#permet d'extraire la date de mise à jour
soup1 = BeautifulSoup(test_date, 'html.parser')
for elm in soup.find_all(class_='DATEMAJ'):
    print(elm.text.split(':')[-1])

for elm in soup.find_all(class_='TYPE0-1COL'):
    tb_IDCC = elm

header = extract_header(tb_IDCC)
cells = extract_cell(tb_IDCC, header)

# permet l'extraction de L'IDCC 
dict_notion["IDCC"]["title"]['IDCC'][0]["title"][0].replace("\xa0", " ")


def extract_meta_data(soup) -> pd.DataFrame:
    """
    Extract 2 informations:
        - Effective date
        - IDCC
    Download this informations inside a dictionnary
    """
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
    return df_meta_data

df_meta_data = extract_meta_data(soup)
