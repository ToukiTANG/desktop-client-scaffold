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
