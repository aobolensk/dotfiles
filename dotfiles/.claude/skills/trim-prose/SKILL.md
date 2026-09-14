---
name: trim-prose
argument-hint: [light|aggressive|max|all] [scope]
description: Shrink or delete comments, docstrings, and documentation body text just authored or substantially rewritten in the current change, at a chosen aggressiveness (light/default/aggressive/max), or strip every comment in a named scope (all). Use when asked to trim, shorten, minimize, cut down, or remove comments, docstrings, doc or spec prose, or any mix. Touches prose only, never code logic.
---

# Trim Prose

Cut the prose this session added: inline comments, block comments, docstrings,
module and class headers, Args/Returns/Raises sections, and the body text of
documentation files. One scan of the changeset, one bar applied to all of it.
Leave prose that predates this session alone, even lines lightly touched by a
nearby edit, unless named explicitly.

## Level

Read the level off the arguments (`--light`, `--aggressive`, `--max`, `--all`,
or the bare words). No level given: reuse the level of the last invocation in
this session, else **default**. A repeat invocation with no new level means the
last pass was too timid — go one level up and re-examine everything it kept.
Escalation stops at `max`: `all` applies only when asked for by name.

| Level | Bar |
| --- | --- |
| `light` | Shrink. Delete only when the WHY is dead. Multi-line to one line where the WHY survives. |
| `default` | Shrink hard. One line is the target. Delete anything restating the code. |
| `aggressive` | Deletion is the default outcome. Only "What earns a line" survives, and it survives as one line. |
| `max` | Keep only what stops a misread. Module headers: one paragraph. Test prose gone unless naming a failure mode. |
| `all` | Not a bar. Delete every comment and docstring in the scope, whoever wrote it and whenever. See "Level all". |

## Level all

`all` drops both the judgement of the other levels and the session boundary
they respect: every comment and docstring in the scope goes, including prose
predating this session and prose "What earns a line" would keep. Step 3 still
holds. Documentation files are out of scope, since stripping the body text of a
doc deletes it rather than trims it.

It needs an explicit scope: a file, a directory, a function. Given none, ask
for one rather than falling back to the changeset. Report the count deleted per
file, and flag any deleted comment that carried a constraint, workaround, or
failure mode the code does not otherwise state.

## What earns a line

A constraint, an invariant, a unit or range, a side effect, an ordering
guarantee, a failure mode, a workaround and what it works around, or the reason
a thing exists at all. Nothing else.

Never earns a line: a paraphrase of the name, a walk through what the body does,
a list of what the module contains, a restated parameter, a point another
comment or docstring already makes, an example the tests already give, hedging.

## In documentation files

In a doc, a spec, a release note, or a changelog the body text is the artifact
rather than commentary on it, so "the reader gets it from the code" is not a
reason to cut. Apply the same level, measured against the document instead of
the code, and delete only what the document already carries elsewhere:

- Two entries stating one rule from opposite directions. State it once and have
  the second refer back to the first.
- A sentence that follows from the entries around it.
- Illustration inside a normative sentence: parentheticals, "for example"
  clauses, and API or intrinsic names the sentence already cites.
- Lead-ins that restate the scope the entry heading gives, and hedging.

Prefer inverting a sentence over qualifying it: lead with the case that holds
and let the fallback follow, rather than leading with the fallback and adding
an "unless" clause.

Never cut a normative statement, a name, a value, or a range. An
under-specified spec is worse than a wordy one, and where a rule and its
exception both hold, both stay.

## Steps

1. Scan the **full changeset**: `git diff` (add `--staged`, or `HEAD~1` /
   `main...HEAD` if already committed this session), including files a
   background or forked agent touched. Narrowing by memory of "which files had
   the interesting changes" silently skips them. Match added (`+`) lines only.
   Find prose by language convention: `#`/`//`/`/* */` comments, `"""`/`'''`
   in Python, `/** */` in JS/TS/Java/C++, `///` or `//!` in Rust, `#` doc
   comments in Ruby, doc attributes elsewhere. In documentation files (`.rst`,
   `.md`, `.txt`, `.adoc`) the added body text is itself in scope. At `all`,
   scan the named scope instead of the changeset, matching every comment in it
   rather than added lines only.
2. Cut each one to the level's bar, hardest case first (at `all` the bar is
   deletion, so go straight to step 3):
   - Delete it. At `aggressive` and up this is the right answer for most short
     functions, most one-purpose classes, and most tests.
   - Otherwise one line. A summary line above a paragraph restating it is one
     line, not two. Re-trim one-liners that can still shrink.
   - Beyond three lines, a docstring is a design doc on a callable: keep the
     single load-bearing constraint and drop the narrative around it.
   - Keep an Args/Returns/Raises entry only for what the signature cannot
     express. Delete the section when every entry fails that test, and delete
     entries freely: a partial list is fine.
   - In a module or package header, cut every paragraph the reader gets from
     the code below. What stays is why the module exists, the constraint it
     enforces, the failure mode it avoids, said once.
   - In a test, delete unless it names a failure mode or consequence the test
     name does not.
   - In a documentation file, follow "In documentation files" above: collapse
     and cross-reference rather than delete, and keep every normative claim.
   - Never invent detail that was not already there.
3. Leave alone: directive comments (`# noqa`, `# type: ignore`,
   `eslint-disable`, `#pragma`, shebangs, license headers) and, in test files
   (`.ll`, `.mir`, `.test`), CHECK/LABEL/RUN directives. The comment char there
   covers both prose and directives: trim only the prose.
4. Delete whole lines rather than blanking them in place, and do not reflow
   surrounding code. In documentation files rewrap the edited entry to the
   width the file already uses, and leave neighbouring entries unreflowed.
5. Keep house rules: no em-dashes, no non-ASCII symbols, no semicolons, no
   possessive "'s".
6. Re-read each file after cutting, confirm the deletions landed, and report
   per file what was deleted and what was collapsed, with the level used.

## Do NOT

- Do NOT edit prose that predates this session's changes, except at `all`.
- Do NOT run `all` without an explicit scope.
- Do NOT touch code logic, only prose.
- Do NOT convert a docstring into a comment to dodge the rules.
- Do NOT skip or weaken a documentation file's normative claims; see
  "In documentation files".
- Do NOT commit or stage.
