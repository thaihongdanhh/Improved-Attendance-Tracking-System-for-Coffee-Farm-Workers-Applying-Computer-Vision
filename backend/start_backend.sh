#!/bin/bash
source /home/ailab/anaconda3/etc/profile.d/conda.sh
conda activate kmou_aiface_v2
cd /mnt/data/AIFace/AICoffeePortal/backend
python run_simple.py 2>&1 | tee /mnt/data/AIFace/AICoffeePortal/logs/backend.log
