from pathlib import Path

path = Path("validation/rules/validate_database.py")
content = path.read_text(encoding="utf-8")

start_marker = "    def validate_route_shape_consistency(self, connection):"
end_marker = "    # ============================================================\n    # R021"

start = content.index(start_marker)
end = content.index(end_marker, start)

new_method = '''    def validate_route_shape_consistency(self, connection):

        inconsistent = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips t
                JOIN (
                    SELECT route_id, shape_id, COUNT(*) AS shape_count
                    FROM trips
                    WHERE route_id IS NOT NULL
                      AND shape_id IS NOT NULL
                    GROUP BY route_id, shape_id
                ) rs
                    ON t.route_id = rs.route_id
                   AND t.shape_id = rs.shape_id
                JOIN (
                    SELECT route_id, MAX(shape_count) AS dominant_count
                    FROM (
                        SELECT route_id, shape_id, COUNT(*) AS shape_count
                        FROM trips
                        WHERE route_id IS NOT NULL
                          AND shape_id IS NOT NULL
                        GROUP BY route_id, shape_id
                    ) counts
                    GROUP BY route_id
                ) dominant
                    ON rs.route_id = dominant.route_id
                WHERE rs.shape_count < dominant.dominant_count
            """)
        ).scalar_one()

        if inconsistent > 0:
            self.add_issue(
                "R020",
                "MEDIUM",
                "ROUTE_SHAPE",
                "Trip references a shape inconsistent with the dominant shape pattern of its route.",
                {
                    "affected_records": inconsistent,
                },
            )

'''

content = content[:start] + new_method + content[end:]
path.write_text(content, encoding="utf-8")

print("R020 method replaced successfully.")
