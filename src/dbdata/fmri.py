from subprocess import Popen, PIPE, STDOUT, call
from shutil import move
import os

standard_header= "\\documentclass{article}\n" + \
"\\begin{document}\n"

standard_footer="\\end{document}\n"

def make_document(my_header, my_content, my_footer):
	tex_document = my_header
	tex_document += my_content
	tex_document += my_footer
	return tex_document

def compose_FMRIMeasurementProtocol(Protocol):
	tex_content = "\\begin{itemize}\n"
	return tex_content

def print_document(tex_document, destination=None):
	p = Popen(["pdflatex"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	grep_stdout = p.communicate(input=tex_document)[0]
	if destination:
		move("texput.pdf", destination)
	all_files = os.listdir(".")
	trace_files = [one_file for one_file in all_files if "texput" in one_file and ".pdf" not in one_file]
	for trace_file in trace_files:
		os.remove(trace_file)

if __name__ == '__main__':
	my_content=compose_FMRIMeasurementProtocol()
	tex_document = make_document(standard_header, my_content, standard_footer)
	print_document(tex_document)
