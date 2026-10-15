# Capstone example: Ocean Cleanup Data Challenge

An advanced example of a full research workflow with agents, for instructors or participants who want to see where this leads. Too demanding as a beginner exercise. Repository: https://github.com/gromicho/OceanCleanupDataChallenge

## What was done

Joaquim and his agents (Codex) took the challenge from raw sources to a complete research bundle: data extraction from PDF and Excel, interpretation of the rules, heuristic search, MILP formulations, Gurobi log analysis, an exact proof of optimality based on dynamic-programming bounds, a validator-compatible route drawing, a LaTeX article, a Beamer deck, and a separate paper on how the human steering and the agents interacted.

## Why it is useful for the course

- **It goes end to end.** The agents read files, wrote and ran code, inspected solver output, built a proof, made figures and compiled the paper.
- **Verification was the bottleneck.** A key moment was finding that Gurobi had *not* proved optimality. The proof came from a custom exact verifier, which was itself developed in the AI-assisted workflow. The researcher stays responsible for knowing what has and has not been proved.
- **It produces the artefacts this course asks for:** paper, slides, a reproducible code and data folder, an AI-use disclosure and a process account.
- **It complements the empirical Lab 4 case** with mathematical optimisation: formulation, bounds, exact certification and careful reading of solver logs.
