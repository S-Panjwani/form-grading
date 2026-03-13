import json
import matplotlib.pyplot as plt

with open("pose_data.json") as f:
    data = json.load(f)

# Collect positions per landmark over time, relative to each ear
relative_to = {
    "LEFT_EAR":  {},
    "RIGHT_EAR": {}
}

for frame in data["frames"]:
    if frame["landmarks"] is None:
        continue
    t = frame["timestamp"]

    # Build a quick lookup for this frame
    lm_map = {lm["name"]: lm for lm in frame["landmarks"]}

    for ear_name, rel_data in relative_to.items():
        if ear_name not in lm_map:
            continue
        ear = lm_map[ear_name]

        for lm in frame["landmarks"]:
            name = lm["name"]
            if name == ear_name:
                continue  # skip the ear itself
            if name not in rel_data:
                rel_data[name] = {"timestamps": [], "x": [], "y": []}

            rel_data[name]["timestamps"].append(t)
            rel_data[name]["x"].append(lm["x"] - ear["x"])
            rel_data[name]["y"].append(lm["y"] - ear["y"])

# Plot
for ear_name, rel_data in relative_to.items():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(f"Landmark Position Relative to {ear_name}", fontsize=13)

    for name, vals in rel_data.items():
        ax1.plot(vals["timestamps"], vals["x"], label=name)
        ax2.plot(vals["timestamps"], vals["y"], label=name)

    ax1.set_title("Relative X Over Time")
    ax1.set_ylabel("ΔX")
    ax1.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax1.legend(loc="upper right", fontsize=7)
    ax1.grid(True)

    ax2.set_title("Relative Y Over Time")
    ax2.set_ylabel("ΔY")
    ax2.set_xlabel("Time (seconds)")
    ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax2.legend(loc="upper right", fontsize=7)
    ax2.grid(True)

    plt.tight_layout()
    fname = f"landmark_plot_{ear_name.lower()}.png"
    plt.savefig(fname, dpi=150)
    print(f"Saved: {fname}")

plt.show()