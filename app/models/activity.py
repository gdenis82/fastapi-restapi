from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.base import Base


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (CheckConstraint("depth BETWEEN 1 AND 3", name="ck_activities_depth"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id"), nullable=True, index=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent", cascade="all, delete-orphan")
    organizations = relationship("Organization", secondary="organization_activity", back_populates="activities")

    @validates("parent")
    def _validate_parent(self, _key, parent):
        if parent is None:
            return parent
        if parent.depth >= 3:
            raise ValueError("Activity nesting depth cannot exceed 3")
        # Глубина ребенка на один уровень ниже глубины родителя.
        self.depth = parent.depth + 1
        return parent
