import pandas as pd
import numpy as np
import time
import random

end_value = 10000


start_time = time.time()
dictionary_list = []
for i in range(0, end_value, 1):
    dictionary_data = {k: random.random() for k in range(30)}
    dictionary_list.append(dictionary_data)

df_final = pd.DataFrame.from_dict(dictionary_list)

end_time = time.time()
print('Execution time = %.6f seconds' % (end_time-start_time))

start_time = time.time()
appended_data = []
for i in range(0, end_value, 1):
    data = pd.DataFrame(np.random.randint(0, 100, size=(1, 30)), columns=list('A'*30))
    appended_data.append(data)

appended_data = pd.concat(appended_data, axis=0)

end_time = time.time()
print('Execution time = %.6f seconds' % (end_time-start_time))

start_time = time.time()
df_final = pd.DataFrame()
for i in range(0, end_value, 1):
    df = pd.DataFrame(np.random.randint(0, 100, size=(1, 30)), columns=list('A'*30))
    df_final = df_final.append(df)

end_time = time.time()
print('Execution time = %.6f seconds' % (end_time-start_time))

start_time = time.time()
df = pd.DataFrame(columns=list('A'*30))
for i in range(0, end_value, 1):
    df.loc[i] = list(np.random.randint(0, 100, size=30))


end_time = time.time()
print('Execution time = %.6f seconds' % (end_time-start_time))
