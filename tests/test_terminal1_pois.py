from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.db.models import Poi
from app.db.seed.data import get_legacy_seed_pois, get_seed_terminal1_pois
from app.db.seed.seeder import seed_database


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    return engine, session


def test_terminal1_day_zero_inventory_matches_map():
    pois = get_seed_terminal1_pois()

    assert len(pois) == 94
    assert len({poi["id"] for poi in pois}) == 94
    assert {poi["map_section"] for poi in pois} == {"checkin", "departure", "piers"}
    assert all(poi["map_source"] == "terminal1-3d-day-zero" for poi in pois)
    assert all(poi["map_x"] is not None and poi["map_z"] is not None for poi in pois)
    assert all(poi["approach_x"] is not None and poi["approach_z"] is not None for poi in pois)


def test_terminal1_seed_archives_legacy_defaults_and_preserves_admin_edits():
    _, session = make_session()
    legacy = get_legacy_seed_pois()[0]
    session.add(Poi(**legacy))
    session.commit()

    seed_database(session=session)
    archived = session.query(Poi).filter(Poi.id == legacy["id"]).one()
    assert archived.is_active is False

    baseline = session.query(Poi).filter(Poi.id == "checkin-retail-1").one()
    baseline.name = "Admin Updated Neo Travel"
    session.commit()

    seed_database(session=session)
    session.expire_all()
    preserved = session.query(Poi).filter(Poi.id == "checkin-retail-1").one()
    assert preserved.name == "Admin Updated Neo Travel"

    active_terminal1 = session.query(Poi).filter(
        Poi.map_source == "terminal1-3d-day-zero",
        Poi.is_active.is_(True),
    ).count()
    assert active_terminal1 == 94

    session.close()
