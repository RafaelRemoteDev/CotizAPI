from sqlalchemy import Engine

from db.models import Asset

if __name__ == '__main__':
    Asset.__table__.create(Engine)
