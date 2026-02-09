"""create tables

Revision ID: 0001_create_tables
Revises: 
Create Date: 2026-02-10 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("depth BETWEEN 1 AND 3", name="ck_activities_depth"),
        sa.ForeignKeyConstraint(["parent_id"], ["activities.id"]),
    )
    op.create_index(op.f("ix_activities_name"), "activities", ["name"], unique=False)
    op.create_index(op.f("ix_activities_parent_id"), "activities", ["parent_id"], unique=False)

    op.create_table(
        "buildings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
    )
    op.create_index(op.f("ix_organizations_building_id"), "organizations", ["building_id"], unique=False)
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"], unique=False)

    op.create_table(
        "phones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.String(length=32), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_phones_organization_id"), "phones", ["organization_id"], unique=False)

    op.create_table(
        "organization_activity",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("organization_id", "activity_id"),
    )


def downgrade() -> None:
    op.drop_table("organization_activity")
    op.drop_index(op.f("ix_phones_organization_id"), table_name="phones")
    op.drop_table("phones")
    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_building_id"), table_name="organizations")
    op.drop_table("organizations")
    op.drop_table("buildings")
    op.drop_index(op.f("ix_activities_parent_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_name"), table_name="activities")
    op.drop_table("activities")