#!/bin/bash

cd /root/code/flix-finder
/root/miniconda3/bin/conda run -n langchain streamlit run --ui.hideTopBar True --client.toolbarMode viewer main.py --server.port 80
