#!/usr/bin/env python
# encoding: utf-8
"""
load_hpo.py


Created by Måns Magnusson on 2016-10-25.
Copyright (c) 2016 __MoonsoInc__. All rights reserved.
"""

import logging

import click

from scout.load import load_hpo

from scout.utils.handle import get_file_handle

from scout.resources import (hpoterms_path, hpodisease_path)

from scout.models.phenotype_term import (HpoTerm, DiseaseTerm)

logger = logging.getLogger(__name__)

@click.command('hpo', short_help='Load hpo terms')
@click.option('--hpo-terms',
                type=click.Path(exists=True),
                help="Path to hpo file",
                default=hpoterms_path
)
@click.option('--hpo-disease',
                type=click.Path(exists=True),
                help="Path to file with hpo diseases",
                default=hpodisease_path
)
@click.pass_context
def hpo(ctx, hpo_terms, hpo_disease):
    """
    Load the hpo terms to the mongo database.
    """
    adapter = ctx.obj['adapter']
    
    logger.info("Dropping HpoTerms")
    HpoTerm.drop_collection()
    logger.debug("HpoTerms dropped")

    logger.info("Dropping DiseaseTerms")
    DiseaseTerm.drop_collection()
    logger.debug("DiseaseTerms dropped")
    
    logger.info("Loading hpo terms from file {0}".format(hpo_terms))
    logger.info("Loading hpo disease terms from file {0}".format(hpo_disease))
    
    hpo_terms_handle = get_file_handle(hpo_terms)
    hpo_disease_handle = get_file_handle(hpo_disease)
    
    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle, 
        disease_lines=hpo_disease_handle, 
    )
    
    logger.info("Successfully loaded all hpo terms")