# Eye Tracking and Heart Rate Visualization in Virtual Therapy

This project is the result of Bachelor's thesis at Comenius University, Faculty of Mathematics, Physics and Informatics. It presents a system designed to collect, synchronize, and visualize eye-tracking and heart rate data during Virtual Reality (VR) therapy sessions. The aim is to support psychological research by enabling a detailed analysis of user attention and physiological response within VR environments.

## Project Overview

Virtual therapy offers a novel approach for psychological treatment and research. By combining eye-tracking (using HTC Vive Pro Eye and Tobii XR SDK) with heart rate monitoring (Polar H10), this application allows for real-time data capture and post-session visualization of user interactions and emotional states.

### Key Features

- **Data Collection in VR**:
  - Eye-tracking (fixation detection, object tagging)
  - Heart rate data synchronization (via Bluetooth using Polar H10)

- **Visualization Tool**:
  - Screenshot-based timeline navigation
  - Graph of heart rate values over time
  - Fixation analysis on objects (tabular view)
  - Visual cues indicating user gaze points

- **Technologies Used**:
  - Unity (VR environment and data collection)
  - Python (Data processing and visualization with PyQt)
  - Tobii XR SDK, SteamVR, SRanipal
  - Polar H10 heart rate monitor

## Folder Structure
data-folder
├── images/ # Screenshots from VR with gaze points
├── data.csv # Eye-tracking data (object, tag, start/end time)
├── hr_data.csv # Heart rate data (system time, elapsed time, BPM)


## Getting Started

### Prerequisites

- Unity with SteamVR and Tobii XR SDK
- Python 3.x with the following packages:
  - `PyQt5`
  - `numpy`
  - `matplotlib`
  - `pandas`

### Running the System

1. Launch the VR data collection system in Unity.
2. Ensure the SRanipal runtime is active.
3. Connect the Polar H10 sensor via the provided external script.
4. Run the Python visualization tool and select the session data folder.
5. Browse fixation and heart rate patterns using the Graph and Table views.

## Purpose

This tool is intended for psychologists and researchers involved in VR therapy experiments. It allows for a deeper understanding of user engagement and the physiological impact of specific VR objects (like trees, animals, or urban elements).

## Limitations

- The system is currently tailored to a specific forest scene.
- Integration with the full therapy suite (including city environments) is pending future work.

## Acknowledgments

Special thanks to:
- RNDr. Zuzana Berger Haladová, PhD. – thesis supervisor
- Mgr. Dagmar Szitás – psychologist on the Virtual Therapy project
- Prof. Mgr. Júlia Halamová, PhD. – research advisor

---

**Author:** Zuzana Matúšková  
**Thesis:** "Utilizing Eye Tracking in Virtual Therapy"  
**Year:** 2025

