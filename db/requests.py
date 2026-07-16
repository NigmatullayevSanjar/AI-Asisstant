from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import selectinload

from db.database import async_session
from db.models import Task, TaskStatus, Team, User

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


async def get_or_create_user(
    tg_id: int, full_name: str, username: str | None, is_admin: bool = False
) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if user:
            return user
        user = User(tg_id=tg_id, full_name=full_name, username=username, is_admin=is_admin)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_user_by_tg_id(tg_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


async def create_user(
    tg_id: int, full_name: str, username: str | None, team_id: int | None = None
) -> User:
    async with async_session() as session:
        user = User(tg_id=tg_id, full_name=full_name, username=username, team_id=team_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_all_users() -> Sequence[User]:
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.id))
        return result.scalars().all()


async def set_user_team(user_id: int, team_id: int) -> None:
    async with async_session() as session:
        await session.execute(update(User).where(User.id == user_id).values(team_id=team_id))
        await session.commit()


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------


async def create_team(name: str) -> Team:
    async with async_session() as session:
        team = Team(name=name)
        session.add(team)
        await session.commit()
        await session.refresh(team)
        return team


async def get_all_teams() -> Sequence[Team]:
    async with async_session() as session:
        result = await session.execute(select(Team).order_by(Team.id))
        return result.scalars().all()


async def get_team_by_id(team_id: int) -> Optional[Team]:
    async with async_session() as session:
        result = await session.execute(select(Team).where(Team.id == team_id))
        return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


async def create_task(
    title: str,
    description: str | None,
    created_by: int | None,
    assigned_to: int | None = None,
    team_id: int | None = None,
    deadline: datetime | None = None,
) -> Task:
    async with async_session() as session:
        task = Task(
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to,
            team_id=team_id,
            deadline=deadline,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


async def get_task_by_id(task_id: int) -> Optional[Task]:
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()


async def get_all_tasks() -> Sequence[Task]:
    async with async_session() as session:
        result = await session.execute(select(Task).order_by(Task.created_at.desc()))
        return result.scalars().all()


async def get_tasks_by_user(user_id: int) -> Sequence[Task]:
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.assigned_to == user_id).order_by(Task.created_at.desc())
        )
        return result.scalars().all()


async def get_team_tasks(team_id: int, exclude_user_id: int | None = None) -> Sequence[Task]:
    """Tasks assigned to members of the given team (based on the assignee's team_id),
    with the assignee eagerly loaded so it's safe to read after the session closes."""
    async with async_session() as session:
        stmt = (
            select(Task)
            .join(User, Task.assigned_to == User.id)
            .where(User.team_id == team_id)
            .options(selectinload(Task.assignee))
            .order_by(Task.created_at.desc())
        )
        if exclude_user_id is not None:
            stmt = stmt.where(Task.assigned_to != exclude_user_id)
        result = await session.execute(stmt)
        return result.scalars().all()


async def assign_task(task_id: int, user_id: int) -> None:
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(assigned_to=user_id))
        await session.commit()


async def edit_task(task_id: int, **fields) -> None:
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(**fields))
        await session.commit()


async def delete_task(task_id: int) -> None:
    async with async_session() as session:
        await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()


async def update_task_status(task_id: int, status: TaskStatus) -> None:
    async with async_session() as session:
        await session.execute(update(Task).where(Task.id == task_id).values(status=status))
        await session.commit()


async def get_statistics() -> dict:
    async with async_session() as session:
        total = await session.scalar(select(func.count(Task.id)))
        new_count = await session.scalar(
            select(func.count(Task.id)).where(Task.status == TaskStatus.NEW)
        )
        in_progress = await session.scalar(
            select(func.count(Task.id)).where(Task.status == TaskStatus.IN_PROGRESS)
        )
        done = await session.scalar(
            select(func.count(Task.id)).where(Task.status == TaskStatus.DONE)
        )
        users_count = await session.scalar(select(func.count(User.id)))
        teams_count = await session.scalar(select(func.count(Team.id)))
        return {
            "total_tasks": total or 0,
            "new": new_count or 0,
            "in_progress": in_progress or 0,
            "done": done or 0,
            "users": users_count or 0,
            "teams": teams_count or 0,
        }
