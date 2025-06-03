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

@ILP and @MILP problems are inherently harder to solve than @LP problems because their set of feasible solutions (the so-called _feasible region_) is non-convex;
the @BnB algorithm is a commonly employed in these cases @land1960automatic
#footnote[When integrality constraints are introduced, the feasible region of the problem becomes a non-convex set of isolated points, hence it's not possible to move smoothly from one feasible integer solution to another, as would instead be possible for continuous regions. For this reason, algorithms such as the Simplex method cannot be applied.]\.
The idea of this method is to temporarily ignore the integrality constraints on the variables and solve the @LP relaxation of the problem #footnote[The LP relaxation is a modified version of a problem where the integrality constraints on some or all variables are removed, allowing them to take continuous (fractional) values.]\; this is convenient as the relaxation is solvable efficiently using, for instance, the Simplex method. The @LP relaxation solution provides an optimistical bound for the original @ILP problem; the result might assign a fractional value to one of the originally-integer variables; if this happens, one of them, let it be $x$, is chosen as a _branching variable_. Two subproblems are created by adding a new constraint which forces $x <= floor(x)$ and $x >= ceil(x)$ in the left and right subtrees respectively: since $x$ should have an integer value, it must certainly hold that its value in the solution of the @ILP problem is either less than or equal to its floor or greater than its ceiling. This procedure is then repeated at each node until a solution is found (not necessarily an optimal one) or the entire search tree has been explored.

// #ref(<cap:branch-n-bound>) shows an example of a simple @BnB tree: at the root node $A$ variables $x_1$ and $x_2$ have fractional values; $x_1$ is chosen as a branching variable and the constraints $x_1 <= 0$ and $x_1 >= 1$ are added. Equivalently, this is done at node $B$ for variable $x_2$.

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

// #figure(
//   pad(
//     y: 15pt,
//     canvas({
//   import draw: *
//   set-style(content: (padding: .2),
//     fill: gray.lighten(30%),
//     stroke: black)
  
//   tree.tree(data, spread: 5, grow: 1.5, draw-node: (node, ..) => {
//     circle((), radius: .45, stroke: black, fill: gray.lighten(50%))
//     content((), node.content)
//   }, draw-edge: (from, to, ..) => {
//     line(from, to, stroke: black)
//   }, name: "tree")
  
//   content((rel: (-1.9, -0.2), to: "tree.0"), [$x_1 <= 0$])
//   content((rel: (1.9, -0.2), to: "tree.0"), [$x_1 >= 1$])
//   content((rel: (-1.9, -0.5), to: "tree.0-0"), [$x_2 <= 2$])
//   content((rel: (1.9, -0.5), to: "tree.0-0"), [$x_2 >= 3$])

//   content("tree.0", anchor: "north", padding: (-1.4, 0), [$x_1 = 0.75\ x_2 = 2.33$])
//   content("tree.0-0", anchor: "north", padding: (-0.9, 0), [$x_2 = 2.33$])
//   })),
//   caption: [An example of a simple @BnB tree.]
// ) <cap:branch-n-bound>


@BnB is guaranteed to find the optimal solution, however the convergence might be slow for large problems. One the factors that influences its performance is the choice of the variable to branch on;
this process is termed _branching_ and can be executed according to several strategies. 
Ideally, these should produce trees with a limited number of nodes in a reduced execution time. Nevertheless, in practice this is a trade-off. @SB for instance, is arguably the most powerful strategy when it comes to reducing the size, however it is prohibitively expensive to perform, at the point of being unusable in practice for fairly large problems. Conversely, @PCB tries to approximates the accuracy of @SB reducing its computational burden, but it yields bigger trees @bestuzheva2021SCIP.

The goal of this project is to reproduce the experiment realized by Alvarez et al. @alvarez2017bnb, who managed to adopt machine learning to approximate @SB decisions. The proposed approach is structured in three phases:
+ solve a set of @MILP problems using the @SB strategy and extract a series of features at each node of the @BnB tree, together with the metric which determined the corresponding branching decision;
+ use the extracted dataset to train a regressor, whose goal is to mimic @SB decisions. The idea is that the trained model should be able to approximate branching decisions accurately enough, but without the computational overhead;
+ employ the trained regressor in the resolution of benchmark problems and compare its performance to @SB and other branching strategies.

Furthermore, in addition to the reproduction of the original paper experiment, the performance of several supervised learning approaches will be compared on a set of benchmark problems.

// == Document structure
// Below is a brief description of the content of each section of this report.

// @sec:theoretical-bg briefly introduces theoretical concepts from optimization theory and machine learning, in order to contextualize the presented experiments and results.

// @sec:dataset-gen describes the dataset generation process, including considered problems, extracted features and actual implementation details.

// @sec:experiments presents the performed experiments, including details on the training process.

// #text("TODO", red, size: 16pt)
