from database import Base
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    created_documents: Mapped[list["Document"]] = relationship("Document", foreign_keys="Document.created_by", back_populates="creator")
    modified_documents: Mapped[list["Document"]] = relationship("Document", foreign_keys="Document.last_modified_by", back_populates="last_modifier")
    owned_documents: Mapped[list["Document"]] = relationship("Document", secondary="document_owners", back_populates="owners")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")


class Document(Base):
    __tablename__ = "documents"
    
    document_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))
    last_modified_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))
    current_version_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], back_populates="created_documents")
    last_modifier: Mapped["User"] = relationship("User", foreign_keys=[last_modified_by], back_populates="modified_documents")
    owners: Mapped[list["User"]] = relationship("User", secondary="document_owners", back_populates="owned_documents")
    versions: Mapped[list["Version"]] = relationship("Version", back_populates="document")


class DocumentOwner(Base):
    __tablename__ = "document_owners"
    
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.document_id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)


class Version(Base):
    __tablename__ = "versions"
    
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.document_id", ondelete="CASCADE"), primary_key=True)
    version_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    mongo_id: Mapped[str] = mapped_column(String(24), nullable=False)
    modified_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("version_number >= 0", name="check_version_nonnegative"),
    )
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    modifier: Mapped["User"] = relationship("User")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    token_hex: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
