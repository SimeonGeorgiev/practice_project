from Bio.Blast import NCBIWWW

def do_blast(sequence, output , program = 'blastp', seq_type = 'p'):

	with NCBIWWW.qblast(program, seq_type, sequence) as blast_output:

		with open("{}".format(output), "w") as f:
	
			f.write(blast_output.read())

def blast_search(input_file = None, output_file = None, prog= "blastp", s_type = 'p'):
	assert s_type in ('p', 'nt')
	assert prog in ("blastp", "blastn")
	
	with open(input_file, "r") as f:
		sequences = f.read()

	do_blast(sequence = sequences, output = output_file, program = prog, seq_type = s_type)
