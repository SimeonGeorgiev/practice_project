
from blast_all import blast_search
from my_classes import PatternFinder, BlastReader

orf_re = '^ATG(?:[ATGC]{3})+?(?:TAA|TAG|TGA)'

find_orfs = PatternFinder( \
filter_with = orf_re,	file = "mine.seq")

find_orfs.set_matches()

find_orfs.filter_out_shorter_orfs() 

find_orfs.file_output(output_file = "ORFs.fasta") 
#this produces a fasta file, the first line gives the location of the ORF in the sequence and it's length - the sequence starts at 30747 (the first reading frame) and is 2424 bases long.
# the second line is the sequence of the ORF


blast_search( input_file = "ORFs.fasta", output_file = "Blast_output.xml", prog = "blastn", s_type = 'nt')
#uses the output of the previous line as an input file for a blast search, the program used is blastn, the sequence type is set to s_type


alignments = BlastReader(input_file = "Blast_output.xml") 
#A blast_reader object is created, with input_file set to the blast output

alignments.analyse()
#Reads the blast output and creates a top_alignments list-> 
#This contains the title (gene name and species) and the score of each alignment, ranked in by sequence cover, sequence identity and alignment score- as usually in the blast outputs produced in the website version. 

alignments.write_output(to = "top_alignments.csv") 
# this file will contain the ranked alignments-  
#the last time when it was ran it produced this output:

#Hit Title;Alignment Score
#[Candida] glabrata uncharacterized protein (CAGL0F05005g), partial mRNA;1044.0
#Candida glabrata strain CBS138 chromosome F complete sequence;1044.0
#Ashbya gossypii FDAG1 chromosome VII, complete sequence;628.0
#Therefore it is most likely that the sequence is taken from Candida glabrata.
