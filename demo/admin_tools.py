from csv import DictReader


def import_model(*, session, model, filename):
    """Takes a session, model, and csv filename and imports the
    model into the session and commits. csv field names must exactly match the
    SQLAlchemy model's constructor and commits them to the session"""
    with open(filename) as fp:
        reader = DictReader(fp)
        for row in reader:
            well = model(**row)
            session.add(well)
        session.commit()