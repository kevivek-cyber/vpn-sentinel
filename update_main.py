import os

filepath = r"c:\Users\Vivek\Desktop\vpn sentinel\backend\main.py"
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update imports
old_import = "from fastapi import FastAPI, Depends, HTTPException"
new_import = "from fastapi import FastAPI, Depends, HTTPException, Header, Query"
code = code.replace(old_import, new_import)

# 2. Add get_tenant_id dependency
dependency_code = """
def get_tenant_id(tenant: Optional[str] = Query(None), x_tenant_id: Optional[str] = Header(None)) -> str:
    return tenant or x_tenant_id or "default"
"""
# Insert it before IngestResponse
code = code.replace("class IngestResponse(BaseModel):", dependency_code + "\nclass IngestResponse(BaseModel):")

# 3. Update ingest_flow signature and database save
old_ingest_sig = "def ingest_flow(flow: FlowInput, request: Request, db: Session = Depends(get_db)):"
new_ingest_sig = "def ingest_flow(flow: FlowInput, request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):"
code = code.replace(old_ingest_sig, new_ingest_sig)

old_log_entry = """    log_entry = FlowInferenceLog(
        duration=flow.duration,"""
new_log_entry = """    log_entry = FlowInferenceLog(
        tenant_id=tenant_id,
        duration=flow.duration,"""
code = code.replace(old_log_entry, new_log_entry)

# 4. Update get_stats
old_get_stats = """@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    logs = db.query(FlowInferenceLog).all()"""
new_get_stats = """@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    logs = db.query(FlowInferenceLog).filter(FlowInferenceLog.tenant_id == tenant_id).all()"""
code = code.replace(old_get_stats, new_get_stats)

# 5. Update get_history
old_get_history = """@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    logs = db.query(FlowInferenceLog).order_by(FlowInferenceLog.timestamp.desc()).limit(100).all()"""
new_get_history = """@app.get("/api/history")
def get_history(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    logs = db.query(FlowInferenceLog).filter(FlowInferenceLog.tenant_id == tenant_id).order_by(FlowInferenceLog.timestamp.desc()).limit(100).all()"""
code = code.replace(old_get_history, new_get_history)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
