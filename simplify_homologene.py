import argparse
import xml.etree.ElementTree as ET

'''
simplify_homologene.py extracts XML elements of the Homologene build 
corresponding only to the provided species Taxa IDs.

Note: The following elements are removed from the XML:
- From HG-Entry
    - HG-Entry_commentaries
    - HG-Entry_cr-date
    - HG-Entry_up-date
- From HG-Gene:
    - HG-Gene_domains
    - HG-Gene_location
'''

_HEAD = \
'''<?xml version="1.0"?>
<!DOCTYPE HG-EntrySet PUBLIC "-//NCBI//HomoloGene/EN" "HomoloGene.dtd">
<HG-EntrySet>
  <HG-EntrySet_entries>
'''
_TAIL = \
'''
  </HG-EntrySet_entries>
</HG-EntrySet>
'''

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str,)
    parser.add_argument('-ids', '--tax_ids', type=str, nargs='+')
    parser.add_argument('-o', '--output', required=True)
    return parser.parse_args()

def find_and_remove(elem, name):
    es = elem.findall(name)
    if es is not None:
        for e in es:
            elem.remove(e)

def simplify_gene(hg_gene):
    '''
    Remove unecessary elements from HG-Gene
    '''
    for n in ['HG-Gene_domains', 'HG-Gene_location']:
        find_and_remove(hg_gene, n)

def filter_genes_by_species_id(ids, hg_entry):
    '''
    Returns simplified HG-Entry containing relevant genes and gene stats that 
    correspond to species in list of given Tax IDs
    '''

    genes = hg_entry.find('HG-Entry_genes')
    to_remove = []
    to_keep = []
    prot_ids = []
    for gene in genes:
        taxid = gene.find('HG-Gene_taxid').text
        if taxid not in ids:
            to_remove.append(gene)
        else:
            to_keep.append(gene)
            prot_ids.append(gene.find('HG-Gene_prot-gi').text)

    for gene in to_remove:
        genes.remove(gene)
    
    for gene in to_keep:
        simplify_gene(gene)
    
    return prot_ids

def simplify_HG_entry_stats(prot_ids, hg_entry):
    distances = hg_entry.find('HG-Entry_distances')
    to_remove = []
    to_keep = []
    for stat in distances:
        gi1 = stat.find('HG-Stats_gi1').text
        gi2 = stat.find('HG-Stats_gi2').text
        if gi1 in prot_ids and gi2 in prot_ids:
            to_keep.append(stat)
        else:
            to_remove.append(stat)
    for stat in to_remove:
        distances.remove(stat)

def simplify_HG_entry(ids, hg_entry):
    prot_ids = filter_genes_by_species_id(ids, hg_entry)
    for n in ['HG-Entry_cr-date', 'HG-Entry_up-date', 'HG-Entry_commentaries']:
        find_and_remove(hg_entry, n)

    if len(prot_ids) < 2: return None
    # Keep stat entries that only correspond to relevant geness
    simplify_HG_entry_stats(prot_ids, hg_entry)
    return hg_entry



def HG_entry_elements(ids, fp):
    root = None
    n_groups = 0
    for event, elem in ET.iterparse(fp, events=('start', 'end')):
        if root is None:
            root = elem
        if event =='end' and elem.tag == 'HG-Entry':
            hg_entry = simplify_HG_entry(ids, elem)
            if hg_entry is not None:
                yield hg_entry
                root.clear()
                elem.clear()

                n_groups += 1

def main():
    args = parse_args()

    print('* Parsing {}'.format(args.input))
    print('* Extracting relevant XML elements for the following Tax IDs:')
    for id in args.tax_ids:
        print('\t- {}'.format(id))
    
    print('* Writing extracted XML to: {}'.format(args.output))
    fmt_str = ' ' * 4 + '{}\n'

    with open(args.output, 'w') as fp:
        fp.write(_HEAD)
        for hg_entry in HG_entry_elements(args.tax_ids, args.input):
            fp.write(fmt_str.format(ET.tostring(hg_entry, encoding='unicode').strip()))
        fp.write(_TAIL)
if __name__ == "__main__":
    main()