# Intelligent Technology for Enhanced Robotic Navigation

A web-based smart lab management prototype in which a simulated robotic arm stores and retrieves chemicals between a work slab and a wall-mounted storage rack. It combines a FastAPI backend, a SQLite inventory database and a live 3D digital twin built with Three.js.

![Dashboard](docs/dashboard.png)
![Simulation](docs/simulation.png)

## Features

- **Dashboard**: live KPIs, rack utilization, a 20-slot rack map, inventory status, recent activity and per-scientist workload (auto-refreshes every 5 s).
- **Simulation & Operations**: a 3D robotic arm with inverse-kinematics motion, a form to place chemicals from the slab into the rack, and one-click retrieval back out.
- **Inventory data**: chemical names, formulas and CAS numbers are pulled from [PubChem](https://pubchem.ncbi.nlm.nih.gov/) when seeding.
- **Rack visualization**: a server-rendered 3D rack image (Matplotlib) that updates after every operation.
- **REST API** with interactive docs at `/docs`.

## Tech stack

Python 3.10+, FastAPI, SQLAlchemy (SQLite), Matplotlib, Three.js, vanilla HTML/CSS/JS.

## Getting started

```bash
# 1. Install dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Create and seed the database (seeding needs internet access for PubChem)
python db.py
python seed.py

# 3. Run the app
python main.py
```

Open **http://localhost:8000** for the dashboard and **http://localhost:8000/simulation** for the simulation.

## Project structure

```
main.py          FastAPI app, page routes and REST API
db.py            SQLAlchemy models (Chemical, Scientist, Robot, Storage, Task)
seed.py          Populates the database (chemicals come from PubChem)
simulation.py    Generates the robot's step-by-step action logs
visualizer.py    Renders the rack image with Matplotlib
static/
  index.html         Dashboard page
  simulation.html    Simulation & operations page
  css/app.css        Shared styles
  js/sim.js          3D scene, arm kinematics and operation logic
```

## API overview

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/chemicals` | List chemicals |
| GET | `/api/chemicals/search?barcode=` | Look up a chemical by CAS number |
| GET | `/api/scientists` | List scientists |
| GET | `/api/storage` | Rack slot status |
| GET | `/api/robot` | Robot status |
| GET | `/api/slab` | Where every chemical currently is |
| GET/POST | `/api/placements` | List tasks / place a chemical in the rack |
| POST | `/api/slab/placements` | Move a chemical from the slab to the rack |
| PUT | `/api/placements/{id}/fetch` | Retrieve a chemical from the rack |
| DELETE | `/api/placements/all` | Clear all tasks and reset slots and robot |
| GET | `/api/visualize/racks` | PNG visualization of the rack |

## License

[MIT](LICENSE)
