import sqlalchemy as sa


metadata = sa.MetaData()


person_table = sa.Table(
    "person",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("department", sa.Text, nullable=False),
    sa.Column("job_title", sa.Text, nullable=False),
    sa.Column("identity", sa.Integer, nullable=False),
    sa.Column("specialize_classify", sa.Integer, nullable=False),
    sa.Column("education", sa.Text, nullable=True),
    sa.Column("gender", sa.Integer, nullable=False),
    sa.Column("production_group_classify", sa.Integer, nullable=True),
    sa.Column("created_at", sa.Text, nullable=False),
    sa.Column("updated_at", sa.Text, nullable=False),
)


sa.Index("idx_person_name", person_table.c.name)

sa.Index("idx_person_department", person_table.c.department)

sa.Index("idx_person_identity", person_table.c.identity)

sa.Index("idx_person_specialize_classify", person_table.c.specialize_classify)

check_problem_table = sa.Table(
    "check_problem",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("status", sa.Integer, nullable=False),
    sa.Column("decomposed", sa.Integer, nullable=False),
    sa.Column("revised", sa.Integer, nullable=False),
    sa.Column("assessed", sa.Integer, nullable=False),
    sa.Column("check_department", sa.String(255), nullable=False),
    sa.Column("check_person", sa.String(255), nullable=False),
    sa.Column("check_type", sa.Integer, nullable=False),
    sa.Column("check_way", sa.Integer, nullable=False),
    sa.Column("check_start_time", sa.DateTime, nullable=False),
    sa.Column("check_end_time", sa.DateTime, nullable=False),
    sa.Column("submit_time", sa.DateTime, nullable=False),
    sa.Column("problem_item", sa.String(255), nullable=False),
    sa.Column("consequences", sa.String(255), nullable=False),
    sa.Column("risk_type", sa.String(255), nullable=False),
    sa.Column("risk_level", sa.Integer, nullable=False),
    sa.Column("problem_classify", sa.Integer, nullable=False),
    sa.Column("problem_label", sa.Integer, nullable=False),
    sa.Column("problem_extra_points", sa.String(50), nullable=False),
    sa.Column("problem_type", sa.String(255), nullable=False),
    sa.Column("red_line", sa.Integer, nullable=False),
    sa.Column("problem_position", sa.String(255), nullable=False),
    sa.Column("implement_department", sa.String(255), nullable=False),
    sa.Column("duty_department", sa.String(255), nullable=False),
    sa.Column("other_classify", sa.String(255), nullable=False),
    sa.Column("cross_unit", sa.Integer, nullable=False),
    sa.Column("business_guidance", sa.Integer, nullable=False),
    sa.Column("outside", sa.Integer, nullable=False),
    sa.Column("problem_description", sa.String(255), nullable=False),
    sa.Column("deadline", sa.Date, nullable=False),
    sa.Column("rectification_requirements", sa.String(255), nullable=True),
    sa.Column("rectification_person", sa.String(50), nullable=True),
    sa.Column("rectification_time", sa.DateTime, nullable=True),
    sa.Column("rectification_description", sa.String(255), nullable=True),
    sa.Column("responsible_person", sa.String(255), nullable=True),
    sa.Column("reason", sa.String(255), nullable=True),
    sa.Column("close_issue_person", sa.String(50), nullable=True),
    sa.Column("close_issue_evaluate", sa.String(255), nullable=True),
    sa.Column("close_issue_time", sa.DateTime, nullable=True),
)
