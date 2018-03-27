from Bio import SeqIO
import re
from Bio.Blast import NCBIXML
"""
This file contains the three classes imported in the Part1.py and Part2.py files
"""
#I am using a class to find the open reading frames, and by subclassing it I can reuse code to carry out the analysis in part 2.
#The first class is used to find the open reading frames from a file and create an output.
#It also is used as a superclass for the class used to find the ASCII characters.

class PatternFinder:
	def __init__(self, filter_with, sequence = None, file = None, frames = 3):
		self.set_filtering(filter_with) #sets a value that will be used to analyse the sequence
		self.nframes = frames #sets how many reading frames to use when reading the sequence
		self.set_seq(file) #extracts the sequence from a string- filename or ATGC's in a string
		self.frames = tuple(self.seq[i:] for i in range(self.nframes)) #splits self.seq into reading frames
		assert self.frames[0][4] == self.frames[1][3] == self.frames[2][2]
	def set_filtering(self, fw):
		self.re = re.compile(fw) #compiles the string to a regular expression that will be used to match the ORF pattern

	def set_seq(self,file):
		if file != None:
			self.set_seq_from_file(file) #sets it from file, which is how it's used in the script
		else:
			raise ValueError('Pass a string as a filename when instantiating.')


	def set_seq_from_file(self,file):	
		with open(file, "rU") as my_file:	#opens the file in read unicode mode, using the context manager open() and the keyword with
			self.seq = str(SeqIO.read(my_file, "fasta").seq) #sets self.seq to the sequence in the fasta file
			#with the argument "fasta" the SeqIO.read() funciton knows how to create an object
			#then, the .seq of that object is taken and coerced into a string object

	def set_matches(self):
			self.matches = [] #sets self.matches to an empty list
			for index in range(0,len(self.seq),self.nframes): # the range function produces an integer value on each iteration- assigned to index
				#              this allows the loop to capture every single codon.
				for frame in self.frames: # now the loops goes trough every single frame, with the same value for the temp variable index
					match = self.re.match(frame[index:]) #tries to match the string starting at position== index
					if match != None: #if there is no match match will be == None
						self.matches.append(match.group()) # but if there is a match(Open Reading Frame) it's appended to self.matches
										#match.group() returns a string, so if there is a match this appends the ORF sequence

	def filter_out_shorter_orfs(self):
		longest = max(len(s) for s in self.matches) #get's the length of the longest sequence in a list of sequences
		self.matches = [s for s in self.matches if len(s) == longest] #this is a list with one value, the longest sequence

	def file_output(self, output_file = "ORFs.fasta"): #Writes a FASTA file with the sequences in self.matches
		with open(output_file, 'w') as f: #open a file in write mode
			for i, s in enumerate(self.matches, 1): #enumerate produces a number at each iteration
#													 that number is assigned to i and is equal to the current iteration the loop is in
				print('>Sequence number- {}\tStarts from base- {}\tLength- {}\t:'.\
					format(i, self.seq.find(s) + 1, len(s)), s, file = f, sep = '\n')
				#the format function gives the sequence a number, equal to I, gives the starting position of the sequence by seartching for it in seq.find
				#and also gives the length of the sequence, and writes it to  file, 
				#sep= '\n' means that it separates the sequence and the header with a newline


class BlastReader:

	def __init__(self, input_file, e_val = 0.04, n_top_alignments = 3):
		self.file = input_file	#sets the input file, required argument!
		self.e = e_val #sets the threshod evalue used by the self.analyse() method
		self.n = n_top_alignments #number of alignments from the blast result to present, set to 10000 if you want to see all
	

	def extract_alignment_titles(self):
		for alignment, desc in zip(self.record.alignments, self.record.descriptions): #alignments and descriptors are lists in the Blast.Record.Blast object
			if (self.e > desc.e): #desc.e is the e value of the alignment
				title = ' '.join(alignment.title.split()[1:]) #This is used in the output
				yield (title, desc.score) #the yield statement turns this function into a listlike object- generator
				#the difference being that each element is evaluated only when needed
				#this allows me to reduce the number of alignments to a specified ammount

	def analyse(self): # 'r' is for opening the file in read mode
		with open(self.file, 'r') as result: #opens the file that was set to this object's __init__ method, with an alias- result
			self.record = NCBIXML.read(result) #The NCBIXML.read() function is used-> 
			#self.record is set as a Bio.Blast.Record.Blast object
			#Blast is a useful class that simplifies working with the XML output of biopython's BLAST.
		alignments = self.extract_alignment_titles() #this is the previously defined generator function
		self.top_alignments = tuple([al for al, _ in zip(alignments, #by using the range function in zip, 
													range(self.n))]) #I restrict the size of the list comprehension
	
	def write_output(self, to): #Creates a semicolon separated csv
#with is analogous to writing the try;except;finally blocks, so it's useful syntatic sugar
#w' is for opening the file in write mode, so we can rewrite it's contents
		with open(to, 'w') as f: #opens the file and gives it an alias - f
			print('Hit Title', 'Alignment Score', file = f, sep = ';', end = '\n') #Header of the csv file
			for info in self.top_alignments: 
				print(info[0], info[1], file = f, sep = ';', end = '\n')#writes a line to the csv file
				#each line of the csv file corresponds to one alignment hit, therefore by looking at the top alignments the origin of the sequence can be inferred
