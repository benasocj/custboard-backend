from datetime import date
import json

import pytest

from custboard import d
from custboard.db import declarative as decl, interface


@pytest.fixture
def call_and_unpack(client):
    def call(url):
        return json.loads(client.get(url).get_data().decode())

    return call


def test_get_partners(call_and_unpack):
    d.session.add(decl.Partner('pa1', 'name1'))
    d.session.add(decl.Partner('pa2', 'name2'))

    assert call_and_unpack('/partners') == [
            {'id': 'pa1', 'name': 'name1'},
            {'id': 'pa2', 'name': 'name2'},
        ]

def test_get_data(call_and_unpack):
    pa1 = decl.Partner('pa1')

    oh1 = decl.OrderHeader('en1', pa1, 'or1', date.today())
    oh2 = decl.OrderHeader('en1', pa1, 'or2',
                           date_created=date.today())
    oh3 = decl.OrderHeader('en1', pa1, 'or3',
                           date_created=date(2017, 1, 1))

    os1 = decl.OrderStore(oh1, 'sl1', 'I', 1)
    os2 = decl.OrderStore(oh1, 'sl2', 'P')
    os3 = decl.OrderStore(oh2, 'sl1')
    os4 = decl.OrderStore(oh3, 'sl2')

    d.session.add(decl.OrderLine(os1, 1, 1))
    d.session.add(decl.OrderLine(os2, 1, 2))
    d.session.add(decl.OrderLine(os3, 1, 4))
    d.session.add(decl.OrderLine(os4, 1, 8))

    r = call_and_unpack('/partners/pa1/data')
    del r['chartData']
    del r['conversion']
    assert r == {
        'released': {'orders': 1, 'units': 1},
        'packed': {'orders': 1, 'units': 2},
        'openToday': {'orders': 1, 'units': 4},
        'openOld': {'orders': 1, 'units': 8},
        }
