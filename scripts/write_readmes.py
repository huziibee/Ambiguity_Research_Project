import os

BASE_RAW_DIR = r"C:\Users\huzii\Documents\University\Research Project\risk-aware-ambiguity-manager\data\raw"

READMES = {
    "AmbiK": """# AmbiK Dataset

## Source & Citation
* **Paper**: *"AmbiK: A Benchmark for Ambiguity Resolution in Keyboard-Based Robot Control"* by Ivanova et al., ACL 2025.
* **Repository**: [GitHub: AmbiK](https://github.com/ambik-benchmark/ambik)

## Original Goal
AmbiK is designed to evaluate Large Language Models (LLMs) on their ability to classify, resolve, and clarify ambiguous household instructions when controlling a robot. It focuses on preference-based, common-sense, and safety ambiguities.

## Use in This Project
We use AmbiK to provide core examples of single-source ambiguities (referential, pragmatic, and safety-related) that require clarification or silent resolution. The standardized CSV maps instructions to the `command` field and environments to the `scene_context` field.
""",

    "CLARA-Dataset": """# CLARA / SaGC Dataset

## Source & Citation
* **Paper**: *"CLARA: A Cognitive Layer for Ambiguity Resolution in Robotic Tasks"* by Park et al., IEEE Robotics and Automation Letters (RA-L) 2024.
* **Repository**: [GitHub: CLARA-Dataset](https://github.com/CLARA-Dataset/CLARA)

## Original Goal
The dataset is built to evaluate a robot's ability to classify natural language instructions into three categories: clear (executable), ambiguous (needs clarification), or infeasible (incapable or unsafe), using visual/object scenes as context.

## Use in This Project
CLARA serves as the backbone dataset for evaluating clear, ambiguous, and infeasible routing. We extract the initial instructions as the `command` field, scene objects and floorplans as the `scene_context`, and the task domain as the `capability_context`.
""",

    "SafeAgentBench": """# SafeAgentBench Dataset

## Source & Citation
* **Paper**: *"SafeAgentBench: A Benchmark for Safety Evaluation of Large Language Model Agents"* by Yin et al., 2024.
* **Repository**: [GitHub: SafeAgentBench](https://github.com/SafeAgentBench/SafeAgentBench)

## Original Goal
SafeAgentBench evaluates LLM agents on their safety alignment and ability to reject harmful or high-risk instructions (e.g., fire hazards, property damage, or human harm) in simulated household environments.

## Use in This Project
SafeAgentBench provides critical rejection stress test cases. We use the `unsafe_detailed` and `abstract` splits to populate high-risk and critical safety rejection scenarios where the robot must output a `face_preserving_rejection` response.
""",

    "IndirectRequests": """# IndirectRequests Dataset

## Source & Citation
* **Paper**: *"Making Task-Oriented Dialogue Datasets More Natural by Synthetically Generating Indirect User Requests"* by Amogh Mannekote et al. (COLING 2025 / arXiv 2024).
* **Repository**: [Hugging Face: msamogh/indirect-requests](https://huggingface.co/datasets/msamogh/indirect-requests)

## Original Goal
This dataset provides synthetically generated, natural indirect requests (e.g., *"I could really go for some biryani"* instead of *"Find an Indian restaurant"*) for task-oriented dialogues, designed to test LLMs on pragmatic speech acts.

## Use in This Project
We use IndirectRequests to test pragmatic ambiguity and indirect speech acts (ISAs) in robot commands. The standardized CSV maps human utterances to the `command` field and situations to `scene_context`.
""",

    "TEACh": """# TEACh Dataset

## Source & Citation
* **Paper**: *"TEACh: Task-oriented Embodied Adversarial Dialogue for Couch-based Agents"* by Padmakumar et al., EMNLP 2022.
* **Repository**: [GitHub: alexa/teach](https://github.com/alexa/teach) | [GLAMOR-USC/teach_tatc](https://github.com/GLAMOR-USC/teach_tatc)

## Original Goal
TEACh is a dataset of human-human dialogues in which a Commander guides a Driver to complete complex, multi-step household tasks (like preparing coffee or washing dishes) in an embodied virtual environment (AI2-THOR).

## Use in This Project
TEACh represents our multi-turn dialogue dataset. We reconstruct commander/driver utterances into the `dialogue_history` column, using the high-level task description as the `command`.
""",

    "ClariQ": """# ClariQ Dataset

## Source & Citation
* **Paper**: *"ClariQ: A Benchmark for Clarification in Conversational Search"* by Aliannejadi et al., 2021.
* **Repository**: [GitHub: aliannejadi/ClariQ](https://github.com/aliannejadi/ClariQ)

## Original Goal
ClariQ is designed to evaluate conversational search systems on their ability to ask clarification questions when initial user queries are ambiguous or underspecified.

## Use in This Project
ClariQ provides conversational search clarification examples. It serves as a benchmark for evaluating when a system should clarify versus silently resolve queries based on user intent descriptions.
""",

    "Dynamic-RDMM": """# Dynamic-RDMM Dataset

## Source & Citation
* **Paper**: *"Dynamic RDMM: Scalable, Controllable Dataset Generation for Instruction-Grounded Robot Learning"* by Shady Nasrat, Minseong Jo, Seonil Lee, and Seung-Joon Yi (IEEE-RAS Humanoids 2025).
* **Repository**: [GitHub: shadynasrat/RDMM](https://github.com/shadynasrat/RDMM) | [Hugging Face: shadyy/ROBOCUP_24](https://huggingface.co/datasets/shadyy/ROBOCUP_24)

## Original Goal
This dataset contains natural language instructions and their corresponding structured robot action plans (e.g. `Move_To('coffee table') | Search_Person('Emma') | Follow()`) for 23 household robot tasks.

## Use in This Project
Dynamic-RDMM provides a large pool of text-to-action plans to evaluate programmatic execution capability matching. The natural language input maps to the `command` field, and the action plan is stored under `metadata.gold_plan`.
""",

    "ReferIt3D": """# ReferIt3D (Nr3D, Sr3D) Dataset

## Source & Citation
* **Paper**: *"ReferIt3D: Neural Listeners for Fine-Grained 3D Object Identification in Real-World Scenes"* by Panos Achlioptas et al., ECCV 2020.
* **Repository**: [GitHub: referit3d/referit3d](https://github.com/referit3d/referit3d)
* **Project Webpage**: [referit3d.github.io](https://referit3d.github.io)

## Original Goal
ReferIt3D contains fine-grained referring expressions for 3D objects in real-world indoor scans (ScanNet). It includes Nr3D (Natural Reference 3D, human-authored) and Sr3D (Synthetic Reference 3D, programmatically generated).

## Use in This Project
ReferIt3D serves as a benchmark for fine-grained 3D referential grounding. The standardized CSV maps referring expressions to the `command` field and scan IDs to the `scene_context` field.
""",

    "RefCOCO": """# RefCOCO Dataset

## Source & Citation
* **Paper**: *"Modeling Context in Referring Expressions"* by Licheng Yu et al., EMNLP 2016.
* **Repository**: [GitHub: lichengunc/refer](https://github.com/lichengunc/refer) | [Hugging Face: PaDT-MLLM/RefCOCO](https://huggingface.co/datasets/PaDT-MLLM/RefCOCO)

## Original Goal
RefCOCO is a visual referring expression dataset based on MS COCO images, used to evaluate models on localizing specific objects in images given natural language phrasings.

## Use in This Project
RefCOCO provides referring expression comprehension examples. We map referring expressions to the `command` field and image file names to the `scene_context` field.
""",

    "CollaborativeManipulationCorpus": """# Collaborative Manipulation Corpus

## Source & Citation
* **Paper**: *"A Corpus of Tabletop Spatial Instructions for Collaborative Robotic Manipulation"* by Rosario Scalise et al., IJRR 2018.
* **Repository**: [GitHub: personalrobotics/collaborative_manipulation_corpus](https://github.com/personalrobotics/collaborative_manipulation_corpus)

## Original Goal
This corpus contains spatial instructions given by human crowd-workers directing a robot or another human to select, move, or arrange wooden blocks on a tabletop.

## Use in This Project
We use this corpus to evaluate spatial referential grounding instructions in tabletop manipulation tasks. Standardized CSV maps tabletop spatial instructions to the `command` field and tabletop scenarios to `scene_context`.
"""
}

def main():
    print("Writing READMEs for all 10 datasets...")
    for folder, content in READMES.items():
        dir_path = os.path.join(BASE_RAW_DIR, folder)
        if not os.path.exists(dir_path):
            print(f"Folder {dir_path} not found. Creating it...")
            os.makedirs(dir_path, exist_ok=True)
        readme_path = os.path.join(dir_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote README.md to {readme_path}")
    print("Done.")

if __name__ == "__main__":
    main()
