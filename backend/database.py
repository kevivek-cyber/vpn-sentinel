import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
DATABASE_URL = "sqlite:///./vpn_sentinel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class FlowInferenceLog(Base):
    __tablename__ = "flow_inference_logs"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    duration = Column(Float)
    fwd_pkt_len_mean = Column(Float)
    bwd_pkt_len_mean = Column(Float)
    flow_iat_mean = Column(Float)
    flow_iat_std = Column(Float)
    packets_per_sec = Column(Float)
    bytes_per_sec = Column(Float)
    is_vpn = Column(Boolean)
    vpn_protocol = Column(String, nullable=True)
    confidence = Column(Float)
    explanation = Column(String)
    webrtc_ip_mismatch = Column(Integer, nullable=True)
    webrtc_blocked = Column(Integer, nullable=True)
    timezone_mismatch_score = Column(Integer, nullable=True)
    language_mismatch_score = Column(Integer, nullable=True)
    geo_ip_distance_km = Column(Float, nullable=True)
    has_geo_permission = Column(Integer, nullable=True)
    is_datacenter_ip = Column(Integer, nullable=True)
    is_known_vpn_ip = Column(Integer, nullable=True)
    proxy_header_detected = Column(Integer, nullable=True)
def init_db():
    Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
