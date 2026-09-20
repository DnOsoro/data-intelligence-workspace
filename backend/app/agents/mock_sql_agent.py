from app.agents.sql_agent import SQLAgent
from app.models.sql_agent import (
    SQLAgentRequest,
    SQLAgentResponse,
)


class MockSQLAgent(SQLAgent):
    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        if "customers" in request.schema_context.lower():
            return SQLAgentResponse(
                sql=(
                    "SELECT country, "
                    "SUM(lifetime_value) AS total_lifetime_value "
                    "FROM customers "
                    "GROUP BY country "
                    "ORDER BY total_lifetime_value DESC"
                ),
                explanation=(
                    "Aggregates customer lifetime value by country "
                    "and orders countries from highest to lowest."
                ),
            )

        return SQLAgentResponse(
            sql="",
            explanation="No authorized tables are available.",
        )