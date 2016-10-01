from datetime import datetime

from flask import request
from flask_restful import Resource

from custboard import api
from custboard.db import interface


class Partners(Resource):
    def get(self):
        return interface.get_partners()


class Data(Resource):
    def get(self, partner_id):
        interval = int(request.args.get('interval', str(60 * 15)))
        return {
            'released': interface.get_released(partner_id),
            'packed': interface.get_packed(partner_id),
            'openToday': interface.get_today(partner_id),
            'openOld': interface.get_old(partner_id),
            'chartData': interface.get_conversion_history(partner_id, interval),
            'conversion':
                interface.get_conversion_current(partner_id, interval),
            }


api.add_resource(Partners, '/partners')
api.add_resource(Data, '/partners/<partner_id>/data')
