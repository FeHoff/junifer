import pytest

from junifer.storage.base import (process_meta, _element_to_index,
                                  BaseFeatureStorage)


def test_process_meta_hash():
    """Test meta_hash"""

    meta = None
    with pytest.raises(ValueError, match=r"Meta must be a dict"):
        process_meta(meta)

    meta = {'element': 'foo', 'A': 1, 'B': [2, 3, 4, 5, 6]}
    hash1, _ = process_meta(meta, return_idx=False)  # type: ignore

    meta = {'element': 'foo', 'B': [2, 3, 4, 5, 6], 'A': 1}
    hash2, _ = process_meta(meta, return_idx=False)  # type: ignore
    assert hash1 == hash2

    meta = {'element': 'foo', 'A': 1, 'B': [2, 3, 1, 5, 6]}
    hash3, _ = process_meta(meta, return_idx=False)  # type: ignore
    assert hash1 != hash3

    meta1 = {
        'element': 'foo',
        'B': {
            'B2': [2, 3, 4, 5, 6],
            'B1': [9.22, 3.14, 1.41, 5.67, 6.28],
            'B3': (1, 'car'),
        },
        'A': 1}

    meta2 = {
        'A': 1,
        'B': {
            'B3': (1, 'car'),
            'B1': [9.22, 3.14, 1.41, 5.67, 6.28],
            'B2': [2, 3, 4, 5, 6],
        },
        'element': 'foo'
    }

    hash4, _ = process_meta(meta1, return_idx=False)  # type: ignore
    hash5, _ = process_meta(meta2, return_idx=False)  # type: ignore
    assert hash4 == hash5


def test_process_meta_element():
    """Test meta element"""

    meta = {}
    with pytest.raises(ValueError, match=r"_element_keys"):
        process_meta(meta, return_idx=False)

    meta = {'element': 'foo', 'A': 1, 'B': [2, 3, 4, 5, 6]}
    _, new_meta = process_meta(meta, return_idx=False)  # type: ignore
    assert '_element_keys' in new_meta
    assert new_meta['_element_keys'] == ['element']
    assert 'A' in new_meta
    assert 'B' in new_meta

    meta = {
        'element': {'subject': 'foo', 'session': 'bar'},
        'B': [2, 3, 4, 5, 6], 'A': 1}
    _, new_meta = process_meta(meta, return_idx=False)  # type: ignore
    assert '_element_keys' in new_meta
    assert new_meta['_element_keys'] == ['subject', 'session']
    assert 'A' in new_meta
    assert 'B' in new_meta


def test_process_meta_index():
    """Test _element_to_index"""

    meta = {'noelement': 'foo'}
    with pytest.raises(ValueError, match=r'meta must contain the key'):
        _element_to_index(meta)

    meta = {'element': 'foo', 'A': 1, 'B': [2, 3, 4, 5, 6]}
    index = _element_to_index(meta)
    assert index.names == ['element']
    assert index.levels[0].name == 'element'
    assert index.levels[0].values[0] == 'foo'

    index = _element_to_index(meta, n_rows=10)
    assert index.names == ['element', 'index']
    assert index.levels[0].name == 'element'
    assert all(x == 'foo' for x in index.levels[0].values)
    assert index.levels[0].values.shape == (1,)

    assert index.levels[1].name == 'index'
    assert all(x == i for i, x in enumerate(index.levels[1].values))
    assert index.levels[1].values.shape == (10,)

    index = _element_to_index(meta, n_rows=1, rows_col_name='scan')
    assert index.names == ['element']
    assert index.levels[0].name == 'element'
    assert all(x == 'foo' for x in index.levels[0].values)
    assert index.levels[0].values.shape == (1,)

    index = _element_to_index(meta, n_rows=7, rows_col_name='scan')
    assert index.names == ['element', 'scan']
    assert index.levels[0].name == 'element'
    assert all(x == 'foo' for x in index.levels[0].values)
    assert index.levels[0].values.shape == (1,)

    assert index.levels[1].name == 'scan'
    assert all(x == i for i, x in enumerate(index.levels[1].values))
    assert index.levels[1].values.shape == (7,)

    meta = {
        'element': {'subject': 'sub-01', 'session': 'ses-01'},
        'A': 1, 'B': [2, 3, 4, 5, 6]}
    index = _element_to_index(meta, n_rows=10)

    assert index.levels[0].name == 'subject'
    assert all(x == 'sub-01' for x in index.levels[0].values)
    assert index.levels[0].values.shape == (1,)

    assert index.levels[1].name == 'session'
    assert all(x == 'ses-01' for x in index.levels[1].values)
    assert index.levels[1].values.shape == (1,)

    assert index.levels[2].name == 'index'
    assert all(x == i for i, x in enumerate(index.levels[2].values))
    assert index.levels[2].values.shape == (10,)


def test_BaseFeatureStorage():
    """Test BaseFeatureStorage"""
    with pytest.raises(TypeError, match=r"abstract"):
        BaseFeatureStorage(uri='/tmp')  # type: ignore

    class MyFeatureStorage(BaseFeatureStorage):
        def validate(self, input):
            super().validate(input)

        def list_features(self):
            super().list_features()

        def read_df(self, feature_name=None, feature_md5=None):
            super().read_df(
                feature_name=feature_name, feature_md5=feature_md5)

        def store_metadata(self, metadata):
            super().store_metadata(metadata)

        def store_matrix2d(self, matrix, meta):
            super().store_matrix2d(matrix, meta)

        def store_table(self, table, meta):
            super().store_table(table, meta)

        def store_df(self, df, meta):
            super().store_df(df, meta)

        def store_timeseries(self, timeseries, meta):
            super().store_timeseries(timeseries, meta)

    st = MyFeatureStorage(uri='/tmp')

    with pytest.raises(NotImplementedError):
        st.validate(None)

    with pytest.raises(NotImplementedError):
        st.list_features()

    with pytest.raises(NotImplementedError):
        st.read_df(None)

    with pytest.raises(NotImplementedError):
        st.store_metadata(None)

    with pytest.raises(NotImplementedError):
        st.store_matrix2d(None, None)

    with pytest.raises(NotImplementedError):
        st.store_table(None, None)

    with pytest.raises(NotImplementedError):
        st.store_df(None, None)

    with pytest.raises(NotImplementedError):
        st.store_timeseries(None, None)

    assert st.uri == '/tmp'
