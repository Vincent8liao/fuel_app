from database.db import query_total

def handle_query(question):
    q = question.lower()

    if "total" in q:
        result = query_total()
        return f"Total fuel cost: {round(result,2)} EUR"

    return "Query not supported"