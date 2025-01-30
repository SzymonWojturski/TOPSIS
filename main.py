import numpy as np
import json

def normalize_matrix(matrix):
    norm_matrix = matrix / np.sqrt(np.sum(matrix ** 2, axis=0))
    return norm_matrix

def calculate_weighted_matrix(norm_matrix, weights):
    weighted_matrix = norm_matrix * weights
    return weighted_matrix

def calculate_ideal_solutions(weighted_matrix, benefit_criteria):
    ideal = []
    anti_ideal = []
    for j in range(weighted_matrix.shape[1]):
        if benefit_criteria[j]:
            ideal.append(np.max(weighted_matrix[:, j]))
            anti_ideal.append(np.min(weighted_matrix[:, j]))
        else:
            ideal.append(np.min(weighted_matrix[:, j]))
            anti_ideal.append(np.max(weighted_matrix[:, j]))
    return np.array(ideal), np.array(anti_ideal)

def calculate_distances(weighted_matrix, ideal, anti_ideal):
    distance_to_ideal = np.sqrt(np.sum((weighted_matrix - ideal) ** 2, axis=1))
    distance_to_anti_ideal = np.sqrt(np.sum((weighted_matrix - anti_ideal) ** 2, axis=1))
    return distance_to_ideal, distance_to_anti_ideal

def calculate_closeness_coefficient(distance_to_ideal, distance_to_anti_ideal):
    closeness = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)
    return closeness

def topsis_from_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    alternatives = data["alternatives"]
    decision_matrices = [np.array(matrix) for matrix in data["decision_matrices"]]
    weights_list = [np.array(weights) for weights in data["weights"]]
    benefit_criteria = data["benefit_criteria"]

    average_weights = np.mean(weights_list, axis=0)
    average_decision_matrix = np.mean(decision_matrices, axis=0)

    normalized_matrix = normalize_matrix(average_decision_matrix)
    weighted_matrix = calculate_weighted_matrix(normalized_matrix, average_weights)
    ideal_solution, anti_ideal_solution = calculate_ideal_solutions(weighted_matrix, benefit_criteria)
    dist_to_ideal, dist_to_anti_ideal = calculate_distances(weighted_matrix, ideal_solution, anti_ideal_solution)
    closeness_coefficients = calculate_closeness_coefficient(dist_to_ideal, dist_to_anti_ideal)

    ranked_alternatives = sorted(zip(alternatives, closeness_coefficients), key=lambda x: x[1], reverse=True)

    print("Rankingi alternatyw (od najlepszej do najgorszej):")
    for alt, score in ranked_alternatives:
        print(f"{alt}: {score:.4f}")

def get_input():
    alternatives = input("Podaj nazwy alternatyw oddzielone przecinkami (np. A,B,C): ").split(",")

    num_experts = int(input("Podaj liczbę ekspertów: "))

    num_criteria = int(input("Podaj liczbę kryteriów: "))

    criteria_names = []
    print("Podaj nazwy kryteriów (po jednym na linię):")
    for i in range(num_criteria):
        criteria_name = input(f"Kryterium {i + 1}: ")
        criteria_names.append(criteria_name)

    decision_matrices = []
    for i in range(num_experts):
        print(f"Wprowadź oceny dla eksperta {i + 1}:")
        matrix = []
        for alt in alternatives:
            print(f"Alternatywa {alt}:")
            row = []
            for crit in criteria_names:
                value = float(input(f"Podaj wartość dla kryterium '{crit}' (ekspert {i + 1}): "))
                row.append(value)
            matrix.append(row)
        decision_matrices.append(matrix)

    weights = []
    for i in range(num_experts):
        print(f"Podaj wagi dla eksperta {i + 1} (po jednej wadze dla każdego kryterium):")
        weight = []
        for crit in criteria_names:
            w = float(input(f"Podaj wagę dla kryterium '{crit}' (ekspert {i + 1}): "))
            weight.append(w)
        if len(weight) != num_criteria:
            print("Błąd: liczba wag nie pasuje do liczby kryteriów. Spróbuj ponownie.")
            return None
        weights.append(weight)

    benefit_criteria = []
    for crit in criteria_names:
        is_benefit = input(f"Czy kryterium '{crit}' jest kryterium korzyści? (true/false): ").lower()
        benefit_criteria.append(is_benefit == "true")

    topsis_input = {
        "alternatives": alternatives,
        "decision_matrices": decision_matrices,
        "weights": weights,
        "benefit_criteria": benefit_criteria
    }

    return topsis_input

if __name__ == "__main__":
    file_name="topsis_input.json"
    print("Program do zbierania danych dla grupowego TOPSIS.")
    topsis_data = get_input()
    if topsis_data:
        print("Dane zostały poprawnie zebrane. Oto wynikowy JSON:")
        print(json.dumps(topsis_data, indent=4))

        save_to_file = input("Czy zapisać dane do pliku? (tak/nie): ").lower()
        if save_to_file == "tak":
            with open(file_name, "w") as f:
                json.dump(topsis_data, f, indent=4)
            print(f"Dane zapisano do pliku '{file_name}'.")

    topsis_from_json(file_name)