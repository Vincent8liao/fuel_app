from database.models import (
    get_total_cost,
    get_all_records,
    get_monthly_cost,
    get_cost_by_station
)

def query_total(filters=None):
    return {"total": get_total_cost(filters)}

def query_all(filters=None):
    return get_all_records(filters)

def query_monthly(filters=None):
    return get_monthly_cost(filters)

def query_by_station():
    return get_cost_by_station()
