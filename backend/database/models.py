"""
This module contains the database models for the project.
"""

# 1st party imports
from typing import List

# 3rd party imports
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship

# create a base class for the models
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Song(Base):
    """This class represents a song table in the database."""

    # Table arguments
    __tablename__ = "songs"

    # Required fields
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    yt_url: Mapped[str] = mapped_column(nullable=False, unique=True)

    # Optional fields
    thumbnail: Mapped[str] = mapped_column(nullable=False)
    artist: Mapped[str] = mapped_column(nullable=True)

    # fingerprints
    fingerprints: Mapped[List["SongFingerPrints"]] = relationship(back_populates="song", cascade="all, delete-orphan")


class SongFingerPrints(Base):
    """This class represents a song fingerprints table in the database."""

    # Table arguments
    __tablename__ = "song_fingerprints"

    # Required fields
    id: Mapped[int] = mapped_column(primary_key=True)
    fingerprint_index: Mapped[int] = mapped_column(nullable=False, index=True)
    fingerprint_hash: Mapped[int] = mapped_column(nullable=False, index=True)

    # Relationship fields
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))
    song: Mapped["Song"] = relationship(back_populates="fingerprints")
