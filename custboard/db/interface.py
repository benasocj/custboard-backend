from datetime import date, datetime, timedelta

from custboard import d
from custboard.db import declarative as decl


def get_partners():
    r = []
    for p in d.session.query(decl.Partner).order_by(decl.Partner.name):
        if p.name.strip():
            r.append({'id': p.id_, 'name': p.name})
    return r


def _get_midnight():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def _get_conversion_base_query(partner_id):
    return (d.session
        .query(
            d.func.max(decl.OrderSSCC.time_closed).label('time_closed'),
            )
        .join(decl.OrderSSCC.order_store)
        .filter(
            decl.OrderStore.partner_id == partner_id,
            decl.OrderStore.status == 'P',
            decl.OrderSSCC.date_closed == date.today())
        .group_by(
            decl.OrderStore.entity,
            decl.OrderStore.partner_id,
            decl.OrderStore.order_id,
            decl.OrderStore.store_loc,
            )
        .subquery())


def get_conversion_current(partner_id, within_seconds):
    sub = _get_conversion_base_query(partner_id)

    cutoff_time = int(
        (datetime.now() - timedelta(seconds=within_seconds) - _get_midnight())
        .total_seconds())
    return (d.session
        .query(d.func.count(sub.c.time_closed))
        .filter(sub.c.time_closed >= cutoff_time)
        .scalar())


def get_conversion_history(partner_id, seconds_group):
    sub = _get_conversion_base_query(partner_id)

    query = (d.session
        .query(
            # `text(...)` used because of Progress's limitation to use
            # placeholders within select list.
            ((d.cast(sub.c.time_closed / d.text(str(seconds_group)), d.Integer)
                + d.text(str(1))) * d.text(str(seconds_group)))
                .label('interval'),
            d.func.count(sub.c.time_closed).label('orders_cnt'))
        .group_by('interval'))

    r = {}
    for i in query:
        key = (_get_midnight() + timedelta(seconds=i.interval)).isoformat()
        r[key] = i.orders_cnt
    return r


def _get_pieces_per_order(partner_id, filter_list):
    sub = (d.session
        .query(
            d.func.sum(decl.OrderLine.qty_picked).label('pieces_per_order'),
            )
        .join(decl.OrderLine.order_store)
        .join(decl.OrderStore.order_header)
        .filter(
            decl.OrderStore.partner_id == partner_id,
            *filter_list)
        .group_by(
            decl.OrderStore.entity,
            decl.OrderStore.partner_id,
            decl.OrderStore.order_id,
            decl.OrderStore.store_loc,
            )
        .subquery())

    return (d.session
        .query(
            d.func.count(sub.c.pieces_per_order).label('orders'),
            # `text(...)` used because of Progress's limitation to use
            # placeholders within select list.
            d.func.coalesce(d.func.sum(sub.c.pieces_per_order), d.text(str(0)))
                .label('units'),
            )
        .one()
        ._asdict())


def get_released(partner_id):
    return _get_pieces_per_order(
        partner_id,
        [
            decl.OrderStore.status.notin_(['P', 'T']),
            decl.OrderStore.sys_id.isnot(None),
            decl.OrderHeader.date_amended == date.today(),
            ]
        )


def get_packed(partner_id):
    return _get_pieces_per_order(
        partner_id,
        [
            decl.OrderStore.status == 'P',
            decl.OrderHeader.date_amended == date.today(),
            ]
        )


def get_today(partner_id):
    return _get_pieces_per_order(
        partner_id,
        [
            decl.OrderStore.sys_id.is_(None),
            decl.OrderHeader.date_created == date.today(),
            ]
        )


def get_old(partner_id):
    return _get_pieces_per_order(
        partner_id,
        [
            decl.OrderStore.sys_id.is_(None),
            decl.OrderHeader.date_created < date.today(),
            ]
        )
