# Lab 4: reproducing a published paper

Evening 3. Leads: Marleen, Yenan, Joaquim. Draft by Joaquim, 15 October 2026, for discussion.

## Why this lab exists

By evening 3 participants have built things with an agent. This lab asks the harder question: can an agent reproduce someone else's published result, and can *you* tell whether it did? A matching number is the start of the work, not the end. The interesting part is which choices produce that number, and what the replication still does not establish.

## Structure (agreed with Marleen and Yenan, 14 October)

| Part | Time | Who | Content |
|---|---|---|---|
| Introduction | ~20 min | Marleen | AI for academic research, based on literature and her own experience. Message: lots of possibilities, but value only comes from deciding deliberately how to use it. Otherwise you end up digging your way out of agentic messes. |
| Demo 1: theory and finance | ~25 min | Yenan | Interactive: participants follow along with the same prompts, code or instructions. |
| Demo 2: applied and optimisation | ~25 min | Joaquim | Interactive, same set-up. Also shows calling a data API (e.g. WRDS, which UvA has access to) from the code editor. |
| Replication exercise | 60–90 min | all | See below. |
| Close | ~10 min | Marleen | What do we as academics contribute alongside this work, and should we optimise that human edge? |

Timing is a first guess and needs a dry run (see open items).

## The exercise

### Candidate paper

**Card & Krueger (1994), "Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania".** Tested on 9 October 2026. The README still lists "political bias in LLMs" as the Lab 4 candidate; the team should choose. Marleen suggested offering three or four pre-selected papers across domains (theoretical, empirical, computational), with Card & Krueger as the tested empirical one.

Why it works for a 90-minute exercise:

- The original data, codebook and SAS program are public (`labs/lab4-replication/get-data.ps1`).
- The question and the difference-in-differences design are accessible without an economics background.
- It replicates: all five Table 4 coefficients and standard errors match at the published precision on the same 357 restaurants.
- It hides real decisions that change the answer, which is what we want participants to find.

### What was tested

| Run | Tool | Outcome | Time |
|---|---|---|---|
| 1 | Codex, translating `check.sas` to Python | All five Table 4 entries match; balanced DiD 2.75 | ~4 min from download to results; a full run takes ~2.6 s |
| 2 | Claude Code, independently, without seeing run 1 | Same five matches; also explained the discrepancies below | ~1 min to the first matching run |
| 3 | Paper2Agent packaging of run 1 | Worked, but added nothing to understanding; not used in the course | ~22 min |

These are single runs by an experienced user, not student completion times. `labs/lab4-replication/facilitator/reference_solution.py` is run 2. It stops with an error if any value differs from the paper, and it does fail when the part-time weight, the model (v) controls or the treatment of closures is changed.

### Participant tasks

1. Get the data (`get-data.ps1`) and set up the environment (`requirements.txt`).
2. With the agent, rebuild full-time-equivalent employment and the regression sample, starting from `starter.py`.
3. Reproduce Table 4, models (i)–(v), and compare with the paper.
4. Explain every difference you find. Is the paper wrong, the code wrong, or your choice different?
5. Run one sensitivity check and say what changes.
6. Write down what the replication does **not** establish.
7. Keep a research log throughout (`templates/research-log.md`) and end with an AI-use disclosure (`templates/ai-disclosure.md`).

### Questions that make the exercise work

- **Sample restriction.** Applying the original wage-data restriction drops the sample from 384 to 357 restaurants and moves the DiD estimate from 2.75 to 2.33, the largest change among the alternatives tested. Why? (The 27 dropped stores work against the finding: 19 in New Jersey gained 4.55 FTE on average, 8 in Pennsylvania lost 3.59.) The restriction is only needed for the wage-gap models; the paper applies it everywhere so all columns share one sample.
- **Closures.** Permanently closed stores count as zero employment, temporarily closed ones as missing. Setting temporary closures to zero gives 2.51.
- **Footnote versus code.** The footnote to model (v) implies an ownership control that `check.sas` omits. Following the code gives 11.91; adding the control gives 11.98.
- **Standard errors.** For the New Jersey dummy the conventional SE is 1.19 (t ≈ 1.96); the robust HC1 SE is 1.45 (t ≈ 1.61). Significance depends on that choice.
- **Part-time weight.** Changing it from 0 to 1 moves the New Jersey estimate from 2.55 to 2.10 and the wage-gap estimate from 18.16 to 13.15.
- **Causality.** With two waves, parallel pre-trends cannot be tested directly. Numerical agreement does not validate the causal interpretation.

### Deliverable

One page per participant or pair: results reproduced, modelling choices and where they come from, one sensitivity check, what remains unverified, and the disclosure statement.

## Optional extensions

- `Capstone-Example-Ocean-Cleanup.md`: an end-to-end optimisation research project done with agents.

## Open items for the leads

- Choose the paper(s). Card & Krueger is tested; are there 2–3 others with working replication packages (Marleen's proposal)?
- The repo is public, so `facilitator/reference_solution.py` is visible to participants. Keep it here, move it to a private place, or publish it after the evening?
- Dry run of the student scaffold on a UvA-managed laptop and on a personal laptop.
- Python version: `scripts/setup-windows.ps1` targets 3.12.10; the replication was tested on 3.12.14.
- Pre-reading: the paper, sections on Tables 3 and 4 only?
