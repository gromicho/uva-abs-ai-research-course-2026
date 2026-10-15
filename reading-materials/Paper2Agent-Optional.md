# Optional: Paper2Agent

Short demo only (10–15 minutes). Not recommended as a participant exercise.

## What it is

[Paper2Agent](https://github.com/jmiao24/Paper2Agent) turns a paper's code into a tool (an MCP server) that an AI assistant can call. It has no licence fee; assistant usage depends on the account.

## What we tried (9 October 2026)

We packaged the Card & Krueger replication. The tool reruns the fixed public analysis and returns the tables, results and logs, including the part-time weight variants and the model (v) ownership control. It does not take new datasets or arbitrary parameters.

- Preparation took about 22 minutes, including implementation, documentation, independent tests and several clean installations.
- Eight verification tests passed (numerical agreement, repeated calls, meaningful failures), and the packaged ZIP reproduced all results after a fresh install.
- Requirements: the Paper2Agent skill, a coding agent with sub-agent support, and FastMCP 4.0.3 with pinned dependencies.

## Assessment

It worked as intended but added nothing to our understanding of the paper. For teaching it works against our purpose: it hides exactly the steps participants should do themselves, namely reading the code, making the modelling choices and checking the numbers. Its value is reuse once a replication is trusted, which makes it a good closing demo of "what comes next".
