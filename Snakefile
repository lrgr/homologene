import os
homologene_fields ='raw/HomoloGene_Field_Description.txt'
homologene_gz = 'raw/homologene.xml.gz'
homologene_xml = 'raw/homologene.xml'

A_name = config['A']
B_name = config['B']
A_id = config['A-id']
B_id = config['B-id']

out_dir = 'output/{}-{}'.format(A_name, B_name)
AB_xml = os.path.join(out_dir, '{}-{}_homologene.xml'.format(A_name, B_name))
AB_homologs = os.path.join(out_dir, '{}-{}_homologs.tsv'.format(A_name, B_name))
BA_homologs = os.path.join(out_dir, '{}-{}_homologs.tsv'.format(B_name, A_name))

rule all:
    input:
        AB_homologs, BA_homologs

rule AB:
    input:
        AB_xml
    output:
        AB_homologs
    params:
        ids = [config['A-id'], config['B-id']],
        use_refseq = '--use_refseq_id' if config.get('use_refseq', False) else ''
    shell:
        '''
        python extract_homologs.py \
            --input {input} \
            --output {output} \
            -ids {params.ids} {params.use_refseq}
        '''
rule BA:
    input:
        AB_xml
    output:
        BA_homologs
    params:
        ids = [config['B-id'], config['A-id']],
        use_refseq = '--use_refseq_id' if config.get('use_refseq', False) else ''
    shell:
        '''
        python extract_homologs.py \
            --input {input} \
            --output {output} \
            -ids {params.ids} {params.use_refseq}
        '''

rule species_xml:
    input:
        homologene_xml
    output:
        AB_xml
    params:
        ids = [config['A-id'], config['B-id']]
    shell:
        '''
        python simplify_homologene.py \
            --input {input} \
            --output {output} \
            -ids {params.ids}
        '''


rule download:
    input:
        homologene_fields,
        homologene_xml

rule gunzip:
    input:
        homologene_gz
    output:
        homologene_xml
    shell:
        '''
        gunzip {input}
        '''

rule raw_data:
    output:
        homologene_gz
    params:
        url = 'ftp://ftp.ncbi.nih.gov/pub/HomoloGene/build68/homologene.xml.gz',
    shell:
        '''
        wget {params.url} -O {output}
        '''

rule fields:
    output:
        homologene_fields
    params:
        url='ftp://ftp.ncbi.nih.gov/pub/HomoloGene/HomoloGene_Field_Description.txt'
    shell:
        '''
        wget {params.url} -O {output}
        '''