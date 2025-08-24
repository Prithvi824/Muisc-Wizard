"""
This module contains the database models for the project.
"""

# 1st party imports
from typing import List, Optional, Type

# 3rd party imports
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import (
    Session,
    declarative_base,
    mapped_column,
    Mapped,
    relationship,
)

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
    fingerprints: Mapped[List["SongFingerPrints"]] = relationship(
        back_populates="song", cascade="all, delete-orphan"
    )

    @classmethod
    def get_song_from_video_id(
        cls: Type["Song"], session: Session, video_id: str
    ) -> Optional["Song"]:
        """Get a song from the database based on the video id.

        Args:
            cls (Type["Song"]: The class type of the Song model.
            session (Session): The database session.
            video_id (str): The video id of the song.

        Returns:
            Optional["Song"]: The song object if found, otherwise None.
        """

        return session.query(cls).filter(cls.yt_url.contains(video_id)).first()

    @classmethod
    def get_all_songs(
        cls: Type["Song"], session: Session, offset: int = 0, limit: int = 10
    ) -> List["Song"]:
        """Get all songs from the database.

        Args:
            cls (Type["Song"]: The class type of the Song model.
            session (Session): The database session.

        Returns:
            List["Song"]: A list of all songs in the database.
        """

        # get all songs from the database with pagination
        return session.query(cls).offset(offset).limit(limit).all()


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
