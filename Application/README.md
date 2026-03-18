# Application Examples

This folder contains example models and specifications used for compliance verification.

## PNML-based verification

Use the repository below to verify the PNML model together with the specification XML files:

- https://github.com/rug-ds-lab/BPMVerification

Relevant files in this folder:

- `runningexample.pnml`
- `runningExamplePnmlSpec.xml`
- `runningexspec.xml`
- `runningexspec2.xml`
- `runningexspec3.xml`

Example command to use the CLI tool once dependencies are downloaded to a lib/ folder: 

```bash
java -cp "$(printf "%s:" lib/*.jar)" \
    nl.rug.ds.bpm.CommandlineVerifier \
    -p runningexample.pnml \
    -s runningexspec3.xml \
    -c ../NuSMV-2.7.1-linux64/bin/NuSMV \
    -v kripke \
    -o output \
    -l debug
```


## Process-tree-based verification

Use the repository below to verify the process tree example:

- https://github.com/JohannesLbck/ProcessTreeVerify

Relevant file in this folder:

- `RunningExampleTree.xml`

`RunningExampleTree.xml` already contains the ASTs in a requirements field.
