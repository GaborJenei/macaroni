import pandas as pd
import numpy as np
from pandas import testing as tm

import sys
sys.path.append('../')
from macaroni.data import make_data


def test_decompose_name_1():
    """
    Test a name with 3 components: title, first name and last name
    """
    name = 'Mr. Brandon Thornton'
    result = pd.Series(['Mr.', 'Brandon', 'Thornton'])
    output = make_data.decompose_name(name)

    tm.assert_series_equal(output, result)


def test_decompose_name_2():
    """
    Test a name with 2 components: first name and last name
    """
    name = 'Joel Allen'
    result = pd.Series([np.NaN, 'Joel', 'Allen'])
    output = make_data.decompose_name(name)

    tm.assert_series_equal(output, result)


def test_decompose_name_3():
    """
    Test a name with 4 components: first name, middle name and last name
    """
    name = 'Ms. Catherine Zeta Jones'
    result = pd.Series(['Ms.', 'Catherine', 'Jones'])
    output = make_data.decompose_name(name)

    tm.assert_series_equal(output, result)


# TODO: Add more tests
