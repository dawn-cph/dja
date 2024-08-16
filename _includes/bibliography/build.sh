grep -v "@string" papers.bib | sed "s/.aap/Astronomy\\ \& Astrophysics/g" | sed "s/.apjs/ApJSS/g" | sed "s/.apjl/ApJL/g" | sed "s/.apj/ApJ/g" > papers-repl.bib

pandoc -t markdown_strict --citeproc pandoc-bib.md -o pandoc-bib-output.md --bibliography papers-repl.bib 

cat pandoc-bib-output.md | sed "s/<span class=\"nocase\">/\*\*/g" | sed "s/<\/span>/\*\*/g" > papers.md

rm pandoc-bib-output.md papers-repl.bib