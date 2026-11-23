# Experiments

How to measure a change on the machine so the result says what it was measured on, and how to keep a claim about the machine honest: `nerv-run` records a command with the machine it ran on, and `balthasar` keeps claims of a fixed set of shapes, each tried by the control its shape demands.

## Synopsis

After reading this chapter, you will know:

- how to record a command's run with the generation, kernel, command line and settings it ran under, and the numbers it measured
- what a claim is, which shapes a claim can take, and what decides its standing
- how to record a claim, run its trial, and read the verdict
- how a program reads the same claims without balthasar

Before reading it, you should know:

- what a generation and a slot are: [Updates and generations](generations.md)
- what a store, a stream and a view are: [The machine's record](what-the-machine-remembers.md)

## Why it works this way

A measurement copied into a table by hand loses what it was measured on. A week later nobody knows which kernel it was, whether a sysctl had been changed for another test, or whether the number came from the run that worked or the one that was kept. And a conclusion drawn from it carries no date it goes stale on: it stays true in the table long after the machine has moved on.

`nerv-run` makes the record the run itself. It reads the machine before the command starts, measures the command while it runs, and writes both into your MAGI store as one record, so running a control is no more work than running the test.

A claim is a statement of cause about the machine, and the hard part of keeping one honest is the test. If whoever makes a claim also writes the test that could disprove it, a test that cannot fail is the easiest to write. So a claim here takes one of a fixed set of shapes, and the shape decides the trial: which runs count, in which arm, how many, and in what order. A claim carries no test of its own and no confidence. Its standing is what its trials found, and the date its falsifier last ran is kept beside it, so a claim nobody has tested says so.

## Recording a run

Put `nerv-run` in front of a command:

```
$ nerv-run --sysctl vm.min_free_kbytes --param nvidia.EnableSystemMemoryPools -- ./bench
```

The command runs as it would have: its output is its own, and `nerv-run` exits with its status. One line on standard error says where the run was recorded:

```
nerv-run: recorded as run 4 in run/runs
```

The record holds:

- the command, and the hash of the file it ran;
- the generation, the slot, the kernel and its command line as booted, and the host;
- each sysctl and module parameter named, as it read when the command started, and any that could not be read;
- the wall time, the exit status or the signal that ended it;
- each metric the command measured.

A command reports a metric by writing `NAME=NUMBER` lines to the file `$NERV_RUN_METRICS` names, which keeps its own output free for people. Name each metric it is expected to write with `--metric NAME`; a declared metric that is missing, written twice or not a number is recorded as that, never as a value.

If magid cannot be reached, the command does not run: an unrecorded run is not a run.

```
$ magi tail run/runs -n 1
```

prints the last run with every field.

## Recording a claim

A claim is about an effect, something a probe can show to hold or not. Record the effect first: the probe, the test that it held, and the condition a run has to be under to count at all.

```
$ balthasar effect context-creation-under-load --holds exit==0 --given 'mem_available_gib<=32' -- ~/probes/49
```

The probe is pinned by the hash of its file, so a run of an edited probe is never evidence. An effect is never changed: another probe or another test is another effect, under another name.

Then the claim:

```
$ balthasar claim 'setting-required-for(kernelcore=16G, context-creation-under-load)'
setting-required-for(kernelcore=16G, context-creation-under-load) recorded, unverified, due again by 2027-02-21 13:46 UTC; trial 1 opened on this machine (balthasar plan shows it)
```

Recording a claim opens its first trial, on the machine it was recorded on, with the plan its shape derives. `--recheck-by YYYY-MM-DD` sets when it is due again, no later than its shape allows.

## Running its trial

```
$ balthasar plan 'setting-required-for(kernelcore=16G, context-creation-under-load)'
```

shows what the trial needs: the host, generation and kernel every run must be on, the command line they must share apart from the setting, the probe, the two arms, how many runs each needs, and how many reboots the trial costs. It also says which arm this boot is in, and the command for the next run:

```
$ nerv-run --trial 'setting-required-for(kernelcore=16G, context-creation-under-load)' -- ~/probes/49
```

The arm a run is in is read from what it recorded, never from what anyone says it was for. For `setting-required-for`, runs alternate: without the setting, with it, and without it again, so the machine drifting during the trial cannot pass for the effect. A command-line setting is changed between arms by sealing the slot with it and rebooting ([Updates and generations](generations.md)).

After each run:

```
$ balthasar judge 'setting-required-for(kernelcore=16G, context-creation-under-load)'
```

While the runs decide nothing, `judge` says how far the trial has got and writes nothing. When they decide, it closes the trial with its verdict:

- **falsified**: one run without the setting in which the effect held;
- **survived**: every run without the setting failed the effect and every run with it held, with enough runs in each arm, bracketed;
- **inconclusive**: a run with the setting failed the effect, so the trial proves nothing; the claim's standing stays as it was.

`balthasar trial CLAIM` opens the next trial, on the machine as it is then.

## Reading the claims

```
$ balthasar claims
setting-required-for(kernelcore=16G, context-creation-under-load)
  unverified; last falsified never; due now: no trial has decided it
  trial 1 open: balthasar plan shows what it needs
```

A program reads the same rows from the store, with no balthasar involved. `claim/claims` holds every claim, `claim/trials` every trial opened and closed, and two views list the claims that need attention:

```
$ magi facts claim/unverified
$ magi facts claim/pending
$ magi tail claim/trials
```

`claim/unverified` holds the claims no trial has decided, and `claim/pending` those with a trial open.

## Promoting a rebuilt tree

A source tree read by new rules into the partition beside the live one ([The machine's record](what-the-machine-remembers.md#asking-about-your-source-code)) is promoted through a trial:

```
$ balthasar promote --name nerv-linux
```

The standby partition is judged as `magi-code promote` judges it, the judgement is recorded in `balthasar/promotions` whether it holds or not, and only then is the partition promoted. `--force` promotes a partition that reads files worse than the live one, and the record says it was forced.

## Reference

| command | does |
| --- | --- |
| `nerv-run [--trial CLAIM] [--sysctl NAME].. [--param MODULE.NAME].. [--metric NAME].. CMD...` | run a command and record it |
| `balthasar shapes` | the shapes a claim can take, each with its falsifier |
| `balthasar effect NAME --holds TEST [--given TEST] -- PROBE...` | record an effect |
| `balthasar effects` | every effect |
| `balthasar claim CLAIM [--recheck-by YYYY-MM-DD]` | record a claim and open its first trial |
| `balthasar claims` | every claim, its standing, when its falsifier last ran, when it is due |
| `balthasar plan CLAIM` | a claim's open trial, and the runs that count so far |
| `balthasar judge CLAIM` | close the open trial if its runs decide it |
| `balthasar trial CLAIM` | open a new trial on this machine |
| `balthasar promote [--name NAME] [--force]` | judge, record and promote a tree's standby partition |

| shape | its trial |
| --- | --- |
| `setting-required-for(SETTING, EFFECT)` | the effect's probe run with the setting and without it, on one host, generation and kernel, nothing else on the command line changed, at least two runs in each arm, alternating without, with, without. A SETTING is `NAME=VALUE` on the kernel command line, `sysctl:NAME=VALUE`, or `param:MODULE.NAME=VALUE`. Due again within 90 days. |

A TEST is a metric, a comparison (`==`, `!=`, `<`, `<=`, `>`, `>=`) and a number. Every run has the metrics `exit` (the status, or 128 and the signal) and `wall_ns`.

| stream | holds |
| --- | --- |
| `run/runs` | every run nerv-run recorded |
| `claim/effects` | every effect |
| `claim/claims` | every claim and its standing |
| `claim/trials` | every trial, opened with its plan and closed with its verdict |
| `claim/unverified`, `claim/pending` | the claims no trial has decided; those with a trial open |
| `balthasar/promotions` | every judgement of a tree's standby partition |
