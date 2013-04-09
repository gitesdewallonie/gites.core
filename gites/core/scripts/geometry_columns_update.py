# -*- coding: utf-8 -*-
from sqlalchemy import and_

import geoalchemy
from gites.db import session as DBSession
from gites.db.content import (Hebergement,
                              InfoTouristique,
                              InfoPratique,
                              MaisonTourisme,
                              MapExternalData)
from gites.core.scripts.db import initializeDB
import gites.core.scripts

GROUPING_DISTANCE_METERS = 500


def main():
    initializeDB(gites.core.scripts)
    updateHebergement()
    updateInfoTour()
    updateInfoPrat()
    updateMaison()
    updateExtData()


def updateHebergement():
    session = DBSession()

    query = session.query(Hebergement)
    query = query.filter(and_(Hebergement.heb_gps_lat != None,
                              Hebergement.heb_gps_long != None))
    hebs = query.all()

    for heb in hebs:
        point = 'POINT(%s %s)' % (heb.heb_gps_long, heb.heb_gps_lat)
        point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        heb.heb_location = point

    session.commit()
    session.flush()


def updateInfoTour():
    session = DBSession()

    query = session.query(InfoTouristique)
    query = query.filter(and_(InfoTouristique.infotour_gps_lat != None,
                              InfoTouristique.infotour_gps_long != None))
    infoTours = query.all()

    for infoTour in infoTours:
        point = 'POINT(%s %s)' % (infoTour.infotour_gps_long, infoTour.infotour_gps_lat)
        point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        infoTour.infotour_location = point

    session.commit()
    session.flush()


def updateInfoPrat():
    session = DBSession()

    query = session.query(InfoPratique)
    query = query.filter(and_(InfoPratique.infoprat_gps_lat != None,
                              InfoPratique.infoprat_gps_long != None))
    infoPrats = query.all()

    for infoPrat in infoPrats:
        point = 'POINT(%s %s)' % (infoPrat.infoprat_gps_long, infoPrat.infoprat_gps_lat)
        point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        infoPrat.infoprat_location = point

    session.commit()
    session.flush()


def updateMaison():
    session = DBSession()

    query = session.query(MaisonTourisme)
    query = query.filter(and_(MaisonTourisme.mais_gps_lat != None,
                              MaisonTourisme.mais_gps_long != None))
    maisonTours = query.all()

    for maisonTour in maisonTours:
        point = 'POINT(%s %s)' % (maisonTour.mais_gps_long, maisonTour.mais_gps_lat)
        point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        maisonTour.mais_location = point

    session.commit()
    session.flush()


def updateExtData():
    session = DBSession()

    query = session.query(MapExternalData)
    query = query.filter(and_(MapExternalData.ext_data_latitude != None,
                              MapExternalData.ext_data_longitude != None))
    extDatas = query.all()

    for extData in extDatas:
        point = 'POINT(%s %s)' % (extData.ext_data_longitude, extData.ext_data_latitude)
        point = geoalchemy.base.WKTSpatialElement(point, srid=3447)
        extData.ext_data_location = point

    session.commit()
    session.flush()


if __name__ == "__main__":
    main()
