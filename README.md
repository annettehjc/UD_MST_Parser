# UD MST Parser
A minimun spanning tree parser for [universal dependency](https://universaldependencies.org/u/dep/) syntactic trees. 
  
**Authors:** Hyunjoo Cho ([@annettehjc](https://github.com/annettehjc)), Erik Zeiner ([@ErikZeiner](https://github.com/ErikZeiner)).

## Example
```
digraph {
	<ROOT> -> give [label="root(8508889.00)"]
	give -> also [label="advmod(58080.00)"]
	give -> me [label="nsubj(2755536.00)"]
	give -> list [label="obj(9306570.00)"]
	give -> flights [label="obj(9306570.00)"]
	list -> a [label="det(13171938.00)"]
	list -> oakland [label="nmod(36635560.00)"]
	list -> boston [label="nmod(36635560.00)"]
	oakland -> of [label="case(80109000.00)"]
	oakland -> between [label="case(80109000.00)"]
	oakland -> and [label="cc(257127.00)"]
}
```
Parser will parse the given sentences with the MST algorithm in to a universal dependency tree. Each arc will be given with a corresponding weight.
```
Macro averaged UAS: 0.47616909423608644
Macro averaged LAS: 0.37184156712786176
```
At the end, the scorer will calculates unlabeled attachment score (UAS) and labeled attachment score (LAS) using the golden output and the predicted output, and report the average UAS and LAS per sentence as a macro average
