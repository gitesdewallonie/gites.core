# -*- coding: utf-8 -*-


class TarifTableMixin(object):
    """
    """

    def get_tarif_table(self, section=None):
        """
        Return render of tarif table
        """
        return NotImplementedError

    def get_week_tarif_table(self):
        return self.get_tarif_table('WEEK')

    def get_weekend_tarif_table(self):
        return self.get_tarif_table('WEEKEND')

    def get_feast_weekend_tarif_table(self):
        return self.get_tarif_table('FEAST_WEEKEND')

    def get_season_tarif_table(self):
        return self.get_tarif_table('SEASON')

    def get_room_tarif_table(self):
        return self.get_tarif_table('ROOM')

    def get_christmas_tarif_table(self):
        return self.get_tarif_table('CHRISTMAS')

    def get_charges_tarif_table(self):
        return self.get_tarif_table('CHARGES')

    def get_other_tarif_table(self):
        return self.get_tarif_table('OTHER')
