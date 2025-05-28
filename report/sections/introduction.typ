#import "../glossary.typ": defs
#import "@preview/glossy:0.8.0": init-glossary
#import "@preview/cetz:0.3.4": canvas, draw, tree


#show : init-glossary.with(defs)

= Introduction
The goal of Operational Research is to obtain the optimal solution to a problem by determining the minimum or maximum of a real-valued function (known as _objective function_), while ensuring that certain constraints are satisfied. This can be achieved by adjusting the value of unknown quantities termed _decision variables_.

The project described herein exclusively focuses on problems with linear objective functions and constraints; these fall into three main categories based on the nature of their decision variables:
- @LP problems: all variables can take real values;
- @ILP problems: all variables are integer or binary;
- @MILP problems: some (not necessarily all) variables can take real values.

@ILP and @MILP problems are inherently harder to solve than @LP problems because their set of feasible solutions (the so-called _feasible region_) is non-convex 
#footnote[When integrality constraints are introduced, the feasible region of the problem becomes a non-convex set of isolated points, hence it's not possible to move smoothly from one feasible integer solution to another, as would instead be possible for continuous regions. For this reason, algorithms such as the Simplex method cannot be applied.]\;
the @BnB algorithm is a commonly employed in these cases.
The idea of this method is to temporarily ignore the integrality constraints on the variables and solve the @LP relaxation of the problem #footnote[The LP relaxation is a modified version of a problem where the integrality constraints on some or all variables are removed, allowing them to take on continuous (fractional) values.]\; this is useful as it provides an optimistical bound for the solution original @ILP problem. The @LP relaxation might yield a fractional value for one of the originally-integer variables; if this happens, one of the fractional variables $x$ is chosen as a _branching variable_. Two subproblems are created by adding a new constraint which forces the variable to be $x <= floor(x)$ and $x >= ceil(x)$ in the left and right subtrees respectively: since $x$ should have an integer value, it must certainly hold that its value in the solution of the @ILP problem is either less than or equal to its floor or greater than its ceiling. This procedure is then repeated recursively.

#ref(<cap:branch-n-bound>) shows an example of a simple @BnB tree: at the root node $A$ variables $x_1$ and $x_2$ have fractional values; $x_1$ is chosen as a branching variable and the constraints $x_1 <= 0$ and $x_1 >= 1$ are added. Equivalently, this is done at node $B$ for variable $x_2$.

#let data = (
  [A], // Root node
  (
    [B], // Left subtree root
    [],
    ([]), // Left subtree leaves (x3 ≤ 2, x3 ≥ 3)
  ),
  (
    [], // Right subtree root  
  )
)

#figure(
  canvas({
  import draw: *
  set-style(content: (padding: .2),
    fill: gray.lighten(30%),
    stroke: black)
  
  tree.tree(data, spread: 3.5, grow: 2.25, draw-node: (node, ..) => {
    circle((), radius: .45, stroke: black, fill: gray.lighten(50%))
    content((), node.content)
  }, draw-edge: (from, to, ..) => {
    line(from, to, stroke: black)
  }, name: "tree")
  
  content((rel: (-2.1, -0.8), to: "tree.0"), [$x_1 <= 0$])
  content((rel: (2.1, -0.8), to: "tree.0"), [$x_1 >= 1$])
  content((rel: (-1.8, -1.1), to: "tree.0-0"), [$x_2 <= 2$])
  content((rel: (1.8, -1.1), to: "tree.0-0"), [$x_2 >= 3$])

  content("tree.0", anchor: "north", padding: (-1.4, 0), [$x_1 = 0.75\ x_2 = 2.33$])
  content("tree.0-0", anchor: "east", padding: (0, -2.25), [$x_2 = 2.33$])
  }),
  caption: [An example of a simple @BnB tree.]
) <cap:branch-n-bound>

The selection of the fractional variable is termed _branching_ and can be executed according to several strategies. Ideally, these should result in trees with a limited number of nodes and a reduced execution time. Nevertheless, in practice this is a trade-off: @SB, for instance, is arguably the most powerful strategy when it comes to reducing the size, however it is prohibitively expensive to perform, at the point of being unusable in practice for fairly large problems. Conversely, @PCB tries to approximates the accuracy of @SB reducing its computational burden, but yielding bigger trees.

The goal of this project is to reproduce and extend the experiment realized by Alvarez et al. @alvarez2017bnb, who managed to use machine learning to approximate @SB decisions. The proposed approach is structured in three steps:
+ solve a set of @MILP problems using the @SB strategy and extract a series of features at each node of the @BnB tree, together with the metric determining the corresponding branching decisions;
+ leverage the extracted dataset to train several regressor models, whose goal is to imitate the @SB decisions;
+ employ the trained regressors in the resolution of benchmark problems and compare their performance to both the original @SB and other branching strategies.

// == Problem statement and motivation
// == Theoretical background
// This section aims to provide the reader with a brief overview of theoretical concepts needed to understand results presented in this report, both from an optimization theory and a machine learning perspective.

// === Optimization problems
// Throughout this report, @MILP optimization problems of the following (standard) form are considered:
// $
//  min quad & c^T x\
//  s.t. quad & A x <= b \
//  &x_i in {0, 1} space forall i in I
// $

// where $c in RR^n$ (the cost vector), $A in RR^(m times n)$ (the coefficient matrix), $b in RR^m$ (the right-hand side vector) and $x in {0, 1}^n$ (decision variables vector). $I$ is the set of indices of binary decision variables.
// Theoretically speaking, any of the considerations made in this experiment can be extended to the general @MILP case, by introducing suitable constraints for continuous variables #footnote[$x_j in RR _+ forall j in C$, with $C$ being the set of continuous variables indices]. However, to shorten dataset generation times only binary problems have been considered.

// === Branch and Bound
// @BnB is one of the most widely used algorithms to solve @MILP problems.

// ==== @SB:both

// === Decision trees

// === @ERT:both

// === @PCA:both

// === Rule-based classifiers


// The goal of this project is to reproduce and extend the experiment realized by Alvarez et al. @alvarez2017bnb, who extracted a series of features at each node of the @BnB tree, and the corresponding @SB scores, during the resolution of a set of problems.