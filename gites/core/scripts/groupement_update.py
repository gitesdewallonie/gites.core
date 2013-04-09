# -*- coding: utf-8 -*-
from sqlalchemy import and_, not_

from gites.db import session as DBSession
from gites.db.content import Hebergement
from gites.core.scripts.db import initializeDB
import gites.core.scripts

GROUPING_DISTANCE_METERS = 500


def main():
    # XXXnext en gros faire comme dans gites.db la migration pour update les
    # groupements
    initializeDB(gites.core.scripts)
    updateGroupementColumn()


def updateGroupementColumn():
    session = DBSession()
    hebs = session.query(Hebergement).order_by(Hebergement.heb_pro_fk, Hebergement.heb_cgt_cap_max.desc())

    groupementPk = 1
    proprioGroupedHebsPk = []
    actualProprio = None

    for heb in hebs:
        #Change proprio
        if actualProprio != heb.heb_pro_fk:
            proprioGroupedHebsPk = []
        actualProprio = heb.heb_pro_fk

        if heb.heb_pk not in proprioGroupedHebsPk:

            groupedHebs = getGroupedHebs(heb, proprioGroupedHebsPk, session)
            if groupedHebs:
                #add this one to the list to update
                groupedHebs.append(heb)

                setGroupementPk(groupedHebs, groupementPk)
                proprioGroupedHebsPk.extend([obj.heb_pk for obj in groupedHebs])
                groupementPk += 1
            else:
                emptyGroupementPk(heb)
    session.commit()
    session.flush()


def getGroupedHebs(heb, groupedHebsPk, session):
    """
    get all hebs near heb from the same proprio
    Exclude groupedHebsPk (already grouped)
    """
    query = session.query(Hebergement)
    query = query.filter(and_(Hebergement.heb_location.distance_sphere(heb.heb_location) < GROUPING_DISTANCE_METERS,
                              Hebergement.heb_pro_fk == heb.heb_pro_fk,
                              Hebergement.heb_pk != heb.heb_pk,
                              not_(Hebergement.heb_pk.in_(groupedHebsPk))))
    return query.all()


def setGroupementPk(hebs, groupementPk):
    """
    fill heb_groupement_pk for hebs by heb_pk
    """
    for heb in hebs:
        heb.heb_groupement_pk = groupementPk
        heb.update()


def emptyGroupementPk(heb):
    """
    empty heb_groupement_pk column of heb
    """
    heb.heb_groupement_pk = None
    heb.update()


if __name__ == "__main__":
    main()
