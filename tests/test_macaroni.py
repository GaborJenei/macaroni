import sys
sys.path.append('../')
import pandas as pd
import numpy as np
from pandas import testing as tm
from macaroni.data import make_data


def test_decompose_name_1():
    name = 'Mr. Brandon Thornton'
    result = pd.Series(['Mr.', 'Brandon', 'Thornton'])
    output = make_data.decompose_name(name)

    tm.assert_series_equal(output, result)


def test_decompose_name_2():
    name = 'Joel Allen'
    result = pd.Series([np.NaN, 'Joel', 'Allen'])
    output = make_data.decompose_name(name)

    tm.assert_series_equal(output, result)


def test_decompose_name_3():
    name = 'Ms. Catherine Zeta Jones'
    result = pd.Series(['Ms.', 'Catherine', 'Jones'])
    output = make_data.decompose_name(name)

    tm.assert_series_equal(output, result)


# TODO: Add more tests