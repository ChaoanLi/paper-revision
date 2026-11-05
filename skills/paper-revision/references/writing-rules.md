# Writing rules for the manuscript

General rules for any text proposed for the paper. Project-specific rules (protected text,
terminology, positioning, journal requirements) are in `revision/rules.md` and win when they
conflict with these.

## Content

1. **Main text = essentials.** Method, theory, and the minimal evidence for the paper's claims.
   Checks done only because a reviewer asked go to the supplement with one pointer sentence;
   the letter cites their location.
2. **Right place for each kind of statement.** Theory sections state what is true and under
   which conditions; implementation sections say what to do and the defaults; results sections
   carry the numbers. Do not mix them in one remark. Do not refer forward from an
   implementation section to a theorem that has not appeared yet.
3. **Cite, don't reinvent.** Before writing a lemma or derivation, check whether it exists in
   the literature. Label each result as borrowed (cite it), adapted (cite and say what
   changed), or new. Claiming a borrowed result as new is the fastest way to lose a reviewer.
4. **No revision narrative.** Never write sentences that only make sense against the old
   version ("unlike the previous argument", "we no longer require", "the proof does not use X").
   Readers never saw the old version. That explanation belongs in the letter.
5. **Omission is allowed; fabrication is not.** A result that does not favour the method may be
   left out. But flag it when leaving it out would make a sentence in the paper false or
   misleading, when a reviewer asked about it directly, or when the released code would expose
   it — then propose the minimal wording that keeps every claim true.
6. **Every formula stays.** When condensing, cut words, not mathematics. Moving a display
   inline unchanged is fine; replacing it with prose is not.
7. **Protected text and references.** Text written by an advisor or coauthor (listed in
   `rules.md`) changes only to fix a genuine error, at word level, shown against the original.
   Separate "wrong" from "could be stated better": act on the first, list the second for the
   user. References in the protected list are never proposed for removal.
8. **Format from the source.** For format questions (statements, their order, section names,
   footnotes, bibliography style), follow the journal's own template first, then its official
   instructions page, and quote the line. Never add a section the template does not have.

## Style

9. **Plain statistics-paper prose.** Declarative sentences in the voice of the surrounding text.
   Write in the order a reader needs: for a simulation, the data-generating model, then
   settings, then methods compared, then replications.
10. **No AI flavour.** None of these:
    - run-in italic labels (*Settings.* *Competing tests.*);
    - sentences that explain or defend the writing ("This choice ensures a fair comparison");
    - parallel category lists ("global (…), local (…), and discontinuous (…)");
    - stock phrases: "it is worth noting", "plays a crucial role", "physically motivated",
      "in order to", "a wide range of", "novel", "remarkable", "significantly" (unless it means
      statistical significance);
    - proofs padded with framing sentences.
11. **Remarks short, main point first.** Two or three sentences.
12. **Numbers.** Conclusion first, then the numbers. Same number of decimals for the same
    quantity throughout. Every number traceable to a result file (`number_audit.py`).
13. **Figures and tables.** Captions say what is shown and how to read it; no colour names in
    text or captions if the journal prints in grey (refer to line styles or labels instead).

## Before showing any proposed text

Reread it once for rules 4, 5, 10 and 11, and check that every number and citation in it has
a source in the proposal's basis section.
