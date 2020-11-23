""" 
This module prepares reference tables for other modules 
 
  Inputs:
  --------------------------------------------------------------
   1. Genecode gtf file 
  --------------------------------------------------------------
  
   Output Tables:
  -------------------------------------------------------------
   1. ensg -> gene 
   2. pb_acc -> gene
   3. isoname (transcript name) -> gene 
   4. ensp -> gene 
   5. isoform, gene, length table 
   6. gene -> min, max, average
 -------------------------------------------------------------- 

"""

# Import Modules 
import pandas as pd 
import argparse
import csv
from collections import defaultdict

# Define Functions
def GenMap(gtf_file):
    """
    This function prepares a series of tables that map gene, transcript and protein level information. 
    """

    # Initialize Lists and Dictionaries
    genes = {} # ENSG -> <genename>
    isos = {} # ENST -> <iso-name>
    ensps = defaultdict(set) # gene_name -> <set(ENSPs)>
    isonames = defaultdict(set) # transcript name -> gene_name

    # Parse GTF file
    for line in open(gtf_file):
        if line.startswith('#'):
            pass
        else:
            wds = line.split('\t')
            cat = wds[2]
            if cat in ['transcript']:
                ensg = line.split('gene_id "')[1].split('"')[0].replace('-', '_')
                gene = line.split('gene_name "')[1].split('"')[0].replace('-', '_')
                enst = line.split('transcript_id "')[1].split('"')[0].replace('-', '_')
                transcript_name = line.split('transcript_name "')[1].split('"')[0].replace('-', '_')
                genes[ensg] = gene
                isos[enst] = transcript_name
                isonames[gene].add(transcript_name)
                if 'transcript_type "protein_coding' in line:
                        gen = line.split('gene_name "')[1].split('"')[0].replace('-', '_')
                        ensp = line.split('protein_id "')[1].split('"')[0].replace('-', '_')
                        ensps[gen].add(ensp)
    
    # Save Tables in results/PG_ReferenceTables 
    with open('../../results/PG_ReferenceTables/ensg_to_gene.tsv', 'w') as ofile:
        for ensg, gene in genes.items():
            ofile.write(ensg + '\t' + gene + '\n')
    
    with open('../../results/PG_ReferenceTables/enst_to_isoname.tsv', 'w') as ofile:
        for enst, isoname in isos.items():
            ofile.write(enst + '\t' + isoname + '\n')
    
    with open('../../results/PG_ReferenceTables/ensp_to_gene.tsv', 'w') as ofile:
        for gen, ensp_set in ensps.items():
            for ensp in ensp_set:
                ofile.write(gen + '\t' + ensp + '\n')
    
    
    with open('isoname_to_gene.tsv', 'w') as ofile:
        for gene, transcript_set in isonames.items():
            for transcript in transcript_set:
                ofile.write(gene + '\t' + transcript + '\n')
    
    print("The ensg_to_gene, enst_to_isoname, ensp_to_gene and isoname_to_gene files have been prepared")

def IsoLenTab(fa_file):
    """
    Prepare a table that provides gene and length information for each isoform
    """

    # Initialize Lists
    isos = []
    genes = []
    lens = []

    # Parse fafsa file to append isoform, gene and length information 
    for line in open(fa_file):
        if line.startswith('>'):
            isos.append(line.split('|')[4].split('""')[0])
            genes.append(line.split('|')[5].split('""')[0])
            lens.append(line.split('|')[6].split('""')[0])

    # Export Data as a DataFrame and a tsv file
    data = {'isoform': isos, 'gene': genes, 'length': lens}
    df = pd.DataFrame(data)
    df.to_csv('../../results/PG_ReferenceTables/isoform_len.tsv', sep='\t', index=False)
    print("The isoform length table has been prepared.")
    return df

def GeneLenTab(IsolenFile):
    """ 
    Prepare a table that provides the min, max and average length of a gene 
    """

    cut = IsolenFile[['gene', 'length']]

    # Map genes to lengths and calc average, min and max. Round mean to nearest tenth. Reset indices. 
    len= cut.groupby(['gene']).length.agg(['mean', 'min', 'max'])
    len['mean'] = len['mean'].round(decimals = 1)
    len = len.reset_index(level=['gene'])

    # Change column names and save the table 
    len.columns =['gene', 'avg_len', 'min_len', 'max_len']
    len.to_csv('../../results/PG_ReferenceTables/gene_len_stats.tsv', sep="\t", index=False)
    print('Prepared the gene length statistics table')



def main():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Proccess ORF related file locations')
    parser.add_argument('--gtf_file','-g',action='store', dest= 'gtf_file',help='Gencode GTF input file location')
    parser.add_argument('--fa_file','-fa',action='store', dest= 'fa_file',help='Gencode Fafsa input file location')
    results = parser.parse_args()

    # Make ensg -> gene, enst -> isoname, ensp -> gene and isoname -> gene mapping files 
    GenMap(results.gtf_file)

    # Prepare Gene Isoform Length table 
    df = IsoLenTab(results.fa_file)

    # Prepare Gene Length Table 
    GeneLenTab(df)

if __name__ == "__main__":
    main()



