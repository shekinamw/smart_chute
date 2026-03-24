# Smart Chute — Automated Waste Sorting System

> Ontario Tech University — ENGR 4940U Capstone | Group 15  
> Supervised by Dr. Mikael Eklund

A chute-based system that uses computer vision and servo-actuated flaps to sort
color-coded waste bags into three bins: **Recycling** (blue), **Compost**
(green), and **Garbage** (black).

---

## Architecture

```
smart_chute/
├── main.py                   # Entry point — CLI + pipeline loop
├── config.py                 # All constants, pins, HSV ranges, timing
├── system.py                 # AWSSSystem orchestrator (R3 class diagram)
│
├── hardware/                 # Hardware Abstraction Layer
│   ├── ir_sensor.py          # IRSensor        — breakbeam detection
│   ├── camera.py             # Camera           — Picamera2 wrapper
│   ├── flap_controller.py    # FlapController   — PCA9685 servo driver
│   └── bin_sensor.py         # BinLevelSensor   — HC-SR04 ultrasonic
│
├── processing/               # Computer Vision
│   └── classifier.py         # HSVBagClassifier — HSV color classification
│
├── utils/                    # Utilities
│   ├── storage.py            # StorageManager   — burst frames + sort logs
│   └── logger.py             # Bin-level logging + console status bars
│
├── web/                      # Flask dashboard (TBD)
├── tests/                    # Hardware test scripts (TBD)
└── docs/                     # Project documentation (TBD)
```

This structure matches the **R3 class diagram** exactly.

---

## Hardware

| Component              | Interface        | Notes                                     |
|------------------------|------------------|-------------------------------------------|
| Raspberry Pi 4B        | —                | Host controller                           |
| PCA9685 servo driver   | I2C (0x40)       | Direct smbus2 — no Blinka (Python 3.13)   |
| SG90 servos × 2       | PCA9685 CH11, 15 | External 5 V power (not Pi GPIO rail!)    |
| Pi Camera Global Shutter| CSI              | Manual focus lock, AWB on                 |
| IR breakbeam sensor    | GPIO 18          | 10 ms debounce, ~5 kHz polling            |
| HC-SR04 ultrasonic × 3 | GPIO 27/17, 13/19, 5/6 | Only RECYCLING wired currently     |



---

## Quick Start

```bash
# On the Raspberry Pi:
cd ~/smart_chute
python3 main.py

# With custom timing:
python3 main.py --delay 0.95 --hold 2.0 --focus 5.0

# All options:
python3 main.py --help
```

---

## Bin-Level Detection

The system uses HC-SR04 ultrasonic sensors to measure the distance from the
sensor (mounted at the top of each bin) to the waste surface.  Fill percentage
is calculated as `(1 - distance / bin_height) × 100`.

When a bin's measured distance falls below the `--full-at` threshold (default
5 cm), a **BIN FULL** alert is logged to `data/logs/bin_levels.txt` and printed
to the console.

Currently only the **RECYCLING** sensor is wired (TRIG=27, ECHO=17). To
activate additional sensors, uncomment the entries in `config.py`:

```python
ULTRASONIC_SENSORS = {
    "RECYCLING": {"trig": 27, "echo": 17},
    "COMPOST":   {"trig": 13, "echo": 19},   # ← uncomment
    "GARBAGE":   {"trig": 5,  "echo": 6},    # ← uncomment
}
```

---

## Output Files

| Path                                  | Content                          |
|---------------------------------------|----------------------------------|
| `data/logs/sorting_log_YYYYMMDD.txt`  | Per-bag sort events              |
| `data/logs/bin_levels.txt`            | Full-bin alerts + session blocks |
| `data/captures/bag_NNNN/`            | Burst frames + summary.txt      |

---

## License

Academic project — Ontario Tech University, 2025–2026.
