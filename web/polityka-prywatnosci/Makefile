TEX_COMPILER = pdflatex
TEX_FLAGS = -interaction=nonstopmode -synctex=1
TEX_FILE = polityka_prywatnosci.tex

all: build

clean:
	rm -f *.aux *.log *.toc *.out *.synctex.gz *.pdf

install:
	cp *.pdf ../

build:
	${TEX_COMPILER} ${TEX_FLAGS} $(TEX_FILE)
