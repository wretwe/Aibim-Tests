import json
import pandas as pd
from typing import List, Dict
import re


def json_extracter(path: str, elem: int = 0, tag: str = "Name") -> List[str]:
    """Extract data from json

    Args:
        path (str): path to file
        elem (int, optional): Key[elem] to sort. Defaults to 0.
        tag (str, optional): Key to sort. Defaults to "Name".

    Returns:
        List[str]: Sorted json by tag[elem]
    """
    def sorter(info: List[str]) -> List[str]:
        """Sorter to json"""
        return sorted(info, key=lambda x: x[tag].split()[elem])

    with open('JSON\\'+path, encoding='utf8') as inf:
        return sorter(json.load(inf))


def only_in_small(sm: pd.DataFrame, big: pd.DataFrame) -> pd.DataFrame:
    """People, which only in sm, and not in big

    Args:
        sm (pd.DataFrame): df_small
        big (pd.DataFrame): df_big

    Returns:
        pd.DataFrame
    """
    return sm[sm.Name.isin(set(sm.Name) - set(big.Name))]


def namesakes(sm: pd.DataFrame, big: pd.DataFrame, dif: int = 10) -> pd.DataFrame:
    """Namesakes whose age difference = dif

    Args:
        sm (pd.DataFrame): df_small
        big (pd.DataFrame): df_big
        dif (int, optional): age difference. Defaults to 10.

    Returns:
        pd.DataFrame
    """
    def f(x): return x[1]["Name"].split()[0]

    surn: Dict[str, str] = dict()
    for i in big.iterrows():
        if f(i) not in surn:
            surn[f(i)] = [i[1]["Age"]]
        else:
            surn[f(i)].append(i[1]["Age"])

    df_names: pd.DataFrame = pd.DataFrame()
    for i in sm.iterrows():
        if f(i) in surn:
            for j in surn[f(i)]:
                if abs(int(j) - int(i[1]["Age"])) == dif:
                    df_names = df_names.append(i[1], ignore_index=True)

    return df_names


def english_leter_in(sm: pd.DataFrame, big: pd.DataFrame) -> List[str]:
    """People, whose name/surname has еnglish letter in

    Args:
        sm (pd.DataFrame): df_small
        big (pd.DataFrame): df_big

    Returns:
        List[str]
    """
    df = pd.concat([sm, big], ignore_index=True)
    return [i[1] for i in df.iterrows() if re.search(r'[a-zA-Z]', i[1]["Name"])]
    # return df[df["Name"].str.match(r'[a-zA-Z]')]


if __name__ == "__main__":
    temp_small: List[str] = json_extracter('small_data_persons.json', 0)
    temp_big: List[str] = json_extracter('big_data_persons.json', 1)

    # завозим наши json-данные в DataFrames
    df_small: pd.DataFrame = pd.DataFrame(temp_small)
    df_big: pd.DataFrame = pd.DataFrame(temp_big)

    df_miss: pd.DataFrame = only_in_small(df_small, df_big)
    df_eng: pd.DataFrame = pd.DataFrame(english_leter_in(df_small, df_big))
    df_name: pd.DataFrame = namesakes(df_small, df_big)

    # список листов: их названия и содержимое
    sheets: Dict[str, pd.DataFrame] = {
        'small_data': df_small,
        'big_data': df_big,
        'missing names': df_miss,
        'english_leter_in': df_eng,
        'namesakes': df_name
    }

    # запись в файл .xlsx
    with pd.ExcelWriter('data_json_1.xlsx', engine='xlsxwriter') as writer:
        for sheet_name, sheed_data in sheets.items():
            sheets[sheet_name].to_excel(
                writer, sheet_name=sheet_name, index=False)