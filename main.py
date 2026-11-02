import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from db import get_db, Chemical, Scientist, Storage, Robot, Task
from simulation import run_placement_simulation, run_fetch_simulation, run_slab_placement_simulation
from visualizer import generate_rack_image

app = FastAPI(title="Intelligent Technology for Enhanced Robotic Navigation")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _page(name: str) -> str:
    with open(os.path.join(BASE_DIR, "static", name), encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return _page("index.html")

@app.get("/simulation", response_class=HTMLResponse)
def simulation_page():
    return _page("simulation.html")

@app.get("/api/scientists")
def get_scientists(db: Session = Depends(get_db)):
    return db.query(Scientist).all()

@app.get("/api/chemicals")
def get_chemicals(db: Session = Depends(get_db)):
    return db.query(Chemical).all()

@app.get("/api/chemicals/search")
def search_chemical(barcode: str, db: Session = Depends(get_db)):
    c = db.query(Chemical).filter(Chemical.barcode == barcode).first()
    if not c:
        raise HTTPException(status_code=404, detail="Chemical not found")
    return c

@app.get("/api/placements")
def get_placements(scientist_id: int = None, db: Session = Depends(get_db)):
    q = db.query(Task)
    if scientist_id:
        q = q.filter(Task.scientist_id == scientist_id)
    return q.all()

@app.post("/api/placements")
def create_placement(chemical_id: int, storage_id: int, scientist_id: int, db: Session = Depends(get_db)):
    c = db.query(Chemical).filter(Chemical.id == chemical_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Chemical not found")

    s = db.query(Storage).filter(Storage.id == storage_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Storage not found")
    if s.occupied == 1:
        raise HTTPException(status_code=400, detail="Storage slot is occupied")

    r = db.query(Robot).filter(Robot.status == "idle").first()
    if not r:
        raise HTTPException(status_code=400, detail="No robot available")

    t = Task(
        robot_id=r.id,
        storage_id=storage_id,
        chemical_id=chemical_id,
        scientist_id=scientist_id,
        status="placed",
        start_time=str(datetime.now())
    )
    db.add(t)
    s.occupied = 1
    r.status = "busy"
    db.commit()

    sim_log = run_placement_simulation(r, s, c)

    r.status = "idle"
    db.commit()

    return {"message": "Chemical placed successfully", "task_id": t.id, "simulation": sim_log}

@app.get("/api/slab")
def get_slab(db: Session = Depends(get_db)):
    chemicals = db.query(Chemical).order_by(Chemical.id).all()
    tasks = db.query(Task).order_by(Task.id).all()

    latest = {}
    for t in tasks:
        latest[t.chemical_id] = t

    result = []
    for position, c in enumerate(chemicals, start=1):
        t = latest.get(c.id)
        if t is None:
            location = "slab"
            storage_id = None
        elif t.status == "placed":
            location = "rack"
            storage_id = t.storage_id
        else:
            location = "slab_main"
            storage_id = None

        result.append({
            "chemical_id": c.id,
            "name": c.name,
            "formula": c.formula,
            "position": position,
            "location": location,
            "storage_id": storage_id
        })

    return result

@app.post("/api/slab/placements")
def place_from_slab(chemical_id: int, storage_id: int, scientist_id: int, db: Session = Depends(get_db)):
    c = db.query(Chemical).filter(Chemical.id == chemical_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Chemical not found")

    s = db.query(Storage).filter(Storage.id == storage_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Storage not found")
    if s.occupied == 1:
        raise HTTPException(status_code=400, detail="Storage slot is occupied")

    r = db.query(Robot).filter(Robot.status == "idle").first()
    if not r:
        raise HTTPException(status_code=400, detail="No robot available")

    t = Task(
        robot_id=r.id,
        storage_id=storage_id,
        chemical_id=chemical_id,
        scientist_id=scientist_id,
        status="placed",
        start_time=str(datetime.now())
    )
    db.add(t)
    s.occupied = 1
    r.status = "busy"
    db.commit()

    sim_log = run_slab_placement_simulation(r, s, c)

    r.status = "idle"
    db.commit()

    return {"message": "Chemical moved from slab to rack", "task_id": t.id, "simulation": sim_log}

@app.put("/api/placements/{pid}/fetch")
def fetch_placement(pid: int, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == pid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Placement not found")

    t.status = "fetched"
    t.end_time = str(datetime.now())

    s = db.query(Storage).filter(Storage.id == t.storage_id).first()
    r = db.query(Robot).filter(Robot.id == t.robot_id).first()

    r.status = "busy"
    db.commit()

    sim_log = run_fetch_simulation(r, s, db.query(Chemical).filter(Chemical.id == t.chemical_id).first())

    s.occupied = 0
    r.status = "idle"
    db.commit()
    return {"message": "Chemical fetched successfully", "simulation": sim_log}

@app.delete("/api/placements/all")
def delete_all_placements(db: Session = Depends(get_db)):
    db.query(Task).delete()
    db.query(Storage).update({Storage.occupied: 0})
    db.query(Robot).update({Robot.status: "idle", Robot.position: "home"})
    db.commit()
    return {"message": "All placements cleared"}

@app.get("/api/robot")
def get_robot(db: Session = Depends(get_db)):
    return db.query(Robot).all()

@app.get("/api/storage")
def get_storage(db: Session = Depends(get_db)):
    return db.query(Storage).all()

@app.get("/api/visualize/racks")
def visualize_racks(scientist_id: int = None, db: Session = Depends(get_db)):
    storage_list = db.query(Storage).all()

    chemical_map = {}
    tasks_q = db.query(Task).filter(Task.status == "placed")
    if scientist_id:
        tasks_q = tasks_q.filter(Task.scientist_id == scientist_id)

    for t in tasks_q.all():
        chem = db.query(Chemical).filter(Chemical.id == t.chemical_id).first()
        if chem:
            chemical_map[t.storage_id] = chem.name

    buf = generate_rack_image(storage_list, chemical_map)
    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
