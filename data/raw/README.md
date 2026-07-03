# Datasets Overview


### 1. Download & Installation Status                                                                                                                                                                 
                                                                                                                                                                                                        
  All datasets are fully installed, verified, and loadable:                                                                                                                                               
                                                                                                                                                                                                          
  • AmbiK: Verified & loadable (400 test cases).                                                                                                                                                        
  • CLARA/SaGC: Verified & loadable (5,345 entries).                                                                                                                                                    
  • SafeAgentBench: Verified & loadable (700 rows total across unsafe, safe, and abstract splits).                                                                                                     
  • IndirectRequests: Verified & loadable (906 rows).                                                                                                                                                     
  • TEACh: Extracted successfully from  games.tar.gz  (171 MB) into  data/raw/TEACh/games/  containing  train  (1,482 game JSONs),  valid_seen , and  valid_unseen .                                    
  • ClariQ: Verified & loadable (9,177 turns in train.tsv).                                                                                                                                               
                                                                                                                                                                                                        
  ### 2. Sourcing and Metadata for IndirectRequests                                                                                                                                                       
                                                                                                                                                                                                        
  • Source URL: Hugging Face: msamogh/indirect-requests https://huggingface.co/datasets/msamogh/indirect-requests                                                                                         
  • Paper: "Making Task-Oriented Dialogue Datasets More Natural by Synthetically Generating Indirect User Requests" (COLING 2025 / arXiv 2024) by Amogh Mannekote et al.                                  
  • Goal: This dataset contains indirect user requests (e.g., "I could really go for some biryani" instead of a direct instruction) and slot target values (including  "<ambiguous>"  indicating that   
  clarification is needed).                                                                                                                                                                               
                                                                                                                                                                                                       
  ### 3. Other Datasets Mentioned in  spec_text.txt                                                                                                                                                       
                                                                                                                                                                                                          
  In the research proposal, these four additional datasets are noted as reserved for augmentation and referential-grounding sub-evaluations:                                                             ▄
                                                                                                                                                                                                         ▀
 1. Dynamic-RDMM:                                                                                                                                                                                       
      • URL: IEEE Xplore / TechRxiv https://www.techrxiv.org/doi/full/10.36227/techrxiv.173168249.46363065/v1                                                                                            
      • Paper: "Dynamic RDMM: Scalable, Controllable Dataset Generation for Instruction-Grounded Robot Learning" (Humanoids 2025).                                                                       
  2. ReferIt3D (Nr3D, Sr3D):                                                                                                                                                                             
      • URL: Project Website https://referit3d.github.io | GitHub: referit3d/referit3d https://github.com/referit3d/referit3d                                                                            
      • Goal: Evaluates fine-grained 3D referential grounding.                                                                                                                                           
  3. RefCOCO:                                                                                                                                                                                            
      • URL: Hugging Face Mirror https://huggingface.co/datasets/PaDT-MLLM/RefCOCO | GitHub API: lichengunc/refer https://github.com/lichengunc/refer                                                    
      • Goal: Evaluates referring expression comprehension on MS COCO 2014 images.                                                                                                                       
  4. Collaborative Manipulation Corpus:                                                                                                                                                                  
      • URL: GitHub: personalrobotics/collaborative_manipulation_corpus https://github.com/personalrobotics/collaborative_manipulation_corpus                                                            
      • Goal: Evaluates spatial referring expression comprehension in tabletop robotic manipulation.                                                                                                     
                                                                                                                                                                                                         
                                                                                                                                                                                                         
  ### 4. Verification Check                                                                                                                                                                              
                                                                                                                                                                                                         
  I wrote and executed a dataset verification script (test_load_datasets.py) using python to ensure all files can be parsed without issues.                                                              
                                                                                                                                                                                                         
  I have updated the detailed documentation in the dataset_guide.md artifact, copied it to the project's folder (dataset_guide.md), and created the walkthrough.md artifact to summarize the             ▄
  verification.                                                                                                                                                                                          ▀
                            


This `raw` directory contains the four datasets you requested, each in its own sub‑folder.

## 1. SafeAgentBench
**Source:** https://huggingface.co/datasets/safeagentbench/SafeAgentBench

- A script `download_safeagentbench.py` is provided to download the entire dataset using the 🤗 `datasets` library. It will create a sub‑folder `SafeAgentBench` with the downloaded files.
- Run:
  ```bash
  uv run --with datasets python download_safeagentbench.py
  ```
- The script requires the `datasets` package (automatically installed by the command).

## 2. AmbiK (Ambiguous Tasks in Kitchen)
**Source:** https://huggingface.co/datasets/IvAnastasia/AmbiK (currently **not publicly available**). The dataset is mentioned in the literature but no public hub entry exists.

- A placeholder folder `AmbiK` is created. If you have private access (e.g., a download link or token), place the files there.
- When the dataset becomes public, you can replace the placeholder with the actual files.

## 3. TEACh (Task‑driven Embodied Agents that Chat)
**Source:** https://github.com/alexa/teach

- The repository has been cloned into `teach`.
- To download the large archive files (≈10 GB total) you need to pull them from the S3 bucket `teach-dataset`. The bucket is **Requester Pays**, so you must specify that flag.
- **Using AWS CLI** (recommended):
  ```bash
  aws s3 cp s3://teach-dataset/all_games.tar.gz . --request-payer requester
  aws s3 cp s3://teach-dataset/edh_instances.tar.gz . --request-payer requester
  aws s3 cp s3://teach-dataset/experiment_games.tar.gz . --request-payer requester
  aws s3 cp s3://teach-dataset/images_and_states.tar.gz . --request-payer requester
  aws s3 cp s3://teach-dataset/tfd_instances.tar.gz . --request-payer requester
  ```
- **Using Boto3 (Python)** – see `download_teach_s3.py` for an example that sets `RequestPayer='requester'`.
- After downloading, extract each archive:
  ```bash
  tar -xzf all_games.tar.gz -C TEACh
  tar -xzf edh_instances.tar.gz -C TEACh
  # etc.
  ```
- All extracted contents will reside under the `TEACh` folder.

## 4. CLARA‑Dataset
**Source:** https://github.com/jeongeun980906/CLARA-Dataset

- The repository was cloned into `CLARA-Dataset`. The main data file is `data/agument.json` (~4.5 MiB) and a small `sample.json`.
- No further download steps are required.

---

### How to use the datasets
Each folder contains the raw files or scripts to obtain them. After downloading, you can point your data processing pipelines to these directories.

---

*Prepared by Antigravity on 2026‑07‑02.*
