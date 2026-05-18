## Case Study Replication Guide

This folder contains scripts and resources to replicate the BPM26 Case Study. For a general project overview and dependencies, see the [main BPM26 README](../README.md).

### How to Replicate
1. Download the relevant documents (see below).
2. Use `upload.py` to upload each document to the file search store (see script usage below).
3. Run the analysis scripts as described below.

#### Script Usage

- **upload.py**: Uploads a document to the file search store.
	```sh
	python upload.py <path-to-file> <display-name>
	```

- **create.py**: Creates a new file search store (usually only needed once).
	```sh
	python create.py
	```

- **ProcessDescription.py**: Extracts requirements from a process description using Google GenAI. Example:
	```sh
	python ProcessDescription.py "<input-text>"
	```

- **ast_transform.py**: Transforms a requirements JSON file into AST format and computes similarity metrics.
	```sh
	python ast_transform.py <input_path.json>
	```

- **case_study_eval.py**: Evaluates AST/NL similarity for all JSON files in the Outputs directory.
	```sh
	python case_study_eval.py --input-dir Outputs
	```

---

### Source Documents

#### Healthcare
- [Guide to the preparation, use and quality assurance of blood components (EDQM, 21st Edition)](https://freepub.edqm.eu/publications/PUBSD-244/detail) (accessed May 18, 2026)
- [Guide to the preparation, use and quality assurance of blood components (EDQM, main site)](https://www.edqm.eu/en/blood-guide) (accessed May 18, 2026)
- [Guide to the quality and safety of tissues and cells for human application (EDQM, 5th Edition)](https://freepub.edqm.eu/publications/AUTOPUB_19/detail) (accessed May 18, 2026)
- [Guide to the quality and safety of organs for transplantation (EDQM, 9th Edition)](https://freepub.edqm.eu/publications/PUBSD-133/detail) (accessed May 18, 2026)
- [Guide to the quality and safety of pharmaceuticals (EDQM, 4th Edition)](https://freepub.edqm.eu/publications/AUTOPUB_26/detail) (accessed May 18, 2026)

#### Higher Education
- [Bayerisches Hochschulgesetz (BayHSchG)](https://www.gesetze-bayern.de/Content/Document/BayLBG) (accessed May 18, 2026)
- [Promotionsordnung TUM (2021)](https://www.docgs.tum.de/sites/default/files/2021-057_Promotionsordnung_23.08.2021.pdf) (accessed May 18, 2026)
- [Algemeine Prüfungsordnung TUM](https://portal.mytum.de/archiv/kompendium_rechtsangelegenheiten/apso/folder_listing)

---