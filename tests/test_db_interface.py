from datetime import date, datetime, timedelta

import pytest

from custboard import d
from custboard.db import declarative as decl, interface


class TestGetPiecesPerOrder:
    def test_group_by(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1')
        oh2 = decl.OrderHeader('en1', pa1, 'or2')

        os1 = decl.OrderStore(oh1, 'sl1')
        os2 = decl.OrderStore(oh1, 'sl2')
        os3 = decl.OrderStore(oh2, 'sl1')

        d.session.add(decl.OrderLine(os1, 1, 1))
        d.session.add(decl.OrderLine(os1, 2, 2))
        d.session.add(decl.OrderLine(os2, 1, 4))
        d.session.add(decl.OrderLine(os2, 2, 8))
        d.session.add(decl.OrderLine(os3, 1, 16))
        d.session.add(decl.OrderLine(os3, 2, 32))

        assert interface._get_pieces_per_order('pa1', []) == {
            'orders': 3, 'units': 63}

    def test_order_store_without_line(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1')
        oh2 = decl.OrderHeader('en1', pa1, 'or2')

        os1 = decl.OrderStore(oh1, 'sl1')
        os2 = decl.OrderStore(oh2, 'sl2')
        d.session.add(os2)

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert (
            interface._get_pieces_per_order('pa1', [])['orders'] == 1)


class TestReleased:
    def test_wrong_status(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date.today())

        os1 = decl.OrderStore(oh1, 'sl1', 'P', 1)
        os2 = decl.OrderStore(oh1, 'sl2', 'T', 1)

        d.session.add(decl.OrderLine(os1, 1, 1))
        d.session.add(decl.OrderLine(os2, 1, 1))

        assert interface.get_released('pa1')['orders'] == 0

    def test_empty_sys_id(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date.today())

        os1 = decl.OrderStore(oh1, 'sl1', 'I')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_released('pa1')['orders'] == 0

    def test_wrong_date(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1', 'I', 1)

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_released('pa1')['orders'] == 0

    def test_ok(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date.today())

        os1 = decl.OrderStore(oh1, 'sl1', '', 1)
        os2 = decl.OrderStore(oh1, 'sl2', 'I', 1)

        d.session.add(decl.OrderLine(os1, 1, 1))
        d.session.add(decl.OrderLine(os2, 1, 1))

        assert interface.get_released('pa1')['orders'] == 2


class TestPacked:
    def test_wrong_status(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date.today())

        os1 = decl.OrderStore(oh1, 'sl1', '')
        os2 = decl.OrderStore(oh1, 'sl2', 'I')
        os3 = decl.OrderStore(oh1, 'sl3', 'T')

        d.session.add(decl.OrderLine(os1, 1, 1))
        d.session.add(decl.OrderLine(os2, 1, 1))
        d.session.add(decl.OrderLine(os3, 1, 1))

        assert interface.get_packed('pa1')['orders'] == 0

    def test_wrong_date(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1', 'P')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_packed('pa1')['orders'] == 0

    def test_ok(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1', date.today())

        os1 = decl.OrderStore(oh1, 'sl1', 'P')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_packed('pa1')['orders'] == 1


class TestToday:
    def test_non_empty_sys_id(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date.today())

        os1 = decl.OrderStore(oh1, 'sl1', sys_id=1)

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_today('pa1')['orders'] == 0

    def test_wrong_date(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_today('pa1')['orders'] == 0

    def test_ok(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date.today())

        os1 = decl.OrderStore(oh1, 'sl1')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_today('pa1')['orders'] == 1


class TestOld:
    def test_non_empty_sys_id(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1', sys_id=1)

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_old('pa1')['orders'] == 0

    def test_wrong_date(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date.today())

        os1 = decl.OrderStore(oh1, 'sl1')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_old('pa1')['orders'] == 0

    def test_ok(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1')

        d.session.add(decl.OrderLine(os1, 1, 1))

        assert interface.get_old('pa1')['orders'] == 1


class TestPartners:
    def test_empty_name(self):
        d.session.add(decl.Partner('pa1', ' '))
        d.session.add(decl.Partner('pa2', ''))

        assert interface.get_partners() == []

    def test_ok(self):
        d.session.add(decl.Partner('pa6', 'name4'))
        d.session.add(decl.Partner('pa7', 'name3'))
        d.session.add(decl.Partner('pa8', 'name2'))
        d.session.add(decl.Partner('pa9', 'name1'))

        assert interface.get_partners() == [
                {'id': 'pa9', 'name': 'name1'},
                {'id': 'pa8', 'name': 'name2'},
                {'id': 'pa7', 'name': 'name3'},
                {'id': 'pa6', 'name': 'name4'},
            ]


class TestConversionHistory:
    def test_ok(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1', 'P')
        os2 = decl.OrderStore(oh1, 'sl2', 'P')
        os3 = decl.OrderStore(oh1, 'sl3', 'P')
        os4 = decl.OrderStore(oh1, 'sl4', 'P')

        today = date.today()
        d.session.add(decl.OrderSSCC(os1, 'ss1', today, 3600 * 7))
        d.session.add(decl.OrderSSCC(os2, 'ss1', today, 3600 * 7 + 60))
        d.session.add(decl.OrderSSCC(os3, 'ss1', today, 3600 * 7 + 120))
        d.session.add(decl.OrderSSCC(os4, 'ss1', today, 3600 * 7 + 180))

        assert interface.get_conversion_history('pa1', 60 * 3) == {
            '{}T07:03:00'.format(today.isoformat()): 3,
            '{}T07:06:00'.format(today.isoformat()): 1,
            }


class TestConversionCurrent:
    def test_ok(self):
        pa1 = decl.Partner('pa1')

        oh1 = decl.OrderHeader('en1', pa1, 'or1',
                               date_created=date(2017, 1, 1))

        os1 = decl.OrderStore(oh1, 'sl1', 'P')
        os2 = decl.OrderStore(oh1, 'sl2', 'P')
        os3 = decl.OrderStore(oh1, 'sl3', 'P')

        def _get_test_date(now, seconds):
            tstamp = now - timedelta(seconds=seconds)
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return tstamp, midnight

        now = datetime.now()

        tstamp, midnight = _get_test_date(now, 70)
        d.session.add(decl.OrderSSCC(os1, 'ss1', tstamp.date(),
                                    int((tstamp - midnight).total_seconds())))
        tstamp, midnight = _get_test_date(now, 20)
        d.session.add(decl.OrderSSCC(os2, 'ss1', tstamp.date(),
                                    int((tstamp - midnight).total_seconds())))
        tstamp, midnight = _get_test_date(now, 10)
        d.session.add(decl.OrderSSCC(os3, 'ss1', tstamp.date(),
                                    int((tstamp - midnight).total_seconds())))

        assert interface.get_conversion_current('pa1', 60) == 2
