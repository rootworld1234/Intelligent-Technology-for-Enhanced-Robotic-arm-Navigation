import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import io

def generate_rack_image(storage_list, chemical_map):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    cols = 5
    for s in storage_list:
        x = s.id % cols
        y = s.id // cols
        z = 0

        color = "tomato" if s.occupied else "lightgreen"
        ax.bar3d(x, y, z, 0.8, 0.8, 1, color=color, edgecolor="black", alpha=0.9)

        label = f"Rack {s.id}"
        chem = chemical_map.get(s.id)
        if chem:
            label += f"\n{chem}"

        ax.text(x + 0.4, y + 0.4, 1.2, label, ha="center", fontsize=7)

    ax.set_title("Storage Rack Visualization")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    ax.set_zlabel("")
    ax.set_zticks([])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf
