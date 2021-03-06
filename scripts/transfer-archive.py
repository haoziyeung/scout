#!/usr/bin/env python
# encoding: utf-8
"""
update_cases.py

Update cases with information from a old instance

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""
import logging

import click
import yaml
from pymongo import MongoClient

from pprint import pprint as pp

from scout.models import Variant
from scout.models.phenotype_term import PhenotypeTerm


logger = logging.getLogger(__name__)


def update_case(adapter, case_obj, exported_data):
    """docstring for update_case"""
    case_id = case_obj.case_id

    # Update the collaborators
    if exported_data['collaborators']:
        collaborators = set(
            [coll for coll in case_obj.collaborators] + exported_data['collaborators'])
        logger.info("Set collaborators to %s ", ', '.join(collaborators))
        case_obj.collaborators = list(collaborators)

    # Set assignee
    if case_obj.assignee is None:
        if exported_data['assignee']:
            mail = exported_data['assignee']
            user_obj = adapter.user(email=mail)
            if user_obj:
                logger.info("Assigning user %s", mail)
                case_obj.assignee = user_obj
            else:
                logger.info("Could not find user user %s", mail)

    # Add the old suspects
    if exported_data['suspects']:
        existing_suspects = case_obj.suspects
        for suspect in exported_data['suspects']:
            variant_obj = Variant.objects.get(
                variant_id=suspect, case_id=case_id)
            if variant_obj:
                logger.info("Adding suspect %s", variant_obj.display_name)
                existing_suspects.append(variant_obj)
            else:
                logger.info("Could not find suspect %s in database", suspect)
        case_obj.suspects = existing_suspects

    # Add the old suspects
    if exported_data['causatives']:
        existing_causatives = case_obj.causatives
        for causative in exported_data['causatives']:
            variant_obj = Variant.objects.get(
                variant_id=causative, case_id=case_id)
            if variant_obj:
                logger.info("Adding causative %s", variant_obj.display_name)
                existing_causatives.append(variant_obj)
            else:
                logger.info(
                    "Could not find causative %s in database", causative)
        case_obj.causatives = existing_causatives

    # Update the synopsis
    if exported_data['synopsis']:
        if not case_obj.synopsis:
            logger.info("Updating synopsis")
            case_obj.synopsis = exported_data['synopsis']

    # Update the phenotype terms
    # If the case is phenotyped, skip to add the terms
    phenotype_terms = exported_data['phenotype_terms']
    if phenotype_terms:
        logger.info("Updating phenotype terms")
        existing_terms = case_obj.phenotype_terms
        if len(existing_terms) == 0:
            for term in phenotype_terms:
                hpo_obj = adapter.hpo_term(term)
                if hpo_obj:
                    new_term = PhenotypeTerm(
                        phenotype_id=term,
                        feature=hpo_obj.description
                    )
                    logger.info("Adding term %s", term)
                    existing_terms.append(new_term)
                else:
                    logger.info("Could not find term %s", term)
            case_obj.phenotype_terms = existing_terms
        else:
            logger.info("Case was already phenotyped")

    # Update the phenotype groups
    # If the case has a phenotype group, skip to add the groups
    phenotype_groups = exported_data['phenotype_groups']
    if phenotype_groups:
        logger.info("Updating phenotype groups")
        existing_groups = case_obj.phenotype_groups
        if len(existing_groups) == 0:
            for term in phenotype_groups:
                hpo_obj = adapter.hpo_term(term)
                if hpo_obj:
                    new_term = PhenotypeTerm(
                        phenotype_id=term,
                        feature=hpo_obj.description
                    )
                    logger.info("Adding term %s", term)
                    existing_groups.append(new_term)
                else:
                    logger.info("Could not find term %s", term)
            case_obj.phenotype_groups = existing_groups
        else:
            logger.info("Case already had phenotype groups")

    logger.info("Saving case")
    case_obj.save()


@click.command('update_cases', short_help='Update cases')
@click.argument('exported_cases',
                type=click.File('r')
                )
@click.pass_context
def update_cases(context, exported_cases):
    """Update all information that was manually annotated from a old instance

        Takes a yaml file
    """
    logger.info("Running scout update cases")

    exported_data = yaml.load(exported_cases)

    adapter = context.obj['adapter']

    for case_obj in adapter.cases():
        if not case_obj.is_migrated:
            case_id = case_obj.case_id
            if case_id in exported_data:
                logger.info("Updating case: %s" % case_id)
                exported_info = exported_data[case_id]
                update_case(adapter, case_obj, exported_info)
