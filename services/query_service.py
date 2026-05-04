from database.models import (
    get_total_cost,
    get_all_records,
    get_monthly_cost,
    get_cost_by_station
)

def query_total():
    return {"total": get_total_cost()}

def query_all():
    return get_all_records()

def query_monthly():
    return get_monthly_cost()

def query_by_station():
    return get_cost_by_station()()