"""Performs hierarchical clustering on enriched terms from gene signatures.
"""

import json
from operator import itemgetter
import pandas
import requests
from requests.exceptions import RequestException
import time

from substrate import EnrichrResults, EnrichmentTerm
from gen3va import Config
from gen3va import database
from gen3va.heat_map_factory import filters, utils


def prepare_enriched_terms(Session, signatures, category, library):
    """Prepares enriched terms for hierarchical clustering.
    """
    max_num_rows = filters.MAX_NUM_ROWS / 2
    df_up = _get_raw_data(Session, signatures, library, True)
    df_up = filters.filter_rows_by_highest_abs_val_mean(df_up, max_num_rows)
    df_down = _get_raw_data(Session, signatures, library, False)
    df_down = filters.filter_rows_by_highest_abs_val_mean(df_down,
                                                          max_num_rows)

    columns = []
    for i in range(len(signatures)):
        sig = signatures[i]
        up_vec = df_up.ix[:,i]
        down_vec = df_down.ix[:,i]
        col = utils.build_column(i, sig, up_vec, down_vec, category)
        columns.append(col)
    return columns


def _get_raw_data(Session, signatures, library, use_up):
    """Creates a matrix of genes (rows) and signatures (columns).
    """
    df = pandas.DataFrame(index=[])
    for i, signature in enumerate(signatures):
        print('%s - %s' % (i, signature.extraction_id))

        if use_up:
            genes = signature.up_genes
        else:
            genes = signature.down_genes

        names, scores = get_names_scores(Session, signature, genes, library,
                                         use_up)

        # We eliminate negative combined scores when collecting the data, but
        # visually--and in clustering--we want to think of combined scores as
        # negative if they come from the down list.
        if not use_up:
            scores = [-s for s in scores]

        col_title = utils.column_title(i, signature)
        right = pandas.DataFrame(
            index=[t for t in names],
            columns=[col_title],
            data=[s for s in scores]
        )

        if type(right) is not pandas.DataFrame:
            continue
        df = df.join(right, how='outer')
        if not df.index.is_unique:
            df = df.groupby(df.index).mean()

    df = df.fillna(0)
    return df


def get_names_scores(Session, signature, genes, library, use_up, attempts=0):
    """Wrapper function to getting enrichment results. Calls itself on failure
    at most 3 times.
    """
    if attempts > 3:
        return [], []
    try:
        terms, scores = _enrich_gene_signature(Session, signature, genes,
                                               library, use_up)
    except (RequestException, ValueError) as e:
        attempts += 1
        return get_names_scores(Session, signature, genes, library, use_up,
                                attempts)
    return terms, scores


def _enrich_gene_signature(Session, signature, genes, library, use_up):
    """Gets enrichment vector from Enrichr.
    """
    # Use the existing pertubrations and scores if we've already computed them.
    enrichr_result = signature.get_enrichr_results(use_up, library)
    if enrichr_result:
        print('Already have Enrichr results.')
        ranks = []
        names = []
        scores = []
        for t in enrichr_result.enrichment_terms:
            ranks.append(t.rank)
            names.append(t.name)
            scores.append(t.combined_score)
        names, scores = utils.sort_scores_rank(ranks, names, scores)
        return names, scores

    genes = utils.sort_and_truncate_ranked_genes(genes)
    user_list_id = _post_to_enrichr(genes)
    if not user_list_id:
        raise ValueError('No Enrichr user_list_id')

    enrichr_result = EnrichrResults(user_list_id, use_up, library)
    signature.enrichr_results.append(enrichr_result)
    Session.merge(signature)

    # Wait for Enrichr to add the new user list.
    time.sleep(1)

    url = 'http://amp.pharm.mssm.edu/Enrichr/enrich?' \
          'userListId=%s&backgroundType=%s' % (user_list_id, library)
    resp = requests.get(url)
    if not resp.ok:
        raise Exception('Error fetching enrichment results.')

    results = json.loads(resp.text)[library]
    enrichment_terms = []
    names = []
    scores = []

    for r in results:
        rank = r[0]
        name = r[1]
        p_value = r[2]
        combined_score = r[4]
        if p_value > 0.05:
            continue
        if combined_score < 0:
            continue
        names.append(name)
        scores.append(combined_score)
        term = EnrichmentTerm(rank, name, combined_score)
        enrichment_terms.append(term)

    enrichr_result.enrichment_terms = enrichment_terms
    Session.merge(enrichr_result)

    # We save the scores for reuse, but we return two arrays rather than
    # the EnrichmentTerm instances.
    #
    # Also, Enrichr's API returns the results sorted by rank, so we do not
    # need to sort these.
    Session.commit()
    return names, scores


def _post_to_enrichr(ranked_genes):
    """Returns userListId after adding gene list to Enrichr.
    """
    gene_list_str = '\n'.join([rg.gene.name for rg in ranked_genes])
    payload = {
        'list': gene_list_str,
        'description': ''
    }
    resp = requests.post('%s/addList' % Config.ENRICHR_URL, files=payload)
    if resp.ok:
        return json.loads(resp.text)['userListId']
    return None
