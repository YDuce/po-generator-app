"""Woot channel models."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, JSON, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
from typing import Dict, List, Optional, Any

from app.extensions import db
from app.channels.base import ChannelModel
from app.core.models.base import BaseModel

class WootPorfStatus(str, Enum):
    """Woot PORF status enum."""
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

class WootPoStatus(str, Enum):
    """Woot PO status enum."""
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

class PORF(BaseModel):
    """Purchase Order Request Form model."""
    __tablename__ = 'woot_porfs'
    
    status = Column(String(50), nullable=False, default='draft')
    warehouse_id = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    lines = relationship('PORFLine', back_populates='porf', cascade='all, delete-orphan')
    
    def to_dict(self) -> dict:
        """Convert PORF to dictionary."""
        data = super().to_dict()
        data['lines'] = [line.to_dict() for line in self.lines]
        return data

class PORFLine(BaseModel):
    """Purchase Order Request Form Line model."""
    __tablename__ = 'woot_porf_lines'
    
    porf_id = Column(Integer, ForeignKey('woot_porfs.id'), nullable=False)
    product_id = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    porf = relationship('PORF', back_populates='lines')
    
    def to_dict(self) -> dict:
        """Convert PORFLine to dictionary."""
        return super().to_dict()

class PO(BaseModel):
    """Purchase Order model."""
    __tablename__ = 'woot_pos'
    
    porf_id = Column(Integer, ForeignKey('woot_porfs.id'), nullable=False)
    status = Column(String(50), nullable=False, default='draft')
    warehouse_id = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    porf = relationship('PORF')
    lines = relationship('POLine', back_populates='po', cascade='all, delete-orphan')
    
    def to_dict(self) -> dict:
        """Convert PO to dictionary."""
        data = super().to_dict()
        data['lines'] = [line.to_dict() for line in self.lines]
        return data

class POLine(BaseModel):
    """Purchase Order Line model."""
    __tablename__ = 'woot_po_lines'
    
    po_id = Column(Integer, ForeignKey('woot_pos.id'), nullable=False)
    porf_line_id = Column(Integer, ForeignKey('woot_porf_lines.id'), nullable=False)
    product_id = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    po = relationship('PO', back_populates='lines')
    porf_line = relationship('PORFLine')
    
    def to_dict(self) -> dict:
        """Convert POLine to dictionary."""
        return super().to_dict()

class WootPorf(db.Model, ChannelModel):
    """Woot PORF model."""
    __tablename__ = 'woot_porfs'
    
    id = Column(Integer, primary_key=True)
    porf_no = Column(String(50), unique=True, nullable=False)
    status = Column(SQLEnum(WootPorfStatus), nullable=False, default=WootPorfStatus.DRAFT)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_value = Column(Numeric(10, 2), nullable=False, default=0)
    extra_data = Column(JSON)
    
    # Google Drive/Sheets integration
    drive_folder_id = Column(String(100))
    sheets_file_id = Column(String(100))
    
    # Relationships
    pos = relationship('WootPo', back_populates='porf', cascade='all, delete-orphan')
    lines = relationship('WootPorfLine', back_populates='porf', cascade='all, delete-orphan')
    
    def get_channel_name(self) -> str:
        """Get the channel name."""
        return 'woot'
    
    def get_status_enum(self) -> type:
        """Get the status enum class."""
        return WootPorfStatus

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'porf_no': self.porf_no,
            'status': self.status,
            'total_value': float(self.total_value),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'sheets_file_id': self.sheets_file_id,
            'lines': [line.to_dict() for line in self.lines]
        }

class WootPo(db.Model, ChannelModel):
    """Woot PO model."""
    __tablename__ = 'woot_pos'
    
    id = Column(Integer, primary_key=True)
    po_no = Column(String(50), unique=True, nullable=False)
    porf_id = Column(Integer, ForeignKey('woot_porfs.id'), nullable=False)
    status = Column(SQLEnum(WootPoStatus), nullable=False, default=WootPoStatus.DRAFT)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    ship_by = Column(DateTime)
    total_ordered = Column(Numeric(10, 2), nullable=False, default=0)
    extra_data = Column(JSON)
    
    # Google Drive integration
    drive_file_id = Column(String(100))
    
    # Relationships
    porf = relationship('WootPorf', back_populates='pos')
    lines = relationship('WootPoLine', back_populates='po', cascade='all, delete-orphan')
    
    def get_channel_name(self) -> str:
        """Get the channel name."""
        return 'woot'
    
    def get_status_enum(self) -> type:
        """Get the status enum class."""
        return WootPoStatus

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'po_no': self.po_no,
            'porf_id': self.porf_id,
            'status': self.status,
            'total_ordered': float(self.total_ordered),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'ship_by': self.ship_by.isoformat() if self.ship_by else None,
            'drive_file_id': self.drive_file_id,
            'drive_folder_id': self.drive_folder_id,
            'lines': [line.to_dict() for line in self.lines]
        }

class WootPorfLine(db.Model):
    """Woot PORF line model."""
    __tablename__ = 'woot_porf_lines'
    
    id = Column(Integer, primary_key=True)
    porf_id = Column(Integer, ForeignKey('woot_porfs.id'), nullable=False)
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    extra_data = Column(JSON)
    
    # Relationships
    porf = relationship('WootPorf', back_populates='lines')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }

class WootPoLine(db.Model):
    """Woot PO line model."""
    __tablename__ = 'woot_po_lines'
    
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey('woot_pos.id'), nullable=False)
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    extra_data = Column(JSON)
    
    # Relationships
    po = relationship('WootPo', back_populates='lines')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        } 