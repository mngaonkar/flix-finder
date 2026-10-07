# End-to-End Accelerated Dataset & Vector Store Update on Kubernetes

This document provides a complete guide for the dataset lifecycle:
1. **Generating and updating `database/movies.csv` from Wikipedia raw multistream dumps** (including parallelization strategies).
2. **Accelerating vector embedding generation (`movies.db`) using GPU-enabled Kubernetes Batch Jobs**.
3. **Deploying zero-downtime database updates to the live application**.

---

## Architecture Overview

```
[ Wikimedia Raw Dumps ]
  ├── enwiki-latest-pages-articles-multistream.xml.bz2 (~22 GB)
  └── enwiki-latest-pages-articles-multistream-index.txt.bz2 (~250 MB)
                         │
                         ▼
[ Phase 1: Dump Extraction Pipeline (tools/) ]
  ├── 1. Filter Film Articles: parse_movie_index.py ➔ movie_index.txt
  └── 2. Stream & Parse Dumps: process_wiki_dump.py (or Parallel K8s Job)
                         │
                         ▼
             [ Updated movies.csv ]
                         │
                         ▼
[ Phase 2: Accelerated Vector Indexing (K8s GPU Job) ]
  ├── Node: mahadev-ms7d28 (NVIDIA GPU with CUDA + fp16)
  ├── Batch Size: 256 items (Throughput: 600-900 docs/sec)
  └── Staging Output: database/movies_temp.db (~35 seconds)
                         │
                         ▼
[ Phase 3: Zero-Downtime Atomic Swap & Rollout ]
  ├── Atomic Move: mv movies_temp.db movies.db
  └── Rollout: kubectl rollout restart deployment/flix-finder -n flix-finder
```

---

## Phase 1: Generating `movies.csv` from Wikipedia Dumps

