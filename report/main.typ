#import "template.typ": ieee

#show: ieee.with(
  title: [Comparing Supervised Learned Approaches for Branch & Bound Strong Branching Approximation ],
  n-columns: 1,
  authors: (
    (
      name: "Elena Ferro",
      department: [ID 2166466],
      organization: [University of Padua],
      location: [Machine Learning],
      email: [`elena.ferro.7@studenti.unipd.it`]
    ),
  ),
  bibliography: bibliography("refs.bib"),
  figure-supplement: [Fig.],
  paper-size: "a4",
  code-font-family: "Liberation Mono",
  body-font-size: 11pt
)

// Additional custom styles
#show link: underline
#set table(inset: (y: 8pt))

#include "sections/introduction.typ"
#include "sections/theoretical-bg.typ"
#include "sections/dataset.typ"
// #include "sections/experiments.typ"
// #include "sections/results.typ"
// #include "sections/conclusion.typ"