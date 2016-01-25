import unittest
import pandas

from substrate import Gene, RankedGene
from gen3va.hierclust.utils import sort_and_truncate_ranked_genes


class TestFilterRows(unittest.TestCase):

    def test_combined_list(self):
        input_genes = [
            RankedGene(Gene('A'), 9),
            RankedGene(Gene('B'), 10),
            RankedGene(Gene('C'), 7.66),
            RankedGene(Gene('D'), -17),
            RankedGene(Gene('E'), -20),
            RankedGene(Gene('F'), -15)
        ]
        output_genes = sort_and_truncate_ranked_genes(input_genes, 3)
        self.assertTrue(output_genes[0].gene.name == 'E')
        self.assertTrue(output_genes[1].gene.name == 'D')
        self.assertTrue(output_genes[2].gene.name == 'F')

    def test_up_list(self):
        input_genes = [
            RankedGene(Gene('A'), 1),
            RankedGene(Gene('B'), 31),
            RankedGene(Gene('C'), 5),
            RankedGene(Gene('D'), 18),
            RankedGene(Gene('E'), 23),
            RankedGene(Gene('F'), 17)
        ]
        output_genes = sort_and_truncate_ranked_genes(input_genes, 3)
        self.assertTrue(output_genes[0].gene.name == 'B')
        self.assertTrue(output_genes[1].gene.name == 'E')
        self.assertTrue(output_genes[2].gene.name == 'D')

    def test_down_list(self):
        input_genes = [
            RankedGene(Gene('A'), -9),
            RankedGene(Gene('B'), -1),
            RankedGene(Gene('C'), -7),
            RankedGene(Gene('D'), -17),
            RankedGene(Gene('E'), -2),
            RankedGene(Gene('F'), -15)
        ]
        output_genes = sort_and_truncate_ranked_genes(input_genes, 3)
        self.assertTrue(output_genes[0].gene.name == 'D')
        self.assertTrue(output_genes[1].gene.name == 'F')
        self.assertTrue(output_genes[2].gene.name == 'A')

    def test_cutoff_length(self):
        input_genes = [
            RankedGene(Gene('A'), -9),
            RankedGene(Gene('B'), -1),
            RankedGene(Gene('C'), -7),
            RankedGene(Gene('D'), -17),
            RankedGene(Gene('E'), -2),
            RankedGene(Gene('F'), -15)
        ]
        cutoff_length = 4
        output_genes = sort_and_truncate_ranked_genes(input_genes, cutoff_length)
        self.assertTrue(len(output_genes) == cutoff_length)
