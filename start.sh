#!/bin/bash
echo "Training Time-Series Model..."
python train_ts_model.py
echo "Starting API server..."
python app.py
