from custboard import d


class Partner(d.Model):
    __tablename__ = 'partner'
    __table_args__ = (
        d.PrimaryKeyConstraint('pa_partner'),)

    id_ = d.Column('pa_partner', d.Text)

    name = d.Column('pa_name', d.Text)

    def __init__(self, id_, name=None):
        self.id_ = id_
        self.name = name


class OrderHeader(d.Model):
    __tablename__ = 'order_hdr'
    __table_args__ = (
        d.PrimaryKeyConstraint('en_entity', 'pa_partner', 'oh_order'),
        d.ForeignKeyConstraint(['pa_partner'], ['partner.pa_partner']))

    entity = d.Column('en_entity', d.Text)
    partner_id = d.Column('pa_partner', d.Text)
    order_id = d.Column('oh_order', d.Text)

    status = d.Column('oh_status', d.Text)
    date_amended = d.Column('oh_amend', d.Date)
    date_created = d.Column('oh_created', d.Date)

    partner = d.relationship('Partner')

    def __init__(self, entity, partner, order_id, status=None,
                 date_amended=None, date_created=None):
        self.entity = entity
        self.partner = partner
        self.order_id = order_id
        self.status = status
        self.date_amended = date_amended
        self.date_created = date_created


class OrderStore(d.Model):
    __tablename__ = 'order_str'
    __table_args__ = (
        d.PrimaryKeyConstraint(
            'en_entity', 'pa_partner', 'oh_order', 'os_store_loc'),
        d.ForeignKeyConstraint(
            ['en_entity', 'pa_partner', 'oh_order'],
            ['order_hdr.en_entity', 'order_hdr.pa_partner',
             'order_hdr.oh_order']))

    entity = d.Column('en_entity', d.Text)
    partner_id = d.Column('pa_partner', d.Text)
    order_id = d.Column('oh_order', d.Text)
    store_loc = d.Column('os_store_loc', d.Text)

    status = d.Column('os_status', d.Text)
    sys_id = d.Column('os_sys_id', d.Integer)

    order_header = d.relationship('OrderHeader')

    def __init__(self, order_header, store_loc, status=None, sys_id=None):
        self.order_header = order_header
        self.store_loc = store_loc
        self.status = status
        self.sys_id = sys_id


class OrderSSCC(d.Model):
    __tablename__ = 'order_sscc'
    __table_args__ = (
        d.PrimaryKeyConstraint(
            'en_entity', 'pa_partner', 'oh_order', 'os_store_loc', 'oc_sscc'),
        d.ForeignKeyConstraint(
            ['en_entity', 'pa_partner', 'oh_order', 'os_store_loc'],
            ['order_str.en_entity', 'order_str.pa_partner',
             'order_str.oh_order', 'order_str.os_store_loc']))

    entity = d.Column('en_entity', d.Text)
    partner_id = d.Column('pa_partner', d.Text)
    order_id = d.Column('oh_order', d.Text)
    store_loc = d.Column('os_store_loc', d.Text)
    sscc_id = d.Column('oc_sscc', d.Text)

    date_closed = d.Column('oc_date_closed', d.Date)
    # Seconds after midnight.
    time_closed = d.Column('oc_time_closed', d.Integer)

    order_store = d.relationship('OrderStore')

    def __init__(self, order_store, sscc_id, date_closed=None,
                 time_closed=None):
        self.order_store = order_store
        self.sscc_id = sscc_id
        self.date_closed = date_closed
        self.time_closed = time_closed


class OrderLine(d.Model):
    __tablename__ = 'order_line'
    __table_args__ = (
        d.PrimaryKeyConstraint(
            'en_entity', 'pa_partner', 'oh_order', 'os_store_loc',
            'ol_line_seq'),
        d.ForeignKeyConstraint(
            ['en_entity', 'pa_partner', 'oh_order', 'os_store_loc'],
            ['order_str.en_entity', 'order_str.pa_partner',
             'order_str.oh_order', 'order_str.os_store_loc']))

    entity = d.Column('en_entity', d.Text)
    partner_id = d.Column('pa_partner', d.Text)
    order_id = d.Column('oh_order', d.Text)
    store_loc = d.Column('os_store_loc', d.Text)
    line_seq = d.Column('ol_line_seq', d.Integer)

    qty_picked = d.Column('ol_qty_picked', d.Integer)

    order_store = d.relationship('OrderStore')

    def __init__(self, order_store, line_seq, qty_picked=None):
        self.order_store = order_store
        self.line_seq = line_seq
        self.qty_picked = qty_picked
