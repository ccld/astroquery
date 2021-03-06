# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Utilities for working with Splatalogue query results
"""
import numpy as np
import astropy

column_headings_map = {'Log<sub>10</sub> (A<sub>ij</sub>)': 'log10(Aij)',
                       'E_U (K)': 'EU_K',
                       'Resolved QNs': 'QNs'}


def clean_column_headings(table, renaming_dict=column_headings_map):
    """
    Rename column headings to shorter version that are easier for display
    on-screen / at the terminal
    """

    for key in renaming_dict:
        if key in table.colnames:
            table.rename_column(key, renaming_dict[key])

    return table


def merge_frequencies(table, prefer='measured', theor_kwd='Freq-GHz',
                      meas_kwd='Meas Freq-GHz'):
    """
    Replace "Freq-GHz" and "Meas Freq-GHz" with a single "Freq" column.

    Parameters
    ----------
    table : table
        The Splatalogue table
    prefer: 'measured' or 'theoretical'
        Which of the two colums to prefer if there is a conflict
    """

    if prefer == 'measured':
        Freq = np.copy(table[theor_kwd])
        measmask = np.logical_not(table[meas_kwd].mask)
        Freq[measmask] = table[meas_kwd][measmask]
    elif prefer == 'theoretical':
        Freq = np.copy(table[meas_kwd])
        theomask = np.logical_not(table[theor_kwd].mask)
        Freq[measmask] = table[theor_kwd][theomask]
    else:
        raise ValueError('prefer must be one of "measured" or "theoretical"')

    index = table.index_column(theor_kwd)
    table.remove_columns([theor_kwd, meas_kwd])
    newcol = astropy.table.Column(name='Freq', data=Freq)
    table.add_column(newcol, index=index)

    return table


def minimize_table(table, columns=['Species', 'Chemical Name',
                                   'Resolved QNs', 'Freq-GHz', 'Meas Freq-GHz',
                                   'Log<sub>10</sub> (A<sub>ij</sub>)',
                                   'E_U (K)'],
                   merge=True,
                   clean=True):
    """
    Strip a table's headers and rename them to their minimalist form

    Parameters
    ----------
    table : table
        The Splatalogue table
    columns : list
        A list of column names to keep before merging and cleaning
    merge : bool
        Run merge_frequencies to get a single reported frequency for each line?
    clean_column_headings : bool
        Run clean_column_headings to shorted the headers?
    """

    table = table[columns]

    if merge:
        table = merge_frequencies(table)
    if clean:
        table = clean_column_headings(table)

    return table
