import pickle
import Orange
import json
MAE = 74.402 


def carregar_model(ruta):
    with open(ruta, "rb") as fitxer:
        return pickle.load(fitxer)

def mostrar_variables(model):
    for variable in model.original_domain.attributes:
        print("Variable:", variable.name)

        if variable.is_discrete:
            print("Valid values:", variable.values)
        else:
            print("Type: Numeric")

def predir_preu(model, portatil):

    domini = Orange.data.Domain(model.original_domain.attributes)

    fila = []

    for variable in domini.attributes:
        valor = portatil[variable.name]
        fila.append(valor)

    taula = Orange.data.Table.from_list(domini, [fila])

    prediccio = model(taula)

    return float(prediccio[0])

def predir_preu_fitxer(model, ruta):

    domini = Orange.data.Domain(model.original_domain.attributes)

    taula = Orange.data.Table(ruta)

    prediccions = model(taula)

    for i in range(len(prediccions)):
        print("Laptop", i + 1, ":", round(float(prediccions[i])), "€")

def demanar_portatil(model):

    portatil = {}

    limits = {
        "ram_gb": (2, 128),
        "disc_gb": (64, 8192),
        "polzades": (10, 20),
        "bateria_wh": (20, 150),
        "pes_kg": (0.5, 5)
    }

    for variable in model.original_domain.attributes:

        if variable.is_discrete:

            while True:

                print("Valid options:", variable.values)

                valor = input("Enter " + variable.name + ": ")

                if valor in variable.values:
                    portatil[variable.name] = valor
                    break

                else:
                    print("Invalid option. Please try again.")

        else:

            while True:

                try:
                    valor = float(input("Enter " + variable.name + ": "))

                    if variable.name in limits:

                        minimum, maximum = limits[variable.name]

                        if minimum <= valor <= maximum:
                            portatil[variable.name] = valor
                            break

                        else:
                            print("Enter a value between", minimum, "and", maximum)

                    elif valor > 0:
                        portatil[variable.name] = valor
                        break

                    else:
                        print("Value must be greater than zero.")

                except ValueError:
                    print("Invalid number. Please try again.")

    return portatil

def valorar(preu_botiga, preu_predit, mae):

    if preu_botiga < preu_predit - mae:
        return "ganga"

    elif preu_botiga > preu_predit + mae:
        return "car"

    else:
        return "preu raonable"

def resum_historial(historial):

    gangues = 0
    cars = 0
    raonables = 0

    millor_oferta = None
    estalvi_maxim = 0

    for consulta in historial:

        if consulta["veredicte"] == "ganga":
            gangues += 1

        elif consulta["veredicte"] == "car":
            cars += 1

        else:
            raonables += 1

        estalvi = consulta["preu_predit"] - consulta["preu_botiga"]

        if estalvi > estalvi_maxim:
            estalvi_maxim = estalvi
            millor_oferta = consulta

    print("\n--- History Summary ---")
    print("Total enquiries:", len(historial))
    print("Bargains:", gangues)
    print("Expensive offers:", cars)
    print("Reasonable prices:", raonables)

    if millor_oferta is not None:
        print("Best offer saving:", round(estalvi_maxim, 2), "€")
        print("Best offer shop price:", millor_oferta["preu_botiga"], "€")
    else:
        print("No offers with savings found.")

if __name__ == "__main__":

    model = carregar_model("model.pkcls")

    # Load previous history
    try:
        with open("consultes.json", "r", encoding="utf-8") as fitxer:
            historial = json.load(fitxer)

            if not isinstance(historial, list):
                historial = []

    except (FileNotFoundError, json.JSONDecodeError):
        historial = []

    # Main program
    while True:

        print("\n--- Laptop Price Advisor ---")

        portatil = demanar_portatil(model)

        # Ask for shop price
        while True:
            try:
                preu_botiga = float(input("Enter shop price (€): "))

                if preu_botiga > 0:
                    break
                else:
                    print("Price must be greater than zero.")

            except ValueError:
                print("Invalid price. Please enter a number.")

        # Predict laptop price
        preu_predit = predir_preu(model, portatil)

        # Evaluate price
        veredicte = valorar(preu_botiga, preu_predit, MAE)

        diferencia = preu_botiga - preu_predit

        # Display results
        print("\n--- Results ---")
        print("Predicted price:", round(preu_predit, 2), "€")
        print("Shop price:", round(preu_botiga, 2), "€")
        print("Difference:", round(diferencia, 2), "€")
        print("Verdict:", veredicte)

        # Save enquiry to history
        consulta = {
            "portatil": portatil,
            "preu_botiga": preu_botiga,
            "preu_predit": preu_predit,
            "veredicte": veredicte
        }

        historial.append(consulta)

        # Ask whether to continue
        resposta = input("\nDo you want to check another laptop? (yes/no): ")

        if resposta.lower() != "yes":
            break

    # Save history to JSON
    with open("consultes.json", "w", encoding="utf-8") as fitxer:
        json.dump(historial, fitxer, indent=4, ensure_ascii=False)

    print("History saved successfully!")
    resum_historial(historial)