import datetime
from datetime import date, timedelta

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = Flask(__name__)
engine = create_engine("postgresql://postgres@localhost:5432")


def get_net_calorie_stats(
    date_range: tuple[date, date] = (
        date.today(),
        date.today() + timedelta(days=1),
    )
) -> float:
    start_date, end_date = date_range
    query = """
            select
                sum(fr."kcal/unit" * fc.qty)
            from
                public.food_cons fc
            join public.food_ref fr on
                fc.food_id = fr.id
            where
                date between :start_date ::timestamp and :end_date ::timestamp
        """
    with Session(engine) as session:
        result: float = session.execute(  # type:ignore
            query,
            {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
        ).first()[0]
    return round(result, 2)


@app.get("/")
def index():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if start_date and end_date:
        calories = get_net_calorie_stats(
            tuple(
                datetime.datetime.fromisoformat(d)
                for d in [start_date, end_date]
            )
        )
    else:
        calories = get_net_calorie_stats()
    return jsonify({"net_calories": calories})


if __name__ == "__main__":
    app.run()
