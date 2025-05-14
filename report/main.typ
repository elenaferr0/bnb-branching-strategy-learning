#import "@elenaferr0/ieee:0.0.1": ieee

#show: ieee.with(
  title: [Learning Branch and Bound strong branching scores via supervised learning],
  abstract: [
    Abstract
  ],
  authors: (
    (
      name: "Elena Ferro",
      department: [ID 2166466],
      organization: [University of Padua],
      location: [Machine Learning],
      email: [`elena.ferro.7@studenti.unipd.it`]
    ),
  ),
  // index-terms: ("Scientific writing", "Typesetting", "Document creation", "Syntax"),
  bibliography: bibliography("refs.bib"),
  figure-supplement: [Fig.],
  paper-size: "a4",
  code-font-family: "Liberation Mono"
)

// Show link underlines
#show link: underline
#set par(spacing: 1em)

#include "sections/introduction.typ"
#include "sections/literature-review.typ"
#include "sections/dataset.typ"
#include "sections/experiments.typ"
#include "sections/results.typ"
#include "sections/conclusion.typ"