import datetime
from time import sleep
from typing import Iterator

import docker
import pytest
from docker.errors import APIError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app import get_total_net_calories
from db import Base
from models.exercise import Bike
from models.food import FoodConsumption

TEST_DB_DOCKERFILE_PATH = "./tests"


@pytest.fixture(scope="session")
def postgres_container():
    """start docker instance of postgres"""
    client = docker.from_env()

    client.images.build(
        path=TEST_DB_DOCKERFILE_PATH, tag="test_postgres", nocache=True
    )

    try:
        # create container
        db_container = client.containers.run(
            "test_postgres",
            name="test_db",
            detach=True,
            ports={5432: 5432},
        )

    except APIError:
        # docker api returns an error sincewe already have a container
        # remove existing container and make a new one
        db_container = client.containers.get("test_db")
        db_container.remove()  # type:ignore
        db_container = client.containers.run(
            "test_postgres",
            name="test_db",
            detach=True,
            ports={5432: 5432},
        )
    # return to calling function so we can use the container
    yield
    # calling function is done so we can stop and remove the container
    db_container.stop()  # type:ignore
    db_container.remove()  # type:ignore


@pytest.fixture
def test_session(postgres_container) -> Iterator[Session]:
    """create db session and cleanup data after each test"""
    # testing connection string
    DOCKER_USERNAME = "postgres"
    DOCKER_PASSWORD = "password"
    DOCKER_HOSTNAME = "localhost:5432"
    DOCKER_DB_NAME = "postgres"

    sql_url = (
        f"postgresql://{DOCKER_USERNAME}:{DOCKER_PASSWORD}@"
        f"{DOCKER_HOSTNAME}/{DOCKER_DB_NAME}"
    )
    engine = create_engine(sql_url, pool_pre_ping=True)

    # wait until db is ready
    MAX_RETRIES = 100
    #  max value for backoff time
    MAX_RETRY_SLEEP_SEC = 2

    num_retries = 0
    try:
        while num_retries < MAX_RETRIES:
            num_retries += 1
            # keep increasing back off time until MAX_RETRY_SLEEP_SEC
            # using (truncated) exponential backoff
            sleep_time_ms = min(
                [MAX_RETRY_SLEEP_SEC * 1000, 100 * num_retries]
            )
            try:
                # check if db is ready with simple query
                engine.execute("SELECT 1")
            except OperationalError:
                # db is still starting up, continue loop and retry
                sleep(sleep_time_ms / 1000)
                continue
            # db has started - lets break out of loop
            break
    except OperationalError:
        raise Exception("Couldn't connect to Test Postgres Docker Instance!")

    # create all tables registered to our declarative base class
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.commit()

    # clean up our db
    Base.metadata.drop_all(engine)


def test_get_net_calories(test_session: Session):
    food_cons = FoodConsumption(
        food_id="a", qty="100", date=datetime.date.today()
    )
    bike_session = Bike(
        date=datetime.date.today(), speed_mph=5, duration_min=20
    )
    with test_session:
        test_session.add_all([food_cons, bike_session])
        test_session.commit()

    result = get_total_net_calories(test_session)

    assert result == 980
