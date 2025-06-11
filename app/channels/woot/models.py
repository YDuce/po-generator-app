from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.extensions import db

class WootPorfStatus(str,Enum): DRAFT='draft'; PENDING='pending'; APPROVED='approved'

class WootPorf(db.Model):
    __tablename__='woot_porfs'
    id=Column(Integer,primary_key=True)
    porf_no=Column(String,unique=True,nullable=False)
    status=Column(SQLEnum(WootPorfStatus),nullable=False,default=WootPorfStatus.DRAFT)
    created_at=Column(DateTime,default=datetime.utcnow)
    lines=relationship('WootPorfLine',back_populates='porf')
    def to_dict(self): return {'id':self.id,'porf_no':self.porf_no,'status':self.status,'lines':[l.to_dict() for l in self.lines]}

class WootPorfLine(db.Model):
    __tablename__='woot_porf_lines'
    id=Column(Integer,primary_key=True)
    porf_id=Column(Integer,ForeignKey('woot_porfs.id'),nullable=False)
    product_id=Column(String,nullable=False);
    quantity=Column(Integer,nullable=False)
    porf=relationship('WootPorf',back_populates='lines')
    def to_dict(self): return {'id':self.id,'product_id':self.product_id,'quantity':self.quantity}
