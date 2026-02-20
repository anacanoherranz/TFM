import pickle

filename = 'matrices_boostrap_ventanas.pkl'

with open(filename, 'rb') as f:
    df = pickle.load(f)

print(df.iloc[0,0])

print("el resultado es: ", 3+5)

filename2 = 'resultado.txt'

with open(filename2, 'w') as fout:
    fout.write("el resultado es: " + str(3+5))