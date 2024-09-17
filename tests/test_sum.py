import unittest
from mean_calcul import somme_revenus_par_groupes

class TestCalculations(unittest.TestCase):
    def test_somme_revenus(self):
        # Exemple de test
        data = ...
        result = somme_revenus_par_groupes(data, "Titre_annonce", "mois_annee", "Revenus")
        self.assertEqual(expected_result, result)

if __name__ == '__main__':
    unittest.main()