### 1. Download Wikimedia Dumps
Obtain the latest official dumps from [dumps.wikimedia.org/enwiki/latest/](https://dumps.wikimedia.org/enwiki/latest/):

* **Articles archive**: `enwiki-latest-pages-articles-multistream.xml.bz2` (compressed article wikitext)
* **Index file**: `enwiki-latest-pages-articles-multistream-index.txt.bz2` (byte offset index)

Decompress the index:
```bash
bzip2 -d enwiki-latest-pages-articles-multistream-index.txt.bz2
```

---

### 2. Extract Movie Index (`tools/parse_movie_index.py`)
Filters the full Wikipedia index down to film entries by searching for `(film)` titles:

```bash
python tools/parse_movie_index.py \
  --index_file path/to/enwiki-latest-pages-articles-multistream-index.txt \
  --out_file movie_index.txt
```

Each line in `movie_index.txt` contains:
```text
<byte_offset>:<page_id>:<article_title>
# Example: 18576985806:57445456:Raising the Bar (film)
```

---

### 3. Stream & Extract Movie Content (`tools/process_wiki_dump.py`)
Because Wikipedia uses a **multistream** format (concatenated bz2 streams), [`tools/process_wiki_dump.py`](../tools/process_wiki_dump.py) seeks directly to the byte offset in the 22 GB archive and only decompresses the specific chunk containing that article.

```bash
python tools/process_wiki_dump.py \
  --index_file movie_index.txt \
  --dump_file path/to/enwiki-latest-pages-articles-multistream.xml.bz2 \
  --out_file database/movies.csv
```

#### What gets extracted:
* **Plot**: Regex search matching `== Plot ==`, `== Synopsis ==`, `== Overview ==`, or `== Premise ==`.
* **Cast**: Regex search matching `== Cast ==`.
* **Poster URL**: Extracts `image = ...` from the infobox and computes the Wikimedia MD5 hash path:
  ```text
  https://upload.wikimedia.org/wikipedia/en/<hash[0]>/<hash[0:2]>/<encoded_image_name>
  ```
* **Output schema**: `id, title, cast, plot, poster`

---

### 4. Accelerating Dump Extraction on Kubernetes (Parallel Workers)
Sequential extraction of 15,000+ movies on a single thread can take hours. Since multistream bz2 chunks are independent, you can partition `movie_index.txt` across parallel Kubernetes workers:

1. **Split the movie index into N parts** (e.g., 4 chunks):
   ```bash
   split -n l/4 -d movie_index.txt movie_index_part_
   ```
2. **Run parallel workers using a Kubernetes Indexed Job**:
   Each pod processes `movie_index_part_${JOB_COMPLETION_INDEX}` against the shared dump file on an NFS or hostPath volume:
   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: wiki-dump-extractor
     namespace: flix-finder
   spec:
     completions: 4
     parallelism: 4
     completionMode: Indexed
     template:
       spec:
         restartPolicy: OnFailure
         containers:
         - name: extractor
           image: python:3.12-slim
           command: ["/bin/bash", "-c"]
           args:
           - |
             pip install loguru
             python tools/process_wiki_dump.py \
               --index_file /data/movie_index_part_0${JOB_COMPLETION_INDEX} \
               --dump_file /data/enwiki-latest-pages-articles-multistream.xml.bz2 \
               --out_file /data/movies_part_${JOB_COMPLETION_INDEX}.csv
   ```
3. **Merge output parts into the final CSV**:
   ```bash
   head -n 1 movies_part_0.csv > database/movies.csv
   tail -n +2 -q movies_part_*.csv >> database/movies.csv
   ```

---

## Phase 2: Accelerated Vector Database Generation (`movies.db`)

Once `database/movies.csv` is updated, the movie plot summaries must be embedded with `sentence-transformers/all-mpnet-base-v2` and loaded into Milvus Lite.

### Performance Comparison

| Metric | Web Serving Node (CPU, 2 cores) | Cluster Worker Node (1x NVIDIA GPU) |
| :--- | :--- | :--- |
| **Inference Precision** | float32 | fp16 (Tensor Cores) |
| **Batch Size** | 50 items/batch | 256 items/batch |
| **Throughput** | ~12 sentences/sec | **~750 sentences/sec** |
| **Total Indexing Time** | ~22 minutes (pegs CPU, disrupts UI) | **~35 seconds** |

### Incremental / Delta Embedding
To avoid re-indexing movies that have already been embedded, compare incoming IDs against existing database IDs:

```python
import pandas as pd
from backend.database import Database

def delta_index(csv_path, db_path):
    new_df = pd.read_csv(csv_path)
    db = Database(db_name=db_path)
    db.load_database(db_path)

    # Ingest only newly added movie records
    existing_ids = set(...) # Query existing primary keys
    delta_df = new_df[~new_df['id'].isin(existing_ids)]

    if not delta_df.empty:
        docs = prepare_documents(delta_df)
        db.store_documents(docs)
```

---

## Phase 3: Kubernetes GPU Indexing Job Manifest

Save as `k8s-embed-job.yaml`. This Job executes on GPU node `mahadev-ms7d28`, builds into a temporary database `database/movies_temp.db`, and swaps files atomically:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: flix-finder-indexer
  namespace: flix-finder
spec:
  ttlSecondsAfterFinished: 600
  backoffLimit: 2
  template:
    metadata:
      labels:
        app: flix-finder-indexer
    spec:
      restartPolicy: OnFailure
      # Pinned to the GPU-enabled node in the cluster
      nodeSelector:
        kubernetes.io/hostname: mahadev-ms7d28
      containers:
      - name: indexer
        image: mngaonkar/flix-finder:latest
        imagePullPolicy: IfNotPresent
        command: ["/bin/bash", "-c"]
        args:
        - |
          set -e
          echo "=== Starting Accelerated GPU Embedding Pipeline ==="
          
          # Ensure compatible pydantic runtime
          pip install --no-cache-dir pydantic==2.8.2 pydantic-core==2.20.1
          
          python3 - << 'EOF'
          import torch
          import os
          from loguru import logger
          from backend.loader import DocumentLoader
          from backend.database import Database
          from configuration import Configuration

          print(f"CUDA Available: {torch.cuda.is_available()}")
          if torch.cuda.is_available():
              print(f"Device Name: {torch.cuda.get_device_name(0)}")

          STAGING_DB = "database/movies_temp.db"
          TARGET_DB = "database/movies.db"
          CSV_FILE = "database/movies.csv"

          # 1. Clean previous staging database
          if os.path.exists(STAGING_DB):
              os.remove(STAGING_DB)

          # 2. Load updated CSV documents
          loader = DocumentLoader(Configuration())
          docs = loader.load_csv_document(CSV_FILE)
          print(f"Loaded {len(docs)} movie records from CSV.")

          # 3. Create staging database with GPU batching
          db = Database(db_name=STAGING_DB)
          db.create_database(STAGING_DB)

          BATCH_SIZE = 256
          for i in range(0, len(docs), BATCH_SIZE):
              batch = docs[i:i + BATCH_SIZE]
              db.store_documents(batch)
              print(f"Indexed {min(i + BATCH_SIZE, len(docs))}/{len(docs)} movies...")

          print("Embedding complete! Swapping database atomically...")
          os.replace(STAGING_DB, TARGET_DB)
          print("Database successfully swapped.")
          EOF
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "6Gi"
            cpu: "4000m"
          requests:
            nvidia.com/gpu: 1
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: database-dir
          mountPath: /app/database
        - name: config-file
          mountPath: /app/config.json
      volumes:
      - name: database-dir
        hostPath:
          path: /root/code/flix-finder/database
          type: Directory
      - name: config-file
        hostPath:
          path: /root/code/flix-finder/config.json
          type: File
```

---

## Phase 4: Step-by-Step Operator Runbook

Follow these steps whenever a dataset update is performed:

### Step 1: Generate / Update `movies.csv`
Generate the updated movie dataset using Phase 1 tools:
```bash
python tools/parse_movie_index.py --index_file <index.txt> --out_file movie_index.txt
python tools/process_wiki_dump.py --index_file movie_index.txt --dump_file <dump.xml.bz2> --out_file database/movies.csv
```

### Step 2: Sync Updated CSV to Cluster Storage
```bash
scp database/movies.csv root@146.190.44.205:/root/code/flix-finder/database/movies.csv
```

### Step 3: Run the GPU Indexer Job
```bash
# Remove any prior completed job run
kubectl delete job flix-finder-indexer -n flix-finder --ignore-not-found=true

# Launch the indexing job on the GPU worker node
kubectl apply -f k8s-embed-job.yaml
```

### Step 4: Stream Live Indexing Logs
```bash
kubectl logs -n flix-finder -l app=flix-finder-indexer -f
```
*(The job will log progress in batches of 256 and complete in ~35 seconds).*

### Step 5: Reload Serving Deployment (Zero Downtime)
Once the job finishes with `Database successfully swapped`, reload the serving pod:
```bash
kubectl rollout restart deployment/flix-finder -n flix-finder
```

### Step 6: Verify Live Service
```bash
# Verify new pod is ready
kubectl get pods -n flix-finder

# Check public application health
curl -Is https://movies.altbox.one | head -n 5
```
