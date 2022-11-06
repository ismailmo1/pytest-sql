import datetime
from datetime import date, timedelta

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = Flask(__name__)
engine = create_engine("postgresql://postgres@localhost:5432")


def get_total_net_calories(
    session: Session,
    date_range: tuple[date, date] = (
        date.today(),
        date.today() + timedelta(days=1),
    ),
) -> float | None:
    start_date, end_date = date_range
    query = """
        WITH consumption AS (
            SELECT
                sum(fr."kcal/unit" * fc.qty) AS total_cons
            FROM
                public.food_cons fc
                JOIN public.food_ref fr ON fc.food_id = fr.id
            WHERE
                date BETWEEN :start_date  :: timestamp
                AND :end_date :: timestamp
        ),
        bike_exp AS (
            SELECT
                sum(b.duration_min) AS total_bike_exp
            FROM
                bike b
            WHERE
                date BETWEEN :start_date :: timestamp
                AND :end_date :: timestamp
        )
        SELECT
            (consumption.total_cons - bike_exp.total_bike_exp) AS net_kcal
        FROM
            bike_exp,
            consumption
        """
    with session:
        result: float | None = session.execute(  # type:ignore
            query,
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
        ).first()[0]
    if result:
        return round(result, 2)

    return


@app.get("/")
def index():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if start_date and end_date:
        calories = get_total_net_calories(
            Session(engine),
            tuple(
                datetime.datetime.fromisoformat(d)
                for d in [start_date, end_date]
            ),
        )
    else:
        calories = get_total_net_calories(Session(engine))
    return jsonify({"total_net_calories": calories})


if __name__ == "__main__":
    app.run()
