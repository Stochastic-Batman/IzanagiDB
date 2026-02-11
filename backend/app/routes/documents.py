import jsonpatch
import logging

from bson import ObjectId
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db, document_contents
from dependencies import get_current_user
from schemas import DocumentCreate, DocumentCommit, DocumentResponse, VersionResponse
from tables import User, Document, DocumentOwner, Version


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(doc_data: DocumentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a new document with initial content."""
    
    # Store content in MongoDB as snapshot
    mongo_doc = {
        "type": "snapshot",
        "content": doc_data.content
    }
    result = await document_contents.insert_one(mongo_doc)
    mongo_id = str(result.inserted_id)
    
    # Create document metadata in PostgreSQL
    new_doc = Document(
        title=doc_data.title,
        created_by=current_user.user_id,
        last_modified_by=current_user.user_id,
        current_version_number=0
    )
    db.add(new_doc)
    await db.flush()  # Get document_id without committing
    
    # Create initial version
    version = Version(
        document_id=new_doc.document_id,
        version_number=0,
        mongo_id=mongo_id,
        modified_by=current_user.user_id
    )
    db.add(version)
    
    # Add user as owner
    owner = DocumentOwner(
        document_id=new_doc.document_id,
        user_id=current_user.user_id
    )
    db.add(owner)
    
    await db.commit()
    await db.refresh(new_doc)
    
    logger.info(f"Document created: {new_doc.document_id} by user {current_user.user_id}")
    
    # Return document with content
    response = DocumentResponse.model_validate(new_doc)
    response.content = doc_data.content
    return response


@router.get("", response_model=list[DocumentResponse])
async def list_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List all documents owned by current user."""
    
    # Get documents where user is owner
    result = await db.execute(
        select(Document)
        .join(DocumentOwner)
        .where(DocumentOwner.user_id == current_user.user_id)
    )
    documents = result.scalars().all()
    
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get a document with its latest content."""
    
    # Check if user owns the document
    result = await db.execute(
        select(DocumentOwner)
        .where(
            DocumentOwner.document_id == document_id,
            DocumentOwner.user_id == current_user.user_id
        )
    )

    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get document metadata
    result = await db.execute(select(Document).where(Document.document_id == document_id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get latest version
    if doc.current_version_number is not None:
        result = await db.execute(
            select(Version).where(
                Version.document_id == document_id,
                Version.version_number == doc.current_version_number
            )
        )
        version = result.scalar_one_or_none()
        
        if version:
            # Fetch content from MongoDB
            mongo_doc = await document_contents.find_one({"_id": ObjectId(version.mongo_id)})
            content = mongo_doc.get("content") if mongo_doc else None
        else:
            content = None
    else:
        content = None
    
    response = DocumentResponse.model_validate(doc)
    response.content = content
    return response


@router.post("/{document_id}/commit", response_model=VersionResponse)
async def commit_version(document_id: int, commit_data: DocumentCommit, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a new version by committing changes."""
    
    # Check ownership
    result = await db.execute(
        select(DocumentOwner)
        .where(
            DocumentOwner.document_id == document_id,
            DocumentOwner.user_id == current_user.user_id
        )
    )

    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get document
    result = await db.execute(select(Document).where(Document.document_id == document_id))
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get current version
    if doc.current_version_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no versions"
        )
    
    result = await db.execute(
        select(Version).where(
            Version.document_id == document_id,
            Version.version_number == doc.current_version_number
        )
    )
    
    current_version = result.scalar_one_or_none()
    
    # Fetch current content from MongoDB
    old_mongo_doc = await document_contents.find_one({"_id": ObjectId(current_version.mongo_id)})
    old_content = old_mongo_doc.get("content")
    
    # Calculate delta (patch from new to old)
    reverse_patch = jsonpatch.make_patch(commit_data.content, old_content)
    
    # Update old version to store reverse delta instead of snapshot
    await document_contents.update_one(
        {"_id": ObjectId(current_version.mongo_id)},
        {"$set": {
            "type": "delta",
            "patch": reverse_patch.patch
        }}
    )
    
    # Store new version as snapshot
    new_mongo_doc = {
        "type": "snapshot",
        "content": commit_data.content
    }
    result = await document_contents.insert_one(new_mongo_doc)
    new_mongo_id = str(result.inserted_id)
    
    # Create new version in PostgreSQL
    new_version_number = doc.current_version_number + 1
    new_version = Version(
        document_id=document_id,
        version_number=new_version_number,
        mongo_id=new_mongo_id,
        modified_by=current_user.user_id
    )
    db.add(new_version)
    
    # Update document metadata
    doc.current_version_number = new_version_number
    doc.last_modified_by = current_user.user_id
    doc.last_modified_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(new_version)
    
    logger.info(f"New version {new_version_number} committed for document {document_id}")
    return VersionResponse.model_validate(new_version)


@router.get("/{document_id}/versions", response_model=list[VersionResponse])
async def list_versions(document_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get version history for a document."""
    
    # Check ownership
    result = await db.execute(
        select(DocumentOwner)
        .where(
            DocumentOwner.document_id == document_id,
            DocumentOwner.user_id == current_user.user_id
        )
    )

    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get all versions
    result = await db.execute(
        select(Version)
        .where(Version.document_id == document_id)
        .order_by(Version.version_number.desc())
    )

    versions = result.scalars().all()
    
    return [VersionResponse.model_validate(v) for v in versions]


@router.get("/{document_id}/versions/{version_number}")
async def get_version(document_id: int, version_number: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get specific version content (reconstructs from deltas if needed)."""
    
    # Check ownership
    result = await db.execute(
        select(DocumentOwner)
        .where(DocumentOwner.document_id == document_id, DocumentOwner.user_id == current_user.user_id)
    )

    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get requested version
    result = await db.execute(select(Version).where(Version.document_id == document_id, Version.version_number == version_number))
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Fetch from MongoDB
    mongo_doc = await document_contents.find_one({"_id": ObjectId(version.mongo_id)})
    
    if mongo_doc.get("type") == "snapshot":
        # Latest version - return directly
        content = mongo_doc.get("content")
    else:
        # Old version with reverse delta - apply to current snapshot
        # Get all versions from this one to current
        result = await db.execute(
            select(Document).where(Document.document_id == document_id)
        )
        doc = result.scalar_one_or_none()

        result = await db.execute(
            select(Version).where(
                Version.document_id == document_id,
                Version.version_number == doc.current_version_number
            )
        )
        current_version = result.scalar_one_or_none()
        
        # Get current snapshot
        current_mongo = await document_contents.find_one({"_id": ObjectId(current_version.mongo_id)})
        current_content = current_mongo.get("content")
        
        # Apply reverse patch to reconstruct old version
        reverse_patch = jsonpatch.JsonPatch(mongo_doc.get("patch"))
        content = reverse_patch.apply(current_content)
        
    return {
        "document_id": document_id,
        "version_number": version_number,
        "content": content,
        "modified_at": version.modified_at
    }
